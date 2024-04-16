from ai.chat.apis import call_add_error_details_api
from ai.common.api_validations import (
    MESSAGE_LENGTH,
    MESSAGE_SET,
    ChatAPIValidationMessage,
)


def validate_user_input(user_input, message_log, time_stamp):
    """
    Validates user input against certain conditions and formats.

    This function ensures that the 'message_log' is a list, that its length is even,
    and that 'time_stamp'  follows the specific pattern. It also ensures that the
    'user_input' does not exceed a length of 300. If any of these conditions are not met,
    the function logs the error in the database and returns a
    generated error message. If all conditions are met, the function returns None.

    Args:
        user_input (str): The user's input string.
        message_log (list): A list of previous message logs.
        time_stamp (str): A string containing the time stamp of the user's input.

    Returns:
        None or str: If validation fails, returns the error message as a string.
        Otherwise, returns None.
    """
    if not user_input:
        call_add_error_details_api(
            user_input, ChatAPIValidationMessage.REQUIRED_PARAMETER.get_all()
        )
        return ChatAPIValidationMessage.REQUIRED_PARAMETER.get_message()
    else:
        if not isinstance(message_log, list):
            call_add_error_details_api(
                user_input,
                ChatAPIValidationMessage.MESSAGE_LOG_SHOULD_BE_OF_TYPE_LIST.get_all(),
            )
            return (
                ChatAPIValidationMessage.MESSAGE_LOG_SHOULD_BE_OF_TYPE_LIST.get_message()
            )

        if len(message_log) % MESSAGE_SET != 0:
            call_add_error_details_api(
                user_input,
                ChatAPIValidationMessage.MESSAGE_LOG_SHOULD_BE_OF_EVEN_LENGTH.get_all(),
            )
            return (
                ChatAPIValidationMessage.MESSAGE_LOG_SHOULD_BE_OF_EVEN_LENGTH.get_message()
            )

        if len(user_input) > MESSAGE_LENGTH:
            call_add_error_details_api(
                user_input,
                ChatAPIValidationMessage.USER_INPUT_SHOULD_BE_IN_EXPECTED_LENGTH.get_all(),
            )
            return (
                ChatAPIValidationMessage.USER_INPUT_SHOULD_BE_IN_EXPECTED_LENGTH.get_message(),
            )

        return None
