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
from langchain.text_splitter import CharacterTextSplitter

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
        print("file_path.................", file_path)
    except Exception as ex:
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
    print("FORMAT.................", FORMAT)

    def split_text_unstructured(text, separator=","):
        document = Document(page_content=str(text), metadata={"source": file_path})
        text_splitter = CharacterTextSplitter(
            separator=separator,
            chunk_size=CHUNK_SIZE_LIMIT,
            chunk_overlap=MAX_CHUNK_OVERLAP,
        )
        return text_splitter.split_documents([document])

    if FORMAT == "md":
        text = load_and_split_md(file_path)

    elif FORMAT == "pdf":
        text = load_and_split_pdf(file_path)

    elif FORMAT in ["docx"]:
        text = load_and_split_word(file_path)
        print("text...................", text)

    elif FORMAT == "doc":
        text = subprocess.run(["antiword", file_path], capture_output=True, text=True)
        print(text)

    if text:
        split_docs = split_text_unstructured(text)
        collection = "joblog"  # get_collection_name(auth_id, workspace_id, is_shared)

        PGVector.from_documents(
            embedding=EMBEDDINGS_FUNCTION,
            documents=split_docs,
            collection_name=collection,
            connection_string=CONNECTION_STRING,
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
    err = fetch_data_from_source(file_path, source_column)
    if err:
        output = f"Embedding failed with the error - {err}"
        logger.error(output)
    else:
        output = "Embedding Completed..."
        logger.info(output)

    return output


def load_and_split_md(file_name):
    try:
        loader = UnstructuredMarkdownLoader(f"./{file_name}", mode="single")
        text = loader.load_and_split()
        if text:
            print("Text using UnstructuredWordDocumentLoader", text)
            return text
        else:
            raise ValueError("Empty text returned by UnstructuredWordDocumentLoader")
    except Exception as e:
        print(f"Failed to process markdown document: {e}", e)
    return None


def load_and_split_pdf(file_name):
    try:
        # use PyPDFLoader if PDFMinerLoader also fails
        loader = PyPDFLoader(f"./{file_name}")
        print("Processing with PyPDFLoader", file_name)
        text = loader.load_and_split()
        if text:
            print("Text using PyPDFLoader", text)
            return text
        else:
            raise ValueError("Empty text returned by PyPDFLoader")
    except Exception as e:
        print(f"PyPDFLoader failed: {e}", e)
    return None


def load_and_split_word(file_name):
    try:
        loader = Docx2txtLoader(f"./{file_name}")
        text = loader.load_and_split()
        if text:
            print("Text using UnstructuredWordDocumentLoader", text)
            return text
        else:
            raise ValueError("Empty text returned by UnstructuredWordDocumentLoader")
    except Exception as e:
        print(f"Failed to process Word document: {e}", e)
    return None
