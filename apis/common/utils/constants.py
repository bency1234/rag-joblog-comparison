from common.envs import get_secret_value_from_secret_manager

################################# Throttle constants starts here #################################
THROTTLE_MSG = (
    lambda time: f"Sorry, we are currently limiting the number of requests to ensure a smooth experience for all users. "
    f"Please try again in {time} seconds. Thank you for understanding!"
)
THROTTLE_CODE = 429
THROTTLE_PERIOD = 60
################################# Throttle constants ends here #################################

################################# Redis constants starts here #################################
REDIS_HOST = get_secret_value_from_secret_manager("REDIS_HOST")
REDIS_PORT = get_secret_value_from_secret_manager("REDIS_PORT")
WS_ENDPOINT = get_secret_value_from_secret_manager("WS_ENDPOINT")
REQUESTS_PER_MINUTE = int(get_secret_value_from_secret_manager("REQUESTS_PER_MINUTE"))
################################# Redis constants ends here #################################
