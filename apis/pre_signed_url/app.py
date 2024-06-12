from datetime import datetime
from http import HTTPStatus

import boto3
from common.app_utils import get_app
from common.chatbot import User, UserFiles
from common.db import db
from common.envs import get_secret_value_from_secret_manager, logger
from common.lambda_utils import call_fn, get_event_data

app = get_app(db)


# Define a dictionary to map file extensions to MIME types
CONTENT_TYPES = {
    "pdf": "application/pdf",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "md": "text/markdown",
    # Add more file types if needed
}


def generate_signed_url(user_id, extension, filename):
    """
    Generates presigned URLs for each file provided.

    Args:
        user_id (str): The ID of the user.
        ext_data (list): The list of file extensions.
        filename (str): The base name of the file.

    Returns:
        list: A list of dictionaries each containing a presigned URL and the file storage path.
    """

    logger.info(f"Generating signed URL for user_id={user_id}, filename={filename}")
    s3 = boto3.client("s3")

    def obtain_signed_url(params):
        response = s3.generate_presigned_url(
            ClientMethod="put_object",
            Params=params,
            ExpiresIn=3600,  # Expiration time in seconds
        )
        return response if response else False

    # Get the MIME type for the file extension
    content_type = CONTENT_TYPES.get(extension)
    current_date = datetime.now().strftime("%Y-%m-%d")
    file_storage_path = f"{current_date}/{filename}"
    params = {
        "Bucket": get_secret_value_from_secret_manager("BUCKET_NAME"),
        "Key": file_storage_path,
        "ContentType": content_type,
    }
    print("")

    return (
        obtain_signed_url(params),
        f"{get_secret_value_from_secret_manager('CLOUDFRONT_URL')}/{file_storage_path}",
        content_type,
    )


def get_pre_signed_url(request):
    """
    Handles file upload requests. Extracts file and user data from the request,
    generates presigned URLs for each file, and returns them.

    Args:
        request (object): The request object containing user ID, file data, and filenames.

    Returns:
        dict: A dictionary with status and either the presigned URLs or an error message.
    """
    logger.info("Processing presigned URL request")
    presigned_url, s3_url, content_type, status_code, error = (
        None,
        None,
        None,
        None,
        None,
    )
    # with app.app_context():
    try:
        # Get signed URL from AWS
        u_id = request.get("id")
        filename = request.get("filename")
        extension = filename.split(".")[-1]

        if u_id and filename:
            user = User.query.filter_by(id=u_id).first()

            if extension in CONTENT_TYPES.keys():
                logger.info("Generating presigned URL")
                presigned_url, s3_url, content_type = generate_signed_url(
                    user.id, extension, filename
                )
                logger.info("Presigned URL generation complete")
                status_code = HTTPStatus.OK.value
            else:
                allowed_files = ", ".join([f"'{key}'" for key in CONTENT_TYPES.keys()])
                error = f"Only {allowed_files} files are allowed"
                status_code = HTTPStatus.BAD_REQUEST.value
                logger.error(error)
        else:
            error = "username or filename parameter is missing"
            status_code = HTTPStatus.BAD_REQUEST.value
            logger.error(error)
    except Exception as e:
        logger.error(f"Error: {e}")
        error = "INTERNAL SERVER ERROR"
        status_code = HTTPStatus.INTERNAL_SERVER_ERROR.value

    return presigned_url, s3_url, content_type, status_code, error


def handle_signed_url(*args):
    event = args[0]
    request = get_event_data(event)
    presigned_url, s3_url, content_type, status_code, error = get_pre_signed_url(
        request
    )
    if not error:
        password = request.get("password", None)
        file = request.get("filename")
        file_info = UserFiles(
            file_name=file,
            s3_url=s3_url,
            password=password,
        )

        db.session.add(file_info)
        db.session.commit()
        logger.info("File info saved successfully")
    else:
        logger.error(f"Error occurred: {error}")
    return {
        "presigned_url": presigned_url,
        "s3_url": s3_url,
        "content_type": content_type,
        "status": False if error else True,
        "error": error,
    }, status_code


def lambda_handler(*args):
    logger.info("Pre signed lambda invoked")
    event = args[0]
    with app.app_context():
        return call_fn(handle_signed_url, event)
