# Import libraries

from ai.chat.apis import call_add_error_details_api
from ai.chat.error_details_exception import capture_error_details
from ai.common.constants import CONNECTION_STRING
from ai.llms.constants import (
    CHUNK_SIZE_LIMIT,
    COLLECTION_NAME,
    EMBEDDINGS_FUNCTION,
    MAX_CHUNK_OVERLAP,
)
from common.envs import get_secret_value_from_secret_manager, logger
from dotenv import load_dotenv
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Import local modules
from langchain.vectorstores.pgvector import PGVector
from langchain_community.document_loaders import (
    Docx2txtLoader,
    PyPDFLoader,
    UnstructuredMarkdownLoader,
)

# Load environment variables
load_dotenv()

# Define global constants
OPENAI_API_KEY = get_secret_value_from_secret_manager("OPENAI_API_KEY")

# PostgreSQL credentials
pg_credentials = {
    "dbname": get_secret_value_from_secret_manager("DATABASE_NAME"),
    "user": get_secret_value_from_secret_manager("DATABASE_USER"),
    "password": get_secret_value_from_secret_manager("DATABASE_PASS"),
    "host": get_secret_value_from_secret_manager("DATABASE_HOST"),
    "port": get_secret_value_from_secret_manager("DATABASE_PORT"),
}


def fetch_data_from_source(file_path, s3_url):
    """Get data from either PostgreSQL, or read a file based on FORMAT.

    Returns:
        list: A list of documents to be processed.
    """
    split_docs = []
    error = None
    try:
        logger.info("File Format Enabled")
        split_docs, error_info = get_splits_of_different_types_of_format(
            file_path, s3_url
        )
        logger.info(f"error_info.................{error_info}")
        logger.info(f"file_path.................{file_path}")
    except Exception as e:
        error_info = capture_error_details(e)
        call_add_error_details_api(user_input=None, error=error_info)
        logger.error(f"Failed to fetch data: {e}")
        error = str(e)
    return split_docs, error


def get_splits_of_different_types_of_format(file_path, s3_url):
    """Function that processes different file formats and splits their content.

    Returns:
        list: A list of split documents to be processed.
    """
    split_docs = []
    FORMAT = file_path.split(".")[-1]
    logger.info(f"FORMAT.................{FORMAT}")

    def split_text_unstructured(text):
        document = Document(page_content=str(text), metadata={"source": s3_url})
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE_LIMIT,
            chunk_overlap=MAX_CHUNK_OVERLAP,
        )
        return text_splitter.split_documents([document])

    if FORMAT == "md":
        loader = UnstructuredMarkdownLoader(f"{file_path}", mode="single")
        text, error_info = text_splitter(loader)

    elif FORMAT == "pdf":
        loader = PyPDFLoader(f"{file_path}")
        text, error_info = text_splitter(loader)

    elif FORMAT in ["docx"]:
        loader = Docx2txtLoader(f"{file_path}")
        text, error_info = text_splitter(loader)

    logger.info(f"text.......{text}, error_info...{error_info}")
    if text:
        split_docs = split_text_unstructured(text)

        PGVector.from_documents(
            embedding=EMBEDDINGS_FUNCTION,
            documents=split_docs,
            collection_name=COLLECTION_NAME,
            connection_string=CONNECTION_STRING,
        )
        logger.info(
            f"{len(split_docs)} documents inserted into the database successfully."
        )
        return split_docs, error_info

    elif error_info is not None:
        logger.error(f"Error info: {error_info}")
        return split_docs, error_info


def insert_data_into_vector_db(file_path, s3_url):
    """
    Main function to get data from the source, create embeddings, and insert them into the database.
    """
    output = None
    logger.info("Embedding Started...")
    logger.info(f"Collection Name: {COLLECTION_NAME}")
    error_info = fetch_data_from_source(file_path, s3_url)
    if error_info:
        output = f"Embedding failed with the error - {error_info}"
        logger.error(output)
    elif error_info is None:
        output = "Embedding Completed..."
        logger.info(output)

    return output


def text_splitter(loader):
    try:
        error_info = None
        text = loader.load_and_split()
        if text:
            logger.info(f"Text using UnstructuredWordDocumentLoader{text}")
            return text, error_info
    except Exception as e:
        error_info = capture_error_details(e)
        call_add_error_details_api(user_input=None, error=error_info)
        logger.info(f"Failed to process Word document: {e}")
        return text, error_info
