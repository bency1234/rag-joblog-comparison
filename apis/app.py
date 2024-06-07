import os

from ai.prompts.system_prompt import TOGGLE_OFF_SYSTEM_PROMPT, TOGGLE_ON_SYSTEM_PROMPT
from common.chatbot import SystemPrompt
from common.db import db
from common.envs import logger
from flask import Flask
from flask_migrate import Migrate, upgrade
from flask_seeder import FlaskSeeder

MIGRATIONS_FOLDER = "./migrations"


class SystemPromptSeeder:
    """
    Adds system prompts to the database based on the 'prompt_data' attribute.
    Skips adding prompts that already exist in the database.
    Prints status messages for each prompt added or skipped.
    """

    prompt_data = {
        "TOGGLE_ON_SYSTEM_PROMPT": {
            "content": TOGGLE_ON_SYSTEM_PROMPT,
            "type": "System Prompt",
        },
        "TOGGLE_OFF_SYSTEM_PROMPT": {
            "content": TOGGLE_OFF_SYSTEM_PROMPT,
            "type": "System Prompt",
        },
    }

    @classmethod
    def run(cls):
        for prompt_type, prompt_info in cls.prompt_data.items():
            content = prompt_info["content"]
            prompt_type = prompt_info["type"]
            existing_prompt = SystemPrompt.query.filter_by(content=content).first()

            if existing_prompt:
                logger.info(
                    f"Content already exists for type: {prompt_type}. Skipping..."
                )
            else:
                prompt = SystemPrompt(content=content, type=prompt_type)
                db.session.add(prompt)
                db.session.commit()
                logger.info(f"Content added for type: {prompt_type}")


def create_app():
    # pr_green(f"Using {LLM} as LLM")
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

    db.init_app(app)

    Migrate(app, db, directory=MIGRATIONS_FOLDER)

    return app


if __name__ == "__main__":
    app = create_app()

    with app.app_context():
        # upgrade()
        seeder = FlaskSeeder()
        seeder.init_app(app, db)

        system_seeder = SystemPromptSeeder()
        system_seeder.run()
