import os
import traceback
from http import HTTPStatus
from urllib.parse import urlparse

import psycopg2
from ai.embeddings.create import insert_data_into_vector_db
from common.app_utils import get_app
from common.chatbot import ChatError, Conversation, User, UserFiles
from common.db import db
from common.envs import get_secret_value_from_secret_manager, logger
from common.lambda_utils import call_fn, get_event_data
from notify.s3_config import S3Manager

app = get_app(db)
BASE_DIR = os.path.abspath("/tmp")


class FileProcessingErrorException(Exception):
    def __init__(self, message="An error occurred while processing the file."):
        super().__init__(message)


def log_error_in_db(user_input, error_type, error_details, db):
    error_log = ChatError(
        user_input=user_input, error_type=error_type, error_details=error_details
    )
    try:
        with db.session() as session:
            session.add(error_log)
            session.commit()
        logger.info("Error details added successfully")
    except Exception as e:
        logger.error(f"Failed to log error details: {e}")
        raise e


def add_file_error_details_in_user_info(user_file, error_details, db):
    logger.error(f"Adding file error details in user file: {error_details}")
    user_file.error_info = f"Error Line: {error_details}"
    db.session.add(user_file)
    db.session.commit()


def handle_notify_request(*args):
    try:
        with app.app_context():
            event = args[0]
            request = get_event_data(event)
            u_id = request.get("id")
            file_path = request.get("s3_url")
            file_name = request.get("file_name")
            conversation_id = request.get("conversation_id")
            time_stamp = request.get("time_stamp")
            user_id = request.get("user_id")

            user = User.query.filter_by(id=u_id).first()
            if not user:
                error_message = f"User with ID {u_id} not found"
                logger.error(error_message)
                log_error_in_db(u_id, "UserNotFoundError", error_message, db)
                return {
                    "success": False,
                    "message": "User not found",
                }, HTTPStatus.BAD_REQUEST.value

            user_file = UserFiles.query.filter_by(s3_url=file_path).first()
            print("file_path", file_path)
            if not user_file:
                error_message = f"File with path {file_path} not found for user {u_id}"
                logger.error(error_message)
                log_error_in_db(file_path, "UserFileNotFoundError", error_message, db)
                return {
                    "success": False,
                    "message": "File not found",
                }, HTTPStatus.BAD_REQUEST.value

            file_name = user_file.file_name
            local_file_path = os.path.join(BASE_DIR, file_name)

            s3 = S3Manager()
            if not s3.download_csv(urlparse(file_path).path[1:], local_file_path):
                error_message = "File not found on S3"
                logger.error(error_message)
                log_error_in_db(file_path, "S3FileNotFoundError", error_message, db)
                return {
                    "success": False,
                    "message": "File not found",
                }, HTTPStatus.BAD_REQUEST.value

            try:
                logger.info(
                    f"user_id: {user_id}, time_stamp: {time_stamp}, conversation_id: {conversation_id}"
                )
                collection_name, conversation_id = check_collection_name(
                    conversation_id, user_id, time_stamp, db
                )
                output = insert_data_into_vector_db(
                    file_path, file_path, collection_name
                )
                if output:
                    user_file.embedded = True
                    db.session.add(user_file)
                    db.session.commit()
                    logger.info("File processed successfully")
                get_collection_uuid_by_name(collection_name, conversation_id)
                return {
                    "processed": output,
                    "conversation_id": conversation_id,
                }, HTTPStatus.OK.value

            except FileProcessingErrorException as e:
                logger.error(f"File processing error: {e}")
                traceback_info = traceback.format_exc()
                add_file_error_details_in_user_info(user_file, traceback_info, db)
                log_error_in_db(file_path, type(e).__name__, traceback_info, db)
                return {"processed": False}, HTTPStatus.INTERNAL_SERVER_ERROR.value

            finally:
                s3.delete_files_from_local(local_file_path)

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        error_message = str(e)
        error_type = type(e).__name__
        stack_trace = traceback.format_exc()
        error_details = f"errorMessage: {error_message}, stackTrace: {stack_trace}"
        log_error_in_db("NotifyRequest", error_type, error_details, db)
        return {"error": "Something went wrong"}, HTTPStatus.INTERNAL_SERVER_ERROR.value


def lambda_handler(*args):
    logger.info("Notify Lambda invoked")
    event = args[0]
    with app.app_context():
        return call_fn(handle_notify_request, event)


def get_collection_uuid_by_name(collection_name, conversation_id):
    try:
        # Connect to the PostgreSQL database

        conn = psycopg2.connect(
            host=os.environ.get(
                "PGVECTOR_HOST", get_secret_value_from_secret_manager("DATABASE_HOST")
            ),
            user=os.environ.get(
                "PGVECTOR_USER", get_secret_value_from_secret_manager("DATABASE_USER")
            ),
            password=os.environ.get(
                "PGVECTOR_PASSWORD",
                get_secret_value_from_secret_manager("DATABASE_PASS"),
            ),
            database=os.environ.get(
                "PGVECTOR_DATABASE",
                get_secret_value_from_secret_manager("DATABASE_NAME"),
            ),
        )

        cursor = conn.cursor()

        # Execute the query
        query = "SELECT uuid FROM langchain_pg_collection WHERE name = %s"
        cursor.execute(query, (collection_name,))

        # Fetch the result
        result = cursor.fetchone()

        # Close the cursor and connection

        # Return the UUID if found
        if result:
            uuid = result[0]
            logger.info(f"The UUID for name '{collection_name}' is: {uuid}")
            update_query = """
                UPDATE conversation
                SET uuid = %s
                WHERE id = %s
                """
            cursor.execute(update_query, (uuid, conversation_id))

            conn.commit()

            cursor.close()
            conn.close()

            return uuid
        else:
            logger.info(f"No UUID found for name '{collection_name}'")
            return None
    except Exception as e:
        logger.info(f"An error occurred: {e}")


def check_collection_name(conversation_id, user_id, time_stamp, db):
    if not conversation_id:
        with db.session() as session:
            new_conversation = Conversation()
            new_conversation.time_stamp = time_stamp
            new_conversation.user_id = user_id
            session.add(new_conversation)
            session.commit()

            new_conversation.collection_name = (
                "joblog_" + str(user_id) + "_" + str(new_conversation.id)
            )
            db.session.commit()
            collection_name = new_conversation.collection_name
            conversation_id = new_conversation.id
    else:
        collection_name = "joblog_" + str(user_id) + "_" + str(conversation_id)

    return collection_name, conversation_id
