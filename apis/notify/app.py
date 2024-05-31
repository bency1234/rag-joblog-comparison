import os
import traceback
from http import HTTPStatus
from urllib.parse import urlparse

from ai.embeddings.create import insert_data_into_vector_db
from common.app_utils import get_app
from common.chatbot import ChatError, User, UserFiles
from common.db import db
from common.envs import logger
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
    db.session.add(error_log)
    db.session.commit()
    logger.info("Error details added successfully")


def add_file_error_details_in_user_info(user_file, error_details, db):
    logger.error(f"Adding file error details in user file: {error_details}")
    user_file.error_info = f"Error Line: {error_details}"
    db.session.add(user_file)
    db.session.commit()


def handle_notify_request(*args):
    try:
        event = args[0]
        request = get_event_data(event)
        u_id = request.get("id")
        file_path = request.get("s3_url")

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
        file_name_without_time_stamp = file_name.split("_", 1)[-1]
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

        logger.info(f"File Processing Started - {file_name_without_time_stamp}")
        try:
            output = insert_data_into_vector_db(file_path, file_path)
            print("split_docs.....................", output)
            if output:
                user_file.embedded = True
                db.session.add(user_file)
                db.session.commit()
                logger.info("File processed successfully")
            return {"processed": output}, HTTPStatus.OK.value

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
