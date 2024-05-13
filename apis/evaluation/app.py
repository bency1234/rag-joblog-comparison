from http import HTTPStatus

from common.app_utils import get_app
from common.chatbot import EvaluationScores
from common.db import db
from common.envs import logger
from common.lambda_utils import call_fn
from flask_sqlalchemy import pagination

app = get_app(db)


def get_feedback_evaluation(*args):
    with app.app_context():
        try:
            event = args[0]
            query_params = event.get("queryStringParameters", {})
            if query_params:
                page = int(query_params.get("page", 1))
                limit = int(query_params.get("size", 10))

                paginate: pagination = EvaluationScores.query.paginate(
                    page=page, per_page=limit, error_out=False
                )
                data = paginate.items
                result = [
                    {
                        "user_input": item.user_input,
                        "final_response": item.final_response,
                        "feedback": item.feedback,
                        "faithfulness": "{:.2f}".format(item.faithfulness),
                        "answer_relevancy": "{:.2f}".format(item.answer_relevancy),
                        "context_utilization": "{:.2f}".format(
                            item.context_utilization
                        ),
                        "date": item.created_at.strftime("%Y-%m-%d"),
                    }
                    for item in data
                ]

                total_count = paginate.total

                return {
                    "message": "success",
                    "total_count": total_count,
                    "data": result,
                }, HTTPStatus.OK

        except Exception as e:
            logger.error(f"An error occurred: {str(e)}", exc_info=True)
            return {
                "message": "An error occurred",
                "errors": str(e),
            }, HTTPStatus.INTERNAL_SERVER_ERROR


def lambda_handler(*args):
    event = args[0]
    return call_fn(get_feedback_evaluation, event)
