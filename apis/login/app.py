import base64
import json
from http import HTTPStatus

from common.app_utils import get_app
from common.chatbot import User
from common.db import db
from common.envs import get_secret_value_from_secret_manager, logger
from common.lambda_utils import call_fn
from werkzeug.security import generate_password_hash

app = get_app(db)


def login(*args):
    with app.app_context():
        try:
            event = args[0]
            print(event)
            if "body" not in event or not event["body"]:
                return {
                    "message": "Username or password not provided"
                }, HTTPStatus.BAD_REQUEST

            file_content = (
                base64.b64decode(event["body"])
                if event.get("isBase64Encoded", False)
                else event["body"]
            )

            # Decode bytes to string and load JSON
            data = json.loads(file_content.decode("utf-8"))

            if "username" not in data or "password" not in data:
                return {
                    "message": "Both username and password are required"
                }, HTTPStatus.BAD_REQUEST

            # Access user_input and thread_id
            username = data["username"]
            password = data["password"]
            # Check if username and password match
            if username == get_secret_value_from_secret_manager(
                "USERNAME"
            ) and password == get_secret_value_from_secret_manager("PASSWORD"):
                user = User.query.filter_by(username=username).first()
                if not user:
                    print("Writing user to DB")
                    hashed_password = generate_password_hash(password)
                    user = User(username=username, password=hashed_password)
                    db.session.add(user)
                db.session.commit()
                return {"message": "Login successful!"}, HTTPStatus.OK
            else:
                return {
                    "message": "Invalid username or password"
                }, HTTPStatus.UNAUTHORIZED

        except Exception as e:
            logger.error(f"An error occurred: {str(e)}", exc_info=True)
            return {
                "message": "An error occurred",
                "errors": str(e),
            }, HTTPStatus.INTERNAL_SERVER_ERROR


def lambda_handler(*args):
    event = args[0]
    logger.info("Calling Login Function")
    return call_fn(login, event)
