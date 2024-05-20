import traceback
from http import HTTPStatus

from common.app_utils import get_app
from common.chatbot import ChatbotData, Feedback
from common.db import db
from common.envs import logger
from common.lambda_utils import call_fn, get_event_data

app = get_app(db)


def replace_quotes(datas):
    """
    Bot response may include single quotes when we pass that with conn execute will return syntax error.
    So, let's replace single quotes with double quotes.
    Reference: https://stackoverflow.com/questions/12316953/insert-text-with-single-quotes-in-postgresql
    """
    record = []
    for data in datas:
        if isinstance(data, str):
            record.append(data.replace("'", "''"))
        else:
            record.append(data)
    return record


def write_to_db(*args):
    try:
        event = args[0]
        data = get_event_data(event)
        record = data.get("record")
        user_id = data.get("user_id")
        logger.info(f"Record: {record}")
        logger.info(f"User ID: {user_id}")
        record = replace_quotes(record)

        [
            user_input,
            raw_prompt,
            bot_response,
            response_time,
            cost,
            time_stamp,
            message_log,
            source_documents,
            use_rag,
        ] = record[:9]

        with app.app_context():
            chatbot_data = ChatbotData(
                user_input=user_input,
                prompt=raw_prompt,
                final_response=bot_response,
                response_time=response_time,
                exchange_cost=cost,
                time_stamp=time_stamp,
                user_id=user_id,
                message_log=message_log,
                source_documents=source_documents,
                use_rag=use_rag,
            )
            logger.info(f"Chatbot data: {chatbot_data}")
            db.session.add(chatbot_data)
            db.session.commit()
            row_id = chatbot_data.id

            feedback_data = Feedback(
                exchange_id=row_id,
                response_status="pending",
                feedback="",
            )
            db.session.add(feedback_data)
            db.session.commit()

        return (
            {
                "status": True,
                "message": "Chatbot data added successfully.",
                "id": row_id,
            },
            HTTPStatus.OK.value,
        )
    except Exception as e:
        traceback.print_exception(e)
        logger.error(f"An error occurred: {str(e)}")
        return (
            {
                "status": False,
                "message": "An error occurred while adding data to the chatbot table.",
            },
            HTTPStatus.INTERNAL_SERVER_ERROR.value,
        )


def lambda_handler(*args):
    event = args[0]
    return call_fn(write_to_db, event)
