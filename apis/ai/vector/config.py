from ai.common.constants import CONNECTION_STRING
from ai.llms.constants import COLLECTION_NAME, EMBEDDINGS_FUNCTION
from langchain.vectorstores.pgvector import PGVector


def get_vector_store():
    """
    Creates and returns a vector store for storing product embeddings.

    Returns:
    PGVector: The vector store instance.
    """
    # PGVector
    vector_store = PGVector(
        embedding_function=EMBEDDINGS_FUNCTION,
        collection_name=COLLECTION_NAME,
        connection_string=CONNECTION_STRING,
    )
    return vector_store


def get_current_file_vector_store(collection_name_check):
    """
    Creates and returns a vector store for storing product embeddings.

    Returns:
    PGVector: The vector store instance.
    """
    # PGVector
    vector_store = PGVector(
        embedding_function=EMBEDDINGS_FUNCTION,
        collection_name=collection_name_check,
        connection_string=CONNECTION_STRING,
    )
    return vector_store
