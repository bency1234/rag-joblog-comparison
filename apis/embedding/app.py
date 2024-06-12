import base64
import hashlib
import json
import os
import re
import traceback
from datetime import datetime
from http import HTTPStatus

import boto3
from ai.embeddings.create import insert_data_into_vector_db
from ai.llms.constants import CONTENT_TYPES
from common.app_utils import get_app
from common.chatbot import UserFiles
from common.db import db
from common.envs import get_secret_value_from_secret_manager, logger
from common.lambda_utils import call_fn
from werkzeug.utils import secure_filename

app = get_app(db)
BASE_DIR = os.path.abspath("/tmp")


def calculate_file_hash(filename):
    hasher = hashlib.sha256()
    with open(filename, "rb") as file:
        while True:
            data = file.read(65536)  # 64 KB chunks
            if not data:
                break
            hasher.update(data)
    return hasher.hexdigest()


def secure_file_deletion(file_path):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        logger.error(f"Error deleting file: {str(e)}")


def upload_to_s3(filename, file_path):
    bucket_name = get_secret_value_from_secret_manager("BUCKET_NAME")
    cloudfront_url = get_secret_value_from_secret_manager("CLOUDFRONT_URL")
    s3 = boto3.client("s3")
    logger.info(f"Uploading {filename} to S3")
    file_name_with_spaces = filename.replace("_", "-").replace(" ", "-")
    logger.info(f"{file_name_with_spaces} Final renamed filename")
    s3_object_key = f"{datetime.now().strftime('%Y-%m-%d')}/{file_name_with_spaces}"
    file_extension = filename.split(".")[-1]
    # Get content type from CONTENT_TYPES dictionary
    content_type = CONTENT_TYPES.get(file_extension)
    logger.info(f"Extension: {file_extension}, Content Type: {content_type}")
    if not content_type:
        raise ValueError(
            f"Content type for file extension '{file_extension}' not found"
        )

    s3.upload_file(
        file_path,
        bucket_name,
        s3_object_key,
        ExtraArgs={"ContentType": content_type},
    )
    s3_url = f"{cloudfront_url}/{s3_object_key}"
    return s3_url


ALLOWED_EXTENSIONS = ["pdf", "doc", "docx", "md"]


def generate_bad_request_response(msg):
    return {"status": False, "body": json.dumps(msg)}, HTTPStatus.BAD_REQUEST.value


def handle_csv_file(event):
    error = None
    column_name = event["headers"].get("X-Header", None)
    if not column_name:
        error = "if the file type is csv, source_column is required in X-Header"
    return column_name, error


def handle_uploaded_file_success(filename, file_path, collection_name):
    with app.app_context():
        s3_url = upload_to_s3(filename, file_path)
        output = insert_data_into_vector_db(file_path, s3_url, collection_name)
        user_file = UserFiles(file_name=file_path, embedded=True, s3_url=s3_url)
        logger.info(f"USER FILE: {user_file}")
        db.session.add(user_file)
        db.session.commit()
        return {"message": output, "s3_url": s3_url}


def sanitize_filename(filename):
    return secure_filename(filename)


def validate_filename(filename):
    return re.match(r"^[a-zA-Z0-9_.-]+$", filename) is not None


def handle_valid_file(
    safe_filename, file_path, file_content, collection_name, conversation_id
):
    with app.app_context():
        logger.info(f"safe_filename.....{safe_filename}")
        logger.info(f"file_path................{file_path}")
        logger.info(f"file_content................{file_content}")
        file_format = safe_filename.split(".")[-1]
        if file_format in ALLOWED_EXTENSIONS:
            logger.info("Entered File Format")
            with open(file_path, "wb") as file:
                file.write(file_content)
            handle_uploaded_file_success(safe_filename, file_path, collection_name)

            return {
                "status": True,
                "success": True,
                "conversation_id": conversation_id,
            }, HTTPStatus.OK.value
        else:
            return generate_bad_request_response(
                f"Allowed extensions are {','.join(ALLOWED_EXTENSIONS)}"
            )


class InvalidFilePath(Exception):
    def __init__(self, message):
        super().__init__(message)


def path_traversal_check(file_name):
    error = None
    sanitized_file_name = secure_filename(file_name)
    if os.path.dirname(sanitized_file_name) != "":
        error = "Access denied: Attempted path traversal"
        return None, error  # Return None for file path

    # Use os.path.join for constructing paths
    file_path = os.path.join(BASE_DIR, sanitized_file_name)
    real_path = os.path.abspath(file_path)

    if not real_path.startswith(os.path.abspath(BASE_DIR)):
        error = "Access denied: Attempted path traversal"
        return None, error  # Return None for file path

    return real_path, error


def lambda_handler1(*args):
    with app.app_context():
        event = args[0]
        file_name = ""
        file_path = ""
        try:
            # Check if the body is empty or if the X-Filename header is missing
            if "body" not in event or not event["body"]:
                return generate_bad_request_response(
                    "No file content provided. Please pass the file content."
                )
            # Decode the file content if it's base64 encoded
            if event.get("isBase64Encoded", False):
                file_content = base64.b64decode(event["body"])
            else:
                file_content = event["body"]
            # Extract the filename from the headers
            file_name = event["headers"].get("X-Filename")
            conversation_id = event["headers"].get("Conversation-Id")
            time_stamp = event["headers"].get("time_stamp")
            user_id = event["headers"].get("User-Id")

            logger.info(
                f"user_id: {user_id}, time_stamp: {time_stamp}, conversation_id: {conversation_id}"
            )
            if not file_name:
                return generate_bad_request_response("X-Filename headers is missing")
            else:
                safe_filename = sanitize_filename(file_name)
                if not validate_filename(safe_filename):
                    return generate_bad_request_response("Invalid file name")
                else:
                    file_path, error = path_traversal_check(safe_filename)
                    if error:
                        return generate_bad_request_response(error)
            return handle_valid_file(
                file_name, file_path, file_content, conversation_id
            )
        except Exception:
            return {
                "status": False,
                "errors": json.dumps(traceback.format_exc().strip()),
            }, HTTPStatus.INTERNAL_SERVER_ERROR.value
        finally:
            secure_file_deletion(file_path)


def lambda_handler(*args):
    event = args[0]
    return call_fn(lambda_handler1, event)
