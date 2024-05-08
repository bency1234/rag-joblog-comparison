from http import HTTPStatus

from common.app_utils import get_app
from common.chatbot import Feedback
from common.db import db
from common.envs import logger
from common.lambda_utils import call_fn, get_event_data

app = get_app(db)


def validate_feedback(feedback_text):
    if not isinstance(feedback_text, str):
        feedback_text = "-"
        return feedback_text
    # Trim leading and trailing whitespace
    sanitized_feedback = feedback_text.strip()

    # Replace backticks with double quotes
    sanitized_feedback = sanitized_feedback.replace("`", '"')

    # Check if feedback exceeds maximum length
    max_length = 500
    if len(sanitized_feedback) > max_length:
        raise ValueError(
            f"Feedback is too long. Maximum allowed length is {max_length} characters."
        )

    # Remove excess whitespace
    sanitized_feedback = " ".join(sanitized_feedback.split())

    return sanitized_feedback


def update_feedback(id, feedback, text):
    """
    Updates the feedback for a given record in the database.

    This function retrieves a record from the database by its ID and updates the feedback information.
    If the record exists, the function updates the `response_accepted` field of the record with the new feedback.
    It then adds the updated record to the database session and commits the session, saving the changes to the database.

    Args:
        id (int or str): The ID of the record to be updated.
        feedback (bool): The new feedback to update the record with.

    Returns:
        bool: True if the feedback was updated successfully, False otherwise.
    """
    success = False

    with app.app_context():
        feedback_data = db.session.query(Feedback).filter_by(exchange_id=id).first()
        # If the record doesn't exist
        if feedback_data is None:
            new_feedback = Feedback(
                exchange_id=id, response_status=feedback, feedback=text
            )
            db.session.add(new_feedback)
        else:
            # If the record exists, update its feedback fields
            feedback_data.response_status = feedback
            if text is not None:
                validate_text = validate_feedback(text)
                feedback_data.feedback = validate_text

        success = True
        db.session.commit()

    return success


def handle_user_feedback(*args):
    event = args[0]
    data = get_event_data(event)
    try:
        if ("id" not in data) and ("feedback" not in data):
            return {
                "status": False,
                "message": "id or feedback parameter is missing",
            }, HTTPStatus.BAD_REQUEST.value

        success = update_feedback(data.get("id", None), data["feedback"], data["text"])

        return {"status": success, "message": success}, HTTPStatus.OK.value
    except Exception as e:
        # Log the exception for further investigation
        logger.error(f"An error occurred: {str(e)}", exc_info=True)
        return {
            "status": False,
            "message": f"An error occurred while storing feedback record: {str(e)}",
        }, HTTPStatus.INTERNAL_SERVER_ERROR.value


def lambda_handler(event, context):
    return call_fn(handle_user_feedback, event)
