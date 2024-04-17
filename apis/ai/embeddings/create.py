# Import libraries

from ai.common.constants import CONNECTION_STRING
from ai.llms.constants import (
    CHUNK_SIZE_LIMIT,
    COLLECTION_NAME,
    EMBEDDINGS_FUNCTION,
    MAX_CHUNK_OVERLAP,
)
from common.envs import get_secret_value_from_secret_manager, logger
from dotenv import load_dotenv
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.text_splitter import CharacterTextSplitter

# Import local modules
from langchain.vectorstores.pgvector import PGVector
from langchain_community.document_loaders import (
    PyPDFLoader,
    UnstructuredWordDocumentLoader,
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


def fetch_data_from_source(file_path, source_column=None):
    """Get data from either PostgreSQL, or read a file based on FORMAT.

    Returns:
        list: A list of documents to be processed.
    """
    split_docs = []
    error = ""
    try:
        logger.info("File Format Enabled")
        split_docs = get_splits_of_different_types_of_format(file_path, source_column)
    except DataFetchException as ex:
        logger.error(f"Failed to fetch data: {ex}")
        error = str(ex)
    return split_docs, error


def get_splits_of_different_types_of_format(file_path, source_column=None):
    """Function that processes different file formats and splits their content.

    Returns:
        list: A list of split documents to be processed.
    """

    split_docs = []
    FORMAT = file_path.split(".")[-1]
    if FORMAT == "md":
        loader = UnstructuredMarkdownLoader(f"./{file_path}", mode="single")
        docs = loader.load_and_split()
        text_splitter = CharacterTextSplitter(
            chunk_size=CHUNK_SIZE_LIMIT, chunk_overlap=MAX_CHUNK_OVERLAP
        )
        split_docs = text_splitter.split_documents(docs)
        
    elif FORMAT == "pdf":
        loader = PyPDFLoader(file_path)
        docs = loader.load_and_split()
        text_splitter = CharacterTextSplitter(
            chunk_size=CHUNK_SIZE_LIMIT, chunk_overlap=MAX_CHUNK_OVERLAP
        )
        logger.info("text splitter", text_splitter)
        split_docs = text_splitter.split_documents(docs)
        print("split", split_docs)
    elif FORMAT in ["doc", "docx"]:
        loader = UnstructuredWordDocumentLoader(file_path, mode="single")
        docs = loader.load_and_split()
        separator=","
        text_splitter = CharacterTextSplitter(
            separator=separator, chunk_size=CHUNK_SIZE_LIMIT, chunk_overlap=MAX_CHUNK_OVERLAP
        )
        split_docs = text_splitter.split_documents(docs)
    else:
        raise InvalidFileFormat(f"Invalid file format - {FORMAT}")
    return split_docs


def insert_data_into_vector_db(file_path, source_column=None):
    """
    Main function to get data from the source, create embeddings, and insert them into the database.
    """
    output = None
    logger.info("Embedding Started...")
    logger.info(f"Collection Name: {COLLECTION_NAME}")
    split_docs, err = fetch_data_from_source(file_path, source_column)

    PGVector.from_documents(
        embedding=EMBEDDINGS_FUNCTION,
        documents=split_docs,
        collection_name=COLLECTION_NAME,
        connection_string=CONNECTION_STRING,
    )
    if err:
        output = f"Embedding failed with the error - {err}"
        logger.error(output)
    else:
        output = "Embedding Completed..."
        logger.info(output)

    return output
