import json
import time
import traceback

from ai.chat.apis import call_add_error_details_api, call_write_to_db_api
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
from ai.vector.config import get_vector_store
from common.envs import get_secret_value_from_secret_manager
from dotenv import load_dotenv

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
    # logging.error(f"System Error for user {user_id}: {traceback.format_exc().strip()}")
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
    toggle = request.get(ChatAPIRequestParameters.Toggle.value, "on")
    user_input = get_user_input(request)
    time_stamp = request.get(ChatAPIRequestParameters.TIME_STAMP.value, None)
    message_log = request.get(ChatAPIRequestParameters.MESSAGE_LOG.value, [])

    return (
        start_time,
        user_input,
        time_stamp,
        message_log,
        toggle,
    )


def handle_user_query(request, client=None, connection_id=None):
    def process_response(
        user_input, message_log, vector_store, client, connection_id, toggle
    ):
        (
            valid_query,
            raw_prompt,
            bot_response,
            source_documents,
            system_cost,
        ) = GenerateResponse(INITIAL_ROW, vector_store).main(
            user_input, message_log, client, connection_id, toggle
        )

        return valid_query, raw_prompt, bot_response, source_documents, system_cost

    (
        start_time,
        user_input,
        time_stamp,
        message_log,
        toggle,
    ) = process_request(request)

    try:
        validation_error = validate_user_input(user_input, message_log)
        if validation_error:
            handle_validation_error(validation_error, client, connection_id)
            return

        INITIAL_ROW[0] = user_input

        vector_store = get_vector_store()

        (
            valid_query,
            raw_prompt,
            bot_response,
            source_documents,
            system_cost,
        ) = process_response(
            user_input, message_log, vector_store, client, connection_id, toggle
        )

        response_time = time.time() - start_time
        record = [
            user_input,
            raw_prompt,
            bot_response,
            response_time,
            system_cost,
            time_stamp,
            json.dumps(message_log, indent=2),
            f"System Docs: {str(source_documents)},",
            toggle,
        ]

        row_id = call_write_to_db_api(record, None)

        stream_response(
            {ChatAPIResponseParameters.ID.value: row_id}, client, connection_id
        )

        if valid_query:
            message_log.append(user_input)
            message_log.append(bot_response)

        message_log = message_log[-4:]
        stream_response(
            {ChatAPIResponseParameters.MESSAGE_LOG.value: message_log},
            client,
            connection_id,
        )

    except Exception:
        handle_system_error(user_input, client, connection_id)
