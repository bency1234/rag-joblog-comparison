import os

import psycopg2
from ai.chat.apis import call_add_error_details_api
from ai.chat.error_details_exception import capture_error_details
from common.app_utils import get_app
from common.db import db
from common.envs import get_secret_value_from_secret_manager, logger

app = get_app(db)
conn = psycopg2.connect(
    host=os.environ.get(
        "PGVECTOR_HOST", get_secret_value_from_secret_manager("DATABASE_HOST")
    ),
    user=os.environ.get(
        "PGVECTOR_USER", get_secret_value_from_secret_manager("DATABASE_USER")
    ),
    password=os.environ.get(
        "PGVECTOR_PASSWORD", get_secret_value_from_secret_manager("DATABASE_PASS")
    ),
    database=os.environ.get(
        "PGVECTOR_DATABASE", get_secret_value_from_secret_manager("DATABASE_NAME")
    ),
)


def is_collection_name_exists(collection_name_check):
    with app.app_context():
        try:
            # Connect to the PostgreSQL database
            query = (
                "SELECT EXISTS (SELECT 1 FROM langchain_pg_collection WHERE name = %s)"
            )
            with conn.cursor() as cursor:
                cursor.execute(query, (collection_name_check,))
                exists = cursor.fetchone()[0]
                return exists

        except Exception as e:
            error_info = capture_error_details(e)
            call_add_error_details_api(user_input=None, error=error_info)
            logger.info(f"An error occurred: {e}")
