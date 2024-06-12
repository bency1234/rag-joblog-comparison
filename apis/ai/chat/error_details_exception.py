import traceback

from common.envs import logger


def capture_error_details(exception):
    """
    Captures the type and details of the provided exception.

    Args:
    - exception (Exception): The exception to capture details from.

    Returns:
    - tuple: A tuple containing the error type (str) and error details (str).
    """
    error_type = type(exception).__name__
    error_details = traceback.format_exc()
    logger.info(f"Error type: {error_type}, Error details: {error_details}")
    return error_type, error_details
