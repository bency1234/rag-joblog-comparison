import os

from common.envs import get_secret_value_from_secret_manager
from langchain.vectorstores.pgvector import PGVector

################################# Migrations constants ##########################################
now = "now()"
################################# Migrations constants ##########################################

#################################  DEBUG_CSV Constants starts here #################################
INITIAL_PROMPT = "initial_prompt"
INITIAL_RESPONSE = "initial_response"
COST = "cost"
#################################  DEBUG_CSV Constants ends here #################################

################################# APP Constants starts here #################################
API_URL = get_secret_value_from_secret_manager("API_URL") or "http://localhost:5000/"
################################# APP Constants ends here #################################

################################# Database connection constants starts here #################################
CONNECTION_STRING = PGVector.connection_string_from_db_params(
    driver=os.environ.get("PGVECTOR_DRIVER", "psycopg2"),
    host=os.environ.get(
        "PGVECTOR_HOST", get_secret_value_from_secret_manager("DATABASE_HOST")
    ),
    port=os.environ.get(
        "PGVECTOR_PORT", get_secret_value_from_secret_manager("DATABASE_PORT")
    ),
    database=os.environ.get(
        "PGVECTOR_DATABASE", get_secret_value_from_secret_manager("DATABASE_NAME")
    ),
    user=os.environ.get(
        "PGVECTOR_USER", get_secret_value_from_secret_manager("DATABASE_USER")
    ),
    password=os.environ.get(
        "PGVECTOR_PASSWORD", get_secret_value_from_secret_manager("DATABASE_PASS")
    ),
)
################################# Database connection constants ends here #################################


################################# Throttle constants starts here #################################
THROTTLE_MSG = (
    lambda time: f"Sorry, we are currently limiting the number of requests to ensure a smooth experience for all users. "
    f"Please try again in {time} seconds. Thank you for understanding!"
)
THROTTLE_CODE = 429
THROTTLE_PERIOD = 60
################################# Throttle constants ends here #################################

################################# Stream constants starts here #################################
RECEIVE_REQUEST = "chat"
EMIT_RESPONSE = "stream"
################################# Stream constants ends here #################################

FILE_NOT_FOUND = "File not found"
USER_NOT_FOUND = "User not found"
UserFileNotFoundError = "User FileNot Found Error"
S3FileNotFoundError = "S3 File Not Found Error"
