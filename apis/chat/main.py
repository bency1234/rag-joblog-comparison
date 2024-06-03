import json
import os
import time
import traceback

import psycopg2
from ai.chat.apis import call_add_error_details_api, call_write_to_db_api
from ai.chat.error_details_exception import capture_error_details
from ai.chat.logic import GenerateResponse
from ai.chat.validation import validate_user_input
from ai.common.api_validations import (
    ChatAPIRequestParameters,
    ChatAPIResponseParameters,
    ChatAPIValidationMessage,
    ErrorType,
    StatusCode,
)
from ai.common.utils.debug import INITIAL_ROW
from ai.common.utils.stream import construct_bot_response, stream_response
from ai.llms.constants import COLLECTION_NAME
from ai.vector.config import get_current_file_vector_store, get_vector_store
from common.chatbot import Conversation
from common.db import db
from common.envs import get_secret_value_from_secret_manager, logger
from dotenv import load_dotenv
from notify.app import check_collection_name

# Load environment variables
load_dotenv()

VERBOSE = get_secret_value_from_secret_manager("VERBOSE")


def stream_word_by_word(words, client, connection_id):
    for word in words.split(" "):
        stream_response(construct_bot_response(f"{word}  "), client, connection_id)


def handle_validation_error(validation_error, client, connection_id):
    stream_response(
        validation_error, client, connection_id, StatusCode.BAD_REQUEST.value, False
    )


def handle_system_error(user_input, client, connection_id):
    error_details = (
        f"Error Line: {traceback.format_exc().strip()}",
        ErrorType.SystemError.value,
    )
    call_add_error_details_api(user_input, error_details)
    stream_response(
        ChatAPIValidationMessage.SOMETHING_WENT_WRONG.get_message(),
        client,
        connection_id,
        status_code=StatusCode.INTERNAL_SERVER_ERROR.value,
        status=False,
    )


def get_user_input(request):
    user_input = request.get(ChatAPIRequestParameters.USER_INPUT.value, "H").strip()
    continue_chat = request.get(ChatAPIRequestParameters.CONTINUE_CHAT.value, False)
    return "Please continue" if continue_chat else user_input


def process_request(request):
    start_time = time.time()
    use_rag = request.get(ChatAPIRequestParameters.USE_RAG.value, True)
    user_input = get_user_input(request)
    time_stamp = request.get(ChatAPIRequestParameters.TIME_STAMP.value, None)
    message_log = request.get(ChatAPIRequestParameters.MESSAGE_LOG.value, [])
    collection_id = request.get(ChatAPIRequestParameters.CONVERSATION_ID.value, None)

    user_id = request.get(ChatAPIRequestParameters.USER_ID.value, None)
    logger.info(f"request: {request}")
    return (
        start_time,
        user_input,
        time_stamp,
        message_log,
        use_rag,
        collection_id,
        user_id,
    )


def handle_user_query(request, client=None, connection_id=None):
    def process_response(
        user_input,
        message_log,
        vector_store,
        client,
        connection_id,
        use_rag,
        collection_id,
    ):
        (
            valid_query,
            raw_prompt,
            bot_response,
            source_documents,
            system_cost,
        ) = GenerateResponse(INITIAL_ROW, vector_store).main(
            user_input, message_log, client, connection_id, use_rag, collection_id
        )

        return valid_query, raw_prompt, bot_response, source_documents, system_cost

    (
        start_time,
        user_input,
        time_stamp,
        message_log,
        use_rag,
        collection_id,
        user_id,
    ) = process_request(request)

    try:
        validation_error = validate_user_input(user_input, message_log)
        if validation_error:
            handle_validation_error(validation_error, client, connection_id)
            return

        INITIAL_ROW[0] = user_input
        collection_id, collection_name = check_collection_id_exist(
            collection_id, time_stamp, user_id, db
        )
        logger.info(
            f"collection_id: {collection_id}, collection_name: {collection_name}"
        )
        collection_name_check = "joblog_" + str(user_id) + "_" + str(collection_id)
        logger.info(f"collection_name_check: {collection_name_check}")
        exists = check_collection_name_exists(collection_name_check)

        logger.info(f"exists {exists}")
        if exists == False:
            logger.info("Entered Pre-Uploaded file")
            vector_store = get_vector_store()
        else:
            logger.info("Entered current-Uploaded file")
            vector_store = get_current_file_vector_store(collection_name_check)
        (
            valid_query,
            raw_prompt,
            bot_response,
            source_documents,
            system_cost,
        ) = process_response(
            user_input,
            message_log,
            vector_store,
            client,
            connection_id,
            use_rag,
            collection_id,
        )

        response_time = time.time() - start_time

        if valid_query:
            message_log.append(user_input)
            message_log.append(bot_response)

        message_log = message_log[-4:]

        record = [
            user_input,
            raw_prompt,
            bot_response,
            response_time,
            system_cost,
            time_stamp,
            json.dumps(message_log, indent=2),
            f"System Docs: {str(source_documents)},",
            use_rag,
        ]
        row_id = call_write_to_db_api(record, None)

        stream_response(
            {ChatAPIResponseParameters.ID.value: row_id},
            client,
            connection_id,
            collection_id,
        )

        stream_response(
            {
                ChatAPIResponseParameters.MESSAGE_LOG.value: message_log,
                "conversation_id": collection_id,
            },
            client,
            connection_id,
        )

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        error_info = capture_error_details(e)
        call_add_error_details_api(user_input=None, error=error_info)
        handle_system_error(user_input, client, connection_id)


conn = psycopg2.connect(
    host=os.environ.get(
        "PGVECTOR_HOST", get_secret_value_from_secret_manager("DATABASE_HOST")
    ),
    user=os.environ.get(
        "PGVECTOR_USER", get_secret_value_from_secret_manager("DATABASE_USER")
    ),
    password=os.environ.get(
        "PGVECTOR_PASSWORD", get_secret_value_from_secret_manager("DATABASE_PASS")
    ),
    database=os.environ.get(
        "PGVECTOR_DATABASE", get_secret_value_from_secret_manager("DATABASE_NAME")
    ),
)


def check_collection_name_exists(collection_name_check):
    try:
        # Connect to the PostgreSQL database
        query = "SELECT EXISTS (SELECT 1 FROM langchain_pg_collection WHERE name = %s)"
        with conn.cursor() as cursor:
            cursor.execute(query, (collection_name_check,))
            exists = cursor.fetchone()[0]
            return exists

    except Exception as e:
        error_info = capture_error_details(e)
        call_add_error_details_api(user_input=None, error=error_info)
        logger.info(f"An error occurred: {e}")


def check_collection_id_exist(collection_id, time_stamp, user_id, db):
    if not collection_id:
        new_conversation = Conversation()

        new_conversation.time_stamp = time_stamp
        new_conversation.user_id = user_id
        db.session.add(new_conversation)
        db.session.commit()

        new_conversation.collection_name = (
            "joblog_" + str(user_id) + "_" + str(new_conversation.id)
        )
        db.session.commit()
        collection_id = new_conversation.id
        collection_name = new_conversation.collection_name
    else:
        collection_name = COLLECTION_NAME
    return collection_id, collection_name
