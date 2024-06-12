import os

import psycopg2
from common.envs import get_secret_value_from_secret_manager, logger

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


def get_collection_uuid_by_name(collection_name, conversation_id):
    try:
        # Connect to the PostgreSQL database
        with conn.cursor() as cursor:
            # Execute the query
            query = "SELECT uuid FROM langchain_pg_collection WHERE name = %s"
            cursor.execute(query, (collection_name,))

            # Fetch the result
            result = cursor.fetchone()

            # Return the UUID if found
            if result:
                uuid = result[0]
                logger.info(f"The UUID for name '{collection_name}' is: {uuid}")
                update_query = """
                    UPDATE conversation
                    SET uuid = %s
                    WHERE id = %s
                    """
                cursor.execute(update_query, (uuid, conversation_id))

                conn.commit()

                return uuid
            else:
                logger.info(f"No UUID found for name '{collection_name}'")
                return None
    except Exception as e:
        logger.info(f"An error occurred: {e}")
