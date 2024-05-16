"""
This script is to update the metrics in the chatbot_metrics table.
"""
from http import HTTPStatus

from common.app_utils import read_database_url_from_secret_manager
from common.chatbot import ChatbotData, ChatbotMetrics, Feedback
from common.db import db
from common.envs import logger
from flask import Flask, json
from job_utils import create_session
from sqlalchemy import func, or_

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = read_database_url_from_secret_manager()
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)


def get_chatbot_data_records(session, time_stamp_of_last_record):
    """
    Retrieve chatbot data records from the database.
    Args:
        session: The database session.
        time_stamp_of_last_record: The timestamp of the last record.
    Returns:
        list: A list of chatbot data records.
    """
    query = session.query(
        ChatbotData.id,
        ChatbotData.response_time,
        ChatbotData.created_at,
        ChatbotData.exchange_cost,
    )
    if time_stamp_of_last_record:
        query = query.filter(ChatbotData.created_at > time_stamp_of_last_record)
    return query.all()


def get_chatbot_feedback_records(time_stamp_of_last_record):
    """
    Retrieve chatbot feedback records from the database.
    Args:
        session: The database session.
        time_stamp_of_last_record: The timestamp of the last record.
    Returns:
        list: A list of chatbot feedback records.
    """
    query = db.session.query(
        Feedback.created_at,
        func.count()
        .filter(
            or_(
                Feedback.response_status == "true",
                Feedback.response_status == "pending",
            )
        )
        .label("response_accepted_count"),
        func.count()
        .filter(Feedback.response_status == "false")
        .label("response_declined_count"),
    )
    if time_stamp_of_last_record:
        query = query.filter(Feedback.created_at > time_stamp_of_last_record)
    return query.group_by(Feedback.created_at).all()


def lambda_handler(*args):
    with app.app_context():
        session = create_session()
        try:
            # Fetch the latest timestamp already processed
            latest_entry = (
                session.query(ChatbotMetrics)
                .order_by(ChatbotMetrics.time_stamp.desc())
                .first()
            )
            latest_time_stamp = latest_entry.time_stamp if latest_entry else None
            if latest_time_stamp:
                logger.info(f"Latest timestamp processed:{latest_time_stamp}")
            # Fetch new records since the last timestamp processed
            chatbot_data_records = get_chatbot_data_records(session, latest_time_stamp)
            feedback_data_records = get_chatbot_feedback_records(latest_time_stamp)
            # Check if there are new records to process
            if chatbot_data_records or feedback_data_records:
                # This function will aggregate data only if there are new records since the last timestamp
                aggregated_data = aggregate_all_data(
                    chatbot_data_records, feedback_data_records
                )
                insert_aggregated_data(session, aggregated_data, latest_time_stamp)
                session.commit()
                logger.info("New data processed and stored.")
            else:
                logger.info("No new data to process.")
            return {
                "statusCode": HTTPStatus.OK.value,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"response": "success"}),
            }
        except Exception as e:
            session.rollback()
            logger.info(f"Error processing data: {e}")
            return {
                "statusCode": HTTPStatus.INTERNAL_SERVER_ERROR.value,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"response": "failure", "error": str(e)}),
            }


def aggregate_all_data(chatbot_data_records, feedback_data_records):
    aggregated_data = {
        "exchange_count": 0,
        "exchange_ids": [],
        "response_accepted_count": 0,
        "response_declined_count": 0,
        "response_time": 0,
        "exchange_cost": 0.0,
        "latest_created_at": None,  # Initialize with None
    }

    latest_timestamp = None
    for id, response_time, created_at, exchange_cost in chatbot_data_records:
        aggregated_data["exchange_count"] += 1
        aggregated_data["exchange_ids"].append(id)
        aggregated_data["response_time"] += response_time
        aggregated_data["exchange_cost"] += float(exchange_cost)
        if not latest_timestamp or created_at > latest_timestamp:
            latest_timestamp = created_at  # Update the latest timestamp

    for (
        created_at,
        response_accepted_count,
        response_declined_count,
    ) in feedback_data_records:
        aggregated_data["response_accepted_count"] += response_accepted_count
        aggregated_data["response_declined_count"] += response_declined_count
        if not latest_timestamp or created_at > latest_timestamp:
            latest_timestamp = created_at  # Update the latest timestamp

    aggregated_data[
        "latest_created_at"
    ] = latest_timestamp  # Assign the latest timestamp to the dictionary
    return aggregated_data


def insert_aggregated_data(session, aggregated_data, latest_time_stamp):
    """
    Insert aggregated data into the ChatbotMetrics table only if the data is newer based on the timestamp.
    Args:
        session (Session): Database session.
        aggregated_data (dict): The aggregated data to insert.
        latest_time_stamp (datetime): The timestamp of the last record processed.
    Returns:
        None
    """
    if not aggregated_data or aggregated_data["latest_created_at"] is None:
        logger.info("No new data to process.")
        return

    # Proceed with insertion if latest_time_stamp is None or the new data timestamp is greater
    if (
        latest_time_stamp is None
        or aggregated_data["latest_created_at"] > latest_time_stamp
    ):
        new_record = ChatbotMetrics(
            exchange_count=aggregated_data["exchange_count"],
            exchange_ids=",".join(map(str, aggregated_data["exchange_ids"])),
            response_accepted_count=aggregated_data["response_accepted_count"],
            response_declined_count=aggregated_data["response_declined_count"],
            response_time=aggregated_data["response_time"],
            exchange_cost=aggregated_data["exchange_cost"],
            time_stamp=aggregated_data[
                "latest_created_at"
            ],  # Using the timestamp from the new data
        )
        session.add(new_record)
        session.commit()
        logger.info("New data inserted successfully.")
    else:
        logger.info(
            "No new data needs processing as it is not newer than the last processed data."
        )
