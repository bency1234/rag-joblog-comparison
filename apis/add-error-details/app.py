from http import HTTPStatus

from common.app_utils import get_app
from common.chatbot import ChatError
from common.db import db
from common.envs import logger
from common.lambda_utils import call_fn, get_event_data

app = get_app(db)


def is_valid_input(input_value):
    """
    Validates if the input value is a safe string.
    This function can be enhanced based on the specific validation needs,
    such as length checks, character whitelisting, etc.
    """
    # Basic example validation: check if not empty and is a string
    return isinstance(input_value, str) and input_value.strip() != ""


def is_valid_user_id(user_id):
    """
    Validates if the user_id is valid. For simplicity, check if it's an integer.
    """
    try:
        int(user_id)
        return True
    except ValueError:
        return False


def add_error_details_in_db(event, db):
    with app.app_context():
        try:
            data = get_event_data(event)

            # Extract and validate inputs
            user_input = data.get("user_input")
            error_type = data.get("error_type")
            error_details = data.get("error_details")
            user_id = data.get("user_id")

            # Validate inputs before processing
            if not (
                is_valid_input(user_input)
                and is_valid_input(error_type)
                and is_valid_input(error_details)
                and is_valid_user_id(user_id)
            ):
                return {
                    "status": False,
                    "message": "Invalid input provided.",
                }, HTTPStatus.BAD_REQUEST.value

            chatbot_response = ChatError(
                user_input=user_input,
                error_details=error_details,
                error_type=error_type,
                user_id=user_id,
            )

            db.session.add(chatbot_response)
            db.session.commit()

            return {
                "status": True,
                "message": "Error details added successfully.",
                "id": chatbot_response.id,
            }, HTTPStatus.OK.value
        except Exception as e:
            logger.error(f"Error Line: {e}")
            return {
                "status": False,
                "message": "An error occurred while adding error details.",
            }, HTTPStatus.INTERNAL_SERVER_ERROR.value


def lambda_handler(event, context):
    return call_fn(add_error_details_in_db, event)
