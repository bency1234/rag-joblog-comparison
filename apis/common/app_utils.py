from flask import Flask

from .envs import get_secret_value_from_secret_manager


def get_app(db):
    app = Flask(__name__)

    app.config[
        "SQLALCHEMY_DATABASE_URI"
    ] = f'postgresql://{get_secret_value_from_secret_manager("DATABASE_USER")}:{get_secret_value_from_secret_manager("DATABASE_PASS")}@{get_secret_value_from_secret_manager("DATABASE_HOST")}:{get_secret_value_from_secret_manager("DATABASE_PORT")}/{get_secret_value_from_secret_manager("DATABASE_NAME")}'

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    return app


def read_database_url_from_secret_manager():
    return (
        f'postgresql://{get_secret_value_from_secret_manager("DATABASE_USER")}:'
        f'{get_secret_value_from_secret_manager("DATABASE_PASS")}@{get_secret_value_from_secret_manager("DATABASE_HOST")}:'
        f'{get_secret_value_from_secret_manager("DATABASE_PORT")}/{get_secret_value_from_secret_manager("DATABASE_NAME")}'
    )
