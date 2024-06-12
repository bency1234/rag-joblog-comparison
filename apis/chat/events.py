from ai.common.constants import RECEIVE_REQUEST
from chat.dev_utils import socketio
from chat.main import handle_user_query
from common.envs import logger


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
    handle_user_query(user_req)
