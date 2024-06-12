import json

from flask_socketio import emit

from ..api_validations import ChatAPIResponseParameters
from ..constants import EMIT_RESPONSE


def construct_msg(msg, status_code, status=False, time_left=None):
    """
    Construct a message dictionary.

    Args:
        msg (str): The message to include in the dictionary.
        status_code (int): The status code to include in the dictionary.
        status (str): The status to include in the dictionary.
        time_left (int, optional): The time left (in seconds) until the next allowed request. Default is None.

    Returns:
        dict: A dictionary containing the message, status code, status, and optional time left.
    """
    return {
        ChatAPIResponseParameters.MESSAGE.value: msg,
        ChatAPIResponseParameters.STATUS.value: status,
        ChatAPIResponseParameters.STATUS_CODE.value: status_code,
        ChatAPIResponseParameters.TIME_LEFT.value: time_left,
    }


def construct_bot_response(msg):
    return {ChatAPIResponseParameters.RESPONSE.value: msg}


def stream_response(msg, client=None, connection_id=None, status_code=200, status=True):
    """
    Emits a response message with the given content, status code, and status.

    Returns:
        bool: True if the response was successfully emitted.
    """

    if client:
        client.post_to_connection(
            ConnectionId=connection_id,
            Data=json.dumps(construct_msg(msg, status_code, status)).encode("utf-8"),
        )
    else:
        emit(EMIT_RESPONSE, construct_msg(msg, status_code, status))
