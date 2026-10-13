from chromadb.utils import embedding_functions

EMBEDDING_MODEL = "all-MiniLM-L6-v2"

def get_embedding_function():
    return embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBEDDING_MODEL
    )