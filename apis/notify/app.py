import os
import traceback
from http import HTTPStatus
from urllib.parse import urlparse

from ai.common.constants import (
    FILE_NOT_FOUND,
    USER_NOT_FOUND,
    S3FileNotFoundError,
    UserFileNotFoundError,
)
from ai.embeddings.create import insert_data_into_vector_db
from ai.llms.constants import NEW_COLLECTION_NAME
from common.app_utils import get_app
from common.chatbot import ChatError, Conversation, User, UserFiles
from common.db import db
from common.envs import logger
from common.lambda_utils import call_fn, get_event_data
from notify.collection_conn import get_collection_uuid_by_name
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


def get_input_data(event):
    request = get_event_data(event)
    u_id = request.get("id")
    file_path = request.get("s3_url")
    file_name = request.get("file_name")
    conversation_id = request.get("conversation_id")
    time_stamp = request.get("time_stamp")
    user_id = request.get("user_id")
    logger.info(
        f"User ID: {u_id}, File Path: {file_path}, File Name: {file_name}, Conversation ID: {conversation_id}, Time Stamp: {time_stamp}, User ID: {user_id}"
    )
    return u_id, file_path, file_name, conversation_id, time_stamp, user_id


def user_and_file_exists(u_id, file_path):
    user = User.query.filter_by(id=u_id).first()
    if not user:
        error_message = f"User with ID {u_id} not found"
        logger.error(error_message)
        log_error_in_db(u_id, USER_NOT_FOUND, error_message, db)
        return {
            "success": False,
            "message": USER_NOT_FOUND,
        }, HTTPStatus.BAD_REQUEST.value

    user_file = UserFiles.query.filter_by(s3_url=file_path).first()
    if not user_file:
        error_message = f"File with path {file_path} not found for user {u_id}"
        logger.error(error_message)
        log_error_in_db(file_path, UserFileNotFoundError, error_message, db)
        return {
            "success": False,
            "message": FILE_NOT_FOUND,
        }, HTTPStatus.BAD_REQUEST.value
    return user_file


def s3_file_exists(file_path, local_file_path):
    s3 = S3Manager()
    if not s3.download_csv(urlparse(file_path).path[1:], local_file_path):
        error_message = S3FileNotFoundError
        logger.error(error_message)
        log_error_in_db(file_path, S3FileNotFoundError, error_message, db)
        return {
            "success": False,
            "message": FILE_NOT_FOUND,
        }, HTTPStatus.BAD_REQUEST.value
    return s3


def handle_notify_request(*args):
    try:
        # with app.app_context():
        event = args[0]
        (
            u_id,
            file_path,
            file_name,
            conversation_id,
            time_stamp,
            user_id,
        ) = get_input_data(event)

        user_file = user_and_file_exists(u_id, file_path)
        file_name = user_file.file_name
        local_file_path = os.path.join(BASE_DIR, file_name)
        s3 = s3_file_exists(file_path, local_file_path)

        try:
            logger.info(
                f"user_id: {user_id}, time_stamp: {time_stamp}, conversation_id: {conversation_id}"
            )
            collection_name, conversation_id = check_collection_name(
                conversation_id, user_id, time_stamp, db
            )
            output = insert_data_into_vector_db(file_path, file_path, collection_name)
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


def check_collection_name(conversation_id, user_id, time_stamp, db):
    if not conversation_id:
        with db.session() as session:
            new_conversation = Conversation()
            new_conversation.time_stamp = time_stamp
            new_conversation.user_id = user_id
            session.add(new_conversation)
            session.commit()

            new_conversation.collection_name = (
                NEW_COLLECTION_NAME + str(user_id) + "_" + str(new_conversation.id)
            )
            session.commit()
            collection_name = new_conversation.collection_name
            conversation_id = new_conversation.id
    else:
        collection_name = (
            NEW_COLLECTION_NAME + str(user_id) + "_" + str(conversation_id)
        )

    return collection_name, conversation_id
