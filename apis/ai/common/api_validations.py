from enum import Enum

MESSAGE_LENGTH = (
    500  # We are expecting user input message length should be 500 or less than that
)
MESSAGE_SET = 2  # Message will have User and System Message


class ErrorType(Enum):
    """Enumeration representing different types of errors"""

    ValidationError = "ValidationError"
    RateLimitError = "RateLimitError"
    SystemError = "SystemError"


class StatusCode(Enum):
    OK = 200
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    INTERNAL_SERVER_ERROR = 500
    SERVICE_UNAVAILABLE = 503
    RATE_LIMIT = 429


MESSAGE_LOG_STR = "message_log"
CONTINUE_CHAT_STR = "continue"
CONVERSATION_ID_STR = "conversation_id"


class ChatAPIRequestParameters(Enum):
    """Enumeration representing different request parameters of the Chat API"""

    USER_INPUT = "user_input"
    MESSAGE_LOG = MESSAGE_LOG_STR
    TIME_STAMP = "time_stamp"
    EMAIL = "email"
    USER_ID = "user_id"
    USE_RAG = "use_rag"
    CONTINUE_CHAT = CONTINUE_CHAT_STR
    CONVERSATION_ID = "conversation_id"


class ChatAPIResponseParameters(Enum):
    """Enumeration representing different response parameters of the Chat API"""

    MESSAGE = "message"
    RESPONSE = "response"
    MESSAGE_LOG = MESSAGE_LOG_STR
    ID = "id"
    TIME_LEFT = "time_left"
    STATUS = "status"
    STATUS_CODE = "status_code"
    CONTINUE_CHAT = CONTINUE_CHAT_STR


class ChatAPIValidationMessage(Enum):
    """Enumeration representing validation messages for the Chat API"""

    REQUIRED_PARAMETER = (
        f"{ChatAPIRequestParameters.USER_INPUT.value} / {ChatAPIRequestParameters.TIME_STAMP.value} / {ChatAPIRequestParameters.EMAIL.value} / {ChatAPIRequestParameters.USER_ID.value} parameter is required",
        ErrorType.ValidationError.value,
    )

    MESSAGE_LOG_SHOULD_BE_OF_TYPE_LIST = (
        f"{ChatAPIRequestParameters.MESSAGE_LOG.value} should be of type list",
        ErrorType.ValidationError.value,
    )

    MESSAGE_LOG_SHOULD_BE_OF_EVEN_LENGTH = (
        f"{ChatAPIRequestParameters.MESSAGE_LOG.value} should be of length even number",
        ErrorType.ValidationError.value,
    )

    TIME_STAMP_SHOULD_BE_IN_EXPECTED_FORMAT = (
        f"{ChatAPIRequestParameters.TIME_STAMP.value} is not in expected format - Example: 2023-04-27 08:16:07",
        ErrorType.ValidationError.value,
    )

    USER_INPUT_SHOULD_BE_IN_EXPECTED_LENGTH = (
        f"Please type a message that is less than {MESSAGE_LENGTH} characters.",
        ErrorType.ValidationError.value,
    )

    OPEN_AI_API_RATE_LIMIT_ERROR = (
        "OpenAI API Rate Limit Error",
        ErrorType.RateLimitError.value,
    )

    SOMETHING_WENT_WRONG = (
        "We are unable to serve your request at this time",
        ErrorType.SystemError.value,
    )

    def get_all(self):
        return self.value

    def get_message(self):
        return self.value[0]
