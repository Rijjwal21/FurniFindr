from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_pinecone import Pinecone
from langchain_core.vectorstores import VectorStoreRetriever
from app.core.config import settings
import os

# --- Global Cache ---
# We cache the embeddings model and vector store in memory
# to avoid reloading them on every API request.
_embeddings = None
_vector_store = None
# --------------------

def get_embedding_model() -> HuggingFaceEmbeddings:
    """
    Loads and caches the sentence-transformer embedding model.
    """
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL_NAME,
            model_kwargs={'device': 'cpu'} # Use CPU for local demo
        )
    return _embeddings

def get_vector_store():
    """
    Loads and caches the vector store (FAISS or Pinecone)
    based on the environment settings.
    This function is called on API startup.
    """
    global _vector_store
    if _vector_store is not None:
        return _vector_store

    print(f"Initializing vector store: {settings.VECTOR_DB}")
    embeddings = get_embedding_model()
    
    if settings.VECTOR_DB == "FAISS":
        if not os.path.exists(settings.LOCAL_FAISS_INDEX_PATH):
            raise FileNotFoundError(
                f"FAISS index not found at {settings.LOCAL_FAISS_INDEX_PATH}. "
                "Did you run the ingestion script? (backend/app/data_ingestion/ingest.py)"
            )
        print(f"Loading FAISS index from {settings.LOCAL_FAISS_INDEX_PATH}...")
        _vector_store = FAISS.load_local(
            settings.LOCAL_FAISS_INDEX_PATH,
            embeddings,
            allow_dangerous_deserialization=True # Required for FAISS
        )
        print("FAISS index loaded.")
        
    elif settings.VECTOR_DB == "PINECONE":
        if not settings.PINECONE_API_KEY:
            raise ValueError("PINECONE_API_KEY must be set in .env for Pinecone")
        
        print(f"Connecting to Pinecone index: {settings.PINECONE_INDEX_NAME}...")
        _vector_store = Pinecone.from_existing_index(
            index_name=settings.PINECONE_INDEX_NAME,
            embedding=embeddings
        )
        print("Connected to Pinecone.")
        
    else:
        raise ValueError(f"Unknown VECTOR_DB type: {settings.VECTOR_DB}")
        
    return _vector_store

def get_retriever(top_k: int = 5) -> VectorStoreRetriever:
    """
    Gets a retriever from the cached vector store.
    This is what the recommendation service will use.
    """
    db = get_vector_store()
    return db.as_retriever(search_kwargs={"k": top_k})