import json

import boto3
from common.app_utils import get_app
from common.db import db
from common.envs import get_secret_value_from_secret_manager, logger
from main import handle_user_query

app = get_app(db)
# Load environment variables
WS_ENDPOINT = get_secret_value_from_secret_manager("WS_ENDPOINT")
REQUESTS_PER_MINUTE = int(get_secret_value_from_secret_manager("REQUESTS_PER_MINUTE"))

# TODO
# Add Redis to limit request in a desired period of time


def get_ip_address(event):
    # Get IP address from event
    if "requestContext" in event and "identity" in event["requestContext"]:
        ip_address = event["requestContext"]["identity"].get("sourceIp", None)
    elif "identity" in event:
        ip_address = event["identity"].get("sourceIp", None)
    else:
        ip_address = None
    return ip_address


def lambda_handler(*args):
    try:
        with app.app_context():
            event = args[0]
            client = boto3.client(
                "apigatewaymanagementapi",
                endpoint_url=WS_ENDPOINT,
            )

            connection_id = event["requestContext"]["connectionId"]
            event_data = json.loads(event["body"])
            user_message = event_data["message"]

            handle_user_query(user_message, client, connection_id)
            return {"statusCode": 200, "body": "Success"}
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)
        return {"statusCode": 500, "body": "Internal Server Error"}
