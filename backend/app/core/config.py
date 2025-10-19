from pydantic_settings import BaseSettings
from typing import Literal

class Settings(BaseSettings):
    """
    Loads application settings from environment variables.
    """
    # Vector DB settings
    VECTOR_DB: Literal["FAISS", "PINECONE"] = "FAISS"
    LOCAL_FAISS_INDEX_PATH: str = "../notebooks/artifacts/faiss_index"
    
    # Pinecone settings
    PINECONE_API_KEY: str | None = None
    PINECONE_ENVIRONMENT: str | None = None
    PINECONE_INDEX_NAME: str = "furnifindr"
    
    # Embedding model
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"
    
    # Generative AI model
    OPENAI_API_KEY: str | None = None
    
    # Data file path
    DATA_FILE_PATH: str = "app/data_ingestion/sample_data.csv"

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

# Create a single settings instance to be imported by other modules
settings = Settings()