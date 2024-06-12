import os

from ai.common.colors import pr_green
from ai.llms.constants import LLM
from chat.events import socketio
from common.db import db
from dotenv import load_dotenv
from flask import Flask
from flask_migrate import Migrate

load_dotenv()

MIGRATIONS_FOLDER = "./migrations" if "backend" in os.getcwd() else "backend/migrations"


def get_origins():
    # Get the value of CORS_ORIGIN from the environment variable
    CORS_ORIGIN = os.getenv("CORS_ORIGIN")

    # Check if CORS_ORIGIN contains a semicolon
    if ";" in CORS_ORIGIN:
        # Split the CORS_ORIGIN string into a list of origins
        origins = CORS_ORIGIN.split(";")
    else:
        # If there's only semicolon, use the value itself otherwise use the values in a list
        origins = CORS_ORIGIN if CORS_ORIGIN == "*" else [CORS_ORIGIN]

    return origins


def create_app():
    pr_green(f"Using {LLM} as LLM")
    app = Flask(__name__)
    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "Chatbot API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config[
        "SQLALCHEMY_DATABASE_URI"
    ] = f'postgresql://{os.getenv("DATABASE_USER")}:{os.getenv("DATABASE_PASS")}@{os.getenv("DATABASE_HOST")}:{os.getenv("DATABASE_PORT")}/{os.getenv("DATABASE_NAME")}'
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 Megabytes

    origins = get_origins()

    db.init_app(app)

    Migrate(app, db, directory=MIGRATIONS_FOLDER)

    socketio.init_app(app, cors_allowed_origins=origins)

    return app


if __name__ == "__main__":
    pr_green("Application Started!")
    app = create_app()
    socketio.run(app, host="0.0.0.0", port=5000, allow_unsafe_werkzeug=True)
