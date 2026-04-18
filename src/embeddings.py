# embeddings.py
from chromadb.utils import embedding_functions

def get_embedding_functions():
    # Menggunakan model multilingual yang mendukung 50+ bahasa
    return embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="paraphrase-multilingual-MiniLM-L12-v2"
    )