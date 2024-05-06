# Import libraries
import subprocess

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
        logger.info(f"file_path.................{file_path}")
    except Exception as ex:
        logger.error(f"Failed to fetch data: {ex}")
        error = str(ex)
        logger.info("error occured here --------------------->>>>>>>>>>>>>>>>")
    return split_docs, error


def get_splits_of_different_types_of_format(file_path, source_column=None):
    """Function that processes different file formats and splits their content.

    Returns:
        list: A list of split documents to be processed.
    """

    split_docs = []
    FORMAT = file_path.split(".")[-1]
    logger.info(f"FORMAT.................{FORMAT}")

    def split_text_unstructured(text):
        document = Document(page_content=str(text), metadata={"source": file_path})
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE_LIMIT,
            chunk_overlap=MAX_CHUNK_OVERLAP,
        )
        return text_splitter.split_documents([document])

    if FORMAT == "md":
        text = load_and_split_md(file_path)

    elif FORMAT == "pdf":
        logger.info(
            "PDF Splitted ------------------------------->>>>>>>>>>>>>>>>>>>>@@@@@@@@@@@@@@@@@@@@@@@@@"
        )
        text = load_and_split_pdf(file_path)

    elif FORMAT in ["docx"]:
        text = load_and_split_word(file_path)
        logger.info(f"text.......{text}")

    elif FORMAT == "doc":
        text = subprocess.run(["antiword", file_path], capture_output=True, text=True)
        logger.info(f"text....{text}")

    if text:
        split_docs = split_text_unstructured(text)

        PGVector.from_documents(
            embedding=EMBEDDINGS_FUNCTION,
            documents=split_docs,
            collection_name=COLLECTION_NAME,
            connection_string=CONNECTION_STRING,
        )
        logger.info(
            f"{len(split_docs)} documents inserted into the database ------------------------------------>>>>>>>>>>>>>>>>>>>>>>>>>>"
        )
        return split_docs
    return False


def insert_data_into_vector_db(file_path, source_column=None):
    """
    Main function to get data from the source, create embeddings, and insert them into the database.
    """
    output = None
    logger.info("Embedding Started...")
    logger.info(f"Collection Name: {COLLECTION_NAME}")
    split_docs, err = fetch_data_from_source(file_path, source_column)
    logger.info("err here -------------------------=================>>>>>>>>>>")
    if err:
        output = f"Embedding failed with the error - {err}"
        logger.error(output)
    else:
        output = "Embedding Completed..."
        logger.info(output)

    return output


def load_and_split_md(file_name):
    try:
        loader = UnstructuredMarkdownLoader(f"{file_name}", mode="single")
        text = loader.load_and_split()
        if text:
            logger.info(f"Text using UnstructuredWordDocumentLoader {text}")
            return text
        else:
            raise ValueError("Empty text returned by UnstructuredWordDocumentLoader")
    except Exception as e:
        logger.info(f"Failed to process markdown document: {e}")
    return None


def load_and_split_pdf(file_name):
    try:
        loader = PyPDFLoader(f"{file_name}")
        logger.info(f"Processing with PyPDFLoader{file_name}")
        text = loader.load_and_split()
        if text:
            logger.info(f"Text using PyPDFLoader{text}")
            return text
        else:
            raise ValueError("Empty text returned by PyPDFLoader")
    except Exception as e:
        logger.info(f"PyPDFLoader failed: {e}")
    return None


def load_and_split_word(file_name):
    try:
        loader = Docx2txtLoader(f"{file_name}")
        text = loader.load_and_split()
        if text:
            logger.info(f"Text using UnstructuredWordDocumentLoader{text}")
            return text
        else:
            raise ValueError("Empty text returned by UnstructuredWordDocumentLoader")
    except Exception as e:
        logger.info(f"Failed to process Word document: {e}")
    return None
