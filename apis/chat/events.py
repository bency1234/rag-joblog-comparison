from ai.common.constants import EMIT_RESPONSE, RECEIVE_REQUEST
from ai.common.utils.stream import construct_msg
from chat.dev_utils import socketio
from chat.main import handle_user_query
from common.envs import logger
from common.utils.constant import THROTTLE_CODE, THROTTLE_MSG
from common.utils.redis import throttle_request_by_ip
from flask import request
from flask_socketio import emit


@socketio.on("connect")
def handle_connect():
    logger.info("Client connected!")


@socketio.on(RECEIVE_REQUEST)
def handle_request(user_req):
    """
    Handle a user request by throttling and processing the query.

    Args:
        user_req (str): The user request/query.

    Returns:
        None

    Side Effects:
        - Retrieves the IP address from the request context.
        - Throttles the request based on the IP address using the 'throttle_request_by_ip' function.
        - Emits a response if the request is throttled.
        - Handles the user query by calling the 'handle_user_query' function.
    """
    ip_address = request.remote_addr
    allowed, time_left = throttle_request_by_ip(ip_address)

    if not allowed:
        emit(
            EMIT_RESPONSE,
            construct_msg(THROTTLE_MSG(time_left), THROTTLE_CODE, False, time_left),
        )
    else:
        logger.info(request)
        handle_user_query(user_req)
