from common.app_utils import read_database_url_from_secret_manager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

database_uri = read_database_url_from_secret_manager()


def create_session():
    engine = create_engine(database_uri)
    session = sessionmaker(bind=engine)()
    return session
