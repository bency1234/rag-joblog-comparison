from enum import Enum

from common.envs import get_secret_value_from_secret_manager
from langchain_openai import OpenAIEmbeddings

################################# Open AI Constants starts here #################################
EXAMPLES_TITLE = "Examples:"
HUMAN = "User: "
BOT = "System: "

OPENAI_API_KEY = get_secret_value_from_secret_manager("OPENAI_API_KEY")
LLM = "OPENAI"


class OpenAIEmbeddingModels(Enum):
    ADA = ("text-embedding-ada-002", 0.0004)


class OpenAITextLLM(Enum):
    BABBAGE = ("text-babbage-001", 0.0005)
    CURIE = ("text-curie-001", 0.0020)
    DAVINCI = ("text-davinci-003", 0.0200)
    TURBO_INSTRUCT = ("gpt-3.5-turbo-instruct", 0.003)


class OpenAIChatLLM(Enum):
    TURBO = ("gpt-3.5-turbo", 0.0015, 0.002)
    TURBO_16k = ("gpt-3.5-turbo-16k", 0.003, 0.004)
    GPT4_8K = ("gpt-4", 0.03, 0.06)
    GPT4_32k = ("gpt-4-32k", 0.06, 0.12)
    GPT4_TURBO = ("gpt-4-turbo-preview", 0.01, 0.03)


COST_PER_TOKENS = 1000
MAX_RETRIES = 2
TEMPERATURE = 0
TOKENS = 400
TAG_TOKENS = 100
TYPE_TOKENS = 50
TURBO_16k = "gpt-3.5-turbo-16k"
DAVINCI = "text-davinci-003"
MODEL, TEMPERATURE, TOKENS = DAVINCI, 0, 300
TURBO_16k_COST = 0.003

# Embeddings
CHUNK_SIZE_LIMIT = 2000
MAX_CHUNK_OVERLAP = 100

BATCH_SIZE = 100
UNITS = 1000
################################# Open AI Constants ends here #################################


#################################  LLM Constants starts here #################################
SYSTEM_MODEL, SYSTEM_INPUT_COST, SYSTEM_OUTPUT_COST = OpenAIChatLLM.GPT4_TURBO.value
#################################  LLM Constants ends here #################################

#################################  Embeddings Constants starts here #################################

EMBEDDINGS_FUNCTION = OpenAIEmbeddings(
    openai_api_key=OPENAI_API_KEY, max_retries=MAX_RETRIES
)


COLLECTION_NAME = "openai_embeddings"
SCORE_THRESHOLD = 0.3
NUMBER_OF_DOCUMENTS_TO_BE_RETURNED = 4
SEARCH_KWARGS = {
    "score_threshold": SCORE_THRESHOLD,
    "k": NUMBER_OF_DOCUMENTS_TO_BE_RETURNED,
}
SEARCH_TYPE = "similarity_score_threshold"
#################################  Embeddings Constants ends here #################################
