import requests
from ai.common.constants import API_URL
from common.envs import get_secret_value_from_secret_manager, logger

HEADERS = {
    "Origin": get_secret_value_from_secret_manager("CORS_ORIGIN").split(";")[0],
}


def call_add_error_details_api(user_input, error):
    """
    Calls the 'add-error-details' API endpoint to add error details to the database.
    This function sends a POST request to the 'add-error-details' API endpoint with provided
    user input, error type, error details, and a default user ID.
    """
    user_id = 1
    error_type, error_details = error
    logger.info(f"Error Type: {error_type}, Error Details: {error_details}")
    requests.post(
        f"{API_URL}add-error-details",
        headers=HEADERS,
        json={
            "user_input": user_input,
            "error_type": error_type,
            "error_details": error_details,
            "user_id": user_id,
        },
    )


def call_write_to_db_api(record, user_id=1):
    """
    Calls the 'write_to_db' API endpoint to write a record to the database.
    This function sends a POST request to the 'write_to_db' API endpoint,
    and returns the ID of the written record from the response.
    """
    response = requests.post(
        f"{API_URL}/write_to_db",
        json={"record": record, "user_id": user_id},
        headers=HEADERS,
    )
    return response.json()["id"]
