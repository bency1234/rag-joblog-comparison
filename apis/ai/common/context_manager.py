from contextlib import contextmanager

from common.db import db
from common.envs import logger
from sqlalchemy.exc import SQLAlchemyError


@contextmanager
def database_operation(operation, obj=None, **kwargs):
    """Perform database operations using context manager."""
    session = db.session
    try:
        if operation == "scope":
            yield session
        elif operation == "insert":
            new_obj = obj(**kwargs)
            session.add(new_obj)
            session.commit()
            yield new_obj
        else:
            raise ValueError("Invalid operation specified")
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(
            f"An error occurred during database operation: {str(e)}", exc_info=True
        )
        raise

    finally:
        session.close()
