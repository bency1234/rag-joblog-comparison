from http import HTTPStatus

from common.app_utils import get_app
from common.chatbot import ChatbotData, EvaluationScores, Feedback
from common.db import db
from common.envs import logger
from common.evaluate import evaluate_chatbot_data
from common.lambda_utils import call_fn
from sqlalchemy import update

app = get_app(db)


def fetch_chat_data():
    return ChatbotData.query.filter_by(is_evaluated=False).all()


def fetch_all_feedback(chat_data):
    # Extracts exchange_ids from chat_data to fetch all corresponding Feedback records
    exchange_ids = [chat.id for chat in chat_data]
    feedbacks = Feedback.query.filter(Feedback.exchange_id.in_(exchange_ids)).all()

    # Creates a dictionary to map each exchange_id to its feedback
    feedback_dict = {feedback.exchange_id: feedback.feedback for feedback in feedbacks}
    return feedback_dict


# Stores the evaluation results in the database
def store_evaluation(exchange_id, user_input, final_response, feedback, results):
    evaluation_data = EvaluationScores(
        exchange_id=exchange_id,
        user_input=user_input,
        final_response=final_response,
        feedback=feedback,
        faithfulness=results["faithfulness"],
        answer_relevancy=results["answer_relevancy"],
        context_utilization=results["context_utilization"],
    )
    db.session.add(evaluation_data)


# Evaluates each chat entry and stores their IDs for bulk update
def evaluate_responses_and_update(chat_data, feedback_dict):
    chat_ids = []
    for chat in chat_data:
        feedback = feedback_dict.get(chat.id)
        results = evaluate_chatbot_data(
            chat.user_input, chat.final_response, chat.source_documents
        )
        store_evaluation(
            chat.id, chat.user_input, chat.final_response, feedback, results
        )
        chat_ids.append(chat.id)
    return chat_ids


def evaluate_response(*args):
    with app.app_context():
        try:
            chat_data = fetch_chat_data()
            if not chat_data:
                return {"message": "No chat data to evaluate"}, HTTPStatus.OK
            feedback_dict = fetch_all_feedback(chat_data)
            chat_ids = evaluate_responses_and_update(chat_data, feedback_dict)
            # Bulk update the is_evaluated flag for all evaluated chats
            if chat_ids:
                db.session.execute(
                    update(ChatbotData)
                    .where(ChatbotData.id.in_(chat_ids))
                    .values(is_evaluated=True)
                )
            db.session.commit()

            return {"message": "success"}, HTTPStatus.OK

        except Exception as e:
            db.session.rollback()
            logger.error(f"An error occurred: {str(e)}", exc_info=True)
            return {
                "message": "An error occurred",
                "errors": str(e),
            }, HTTPStatus.INTERNAL_SERVER_ERROR


def lambda_handler(event, context):
    return call_fn(evaluate_response, event)
