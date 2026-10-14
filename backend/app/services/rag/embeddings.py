from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2

EMBEDDING_MODEL = "all-MiniLM-L6-v2"


def get_embedding_function():
    return ONNXMiniLM_L6_V2()