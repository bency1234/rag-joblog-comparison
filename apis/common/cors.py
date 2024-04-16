from .envs import get_secret_value_from_secret_manager


def get_origins():
    # Get the value of CORS_ORIGIN from the environment variable
    CORS_ORIGIN = get_secret_value_from_secret_manager("CORS_ORIGIN")

    # Check if CORS_ORIGIN contains a semicolon
    if ";" in CORS_ORIGIN:
        # Split the CORS_ORIGIN string into a list of origins
        origins = CORS_ORIGIN.split(";")
    else:
        # If there's only semicolon, use the value itself otherwise use the values in a list
        origins = CORS_ORIGIN if CORS_ORIGIN == "*" else [CORS_ORIGIN]

    return origins
