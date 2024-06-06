import redis
from common.envs import logger
from common.utils.constant import (
    REDIS_HOST,
    REDIS_PORT,
    REQUESTS_PER_MINUTE,
    THROTTLE_PERIOD,
)

# Initialize Redis client
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)


def get_ip_address(event):
    # Get IP address from event
    if "requestContext" in event and "identity" in event["requestContext"]:
        ip_address = event["requestContext"]["identity"].get("sourceIp", None)
    elif "identity" in event:
        ip_address = event["identity"].get("sourceIp", None)
    else:
        ip_address = None
    return ip_address


def throttle_request_by_ip(ip_address):
    """
    Throttle requests based on the IP address.
    Args:
        ip_address (str): The IP address from which the request is made.
    Returns:
        tuple: A tuple containing two values:
            - A boolean indicating whether the request is allowed or throttled.
            - The time left (in seconds) until the IP address
            can make another request if it's throttled.
              If the request is allowed, this value is None.
    """
    key = f"ip_throttle:{ip_address}"
    count = redis_client.incr(key)
    logger.info(f"IP {ip_address}: incremented count to {count}")
    if count == 1:
        redis_client.expire(key, THROTTLE_PERIOD)
    elif count > REQUESTS_PER_MINUTE:
        time_left = redis_client.ttl(key)
        return False, time_left

    return True, None
