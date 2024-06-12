import base64
import json

from .cors import get_origins
from .db import db
from .envs import logger


def generate_headers(request_origin):
    return {
        "Access-Control-Allow-Origin": request_origin,
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Content-Type": "application/json",
        "Access-Control-Allow-Headers": "Content-Type",
    }


def get_event_data(event):
    # Decode the file content if it's base64 encoded
    if event.get("isBase64Encoded", False):
        body = json.loads(base64.b64decode(event["body"]))
    else:
        body = json.loads(event["body"])

    return body


def call_fn(fn, event):
    import json

    # Get the "headers" dictionary from the "event" dictionary, defaulting to an empty dictionary
    # if "headers" is not present.
    headers = event.get("headers", {})

    # Check if "origin" header exists in the headers, if yes, use its value,
    # otherwise use the value of "Origin" header.
    # In lambda, origin would be in header origin and in local, origin would be in header Origin
    request_origin = headers.get("origin") or headers.get("Origin")

    origins = get_origins()

    if request_origin in origins:
        logger.info("Origin allowed")

        if event["httpMethod"] == "OPTIONS":
            # Handle preflight request
            return {"statusCode": 200, "headers": generate_headers(request_origin)}
        else:
            data, status_code = fn(event, db)

            return {
                "statusCode": status_code,
                "body": json.dumps(data),
                "headers": generate_headers(request_origin),
            }
    else:
        return {
            "statusCode": 200,
            "body": "CORS Origin is not allowed here",
            "headers": generate_headers(request_origin),
        }
