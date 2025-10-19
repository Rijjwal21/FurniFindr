import pandas as pd
import ast
import re
from typing import List, Dict, Any
from langchain_community.docstore.document import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_pinecone import Pinecone
from pinecone import Pinecone as PineconeClient, ServerlessSpec
from app.core.config import settings

def clean_price(price_str: str) -> float:
    """Removes '$' and ',' from price string and converts to float."""
    if not isinstance(price_str, str):
        return 0.0
    try:
        return float(re.sub(r"[$,]", "", price_str))
    except (ValueError, TypeError):
        return 0.0

def safe_literal_eval(val: str) -> List[str]:
    """Safely evaluates a string representation of a list."""
    if not isinstance(val, str):
        return []
    try:
        return ast.literal_eval(val)
    except (ValueError, SyntaxError):
        return [val]  # Return as list with the original string if eval fails

def create_documents(df: pd.DataFrame) -> List[Document]:
    """Converts DataFrame rows into LangChain Document objects."""
    documents = []
    for _, row in df.iterrows():
        # Create a combined text for embedding
        text_to_embed = f"Title: {row['title']}\n"
        text_to_embed += f"Brand: {row['brand']}\n"
        text_to_embed += f"Description: {row['description']}\n"
        text_to_embed += f"Categories: {', '.join(row['categories_clean'])}\n"
        text_to_embed += f"Material: {row['material']}\n"
        text_to_embed += f"Color: {row['color']}"
        
        # Store all other data as metadata
        metadata = row.to_dict()
        # Convert lists to strings for FAISS/metadata compatibility if needed
        metadata['categories'] = str(metadata['categories_clean'])
        metadata['images'] = str(metadata['images_clean'])
        
        documents.append(
            Document(page_content=text_to_embed, metadata=metadata)
        )
    return documents

def main():
    """Main ingestion function."""
    print(f"Loading data from {settings.DATA_FILE_PATH}...")
    df = pd.read_csv(settings.DATA_FILE_PATH)
    
    # --- Data Cleaning ---
    df = df.fillna("")
    df['price_clean'] = df['price'].apply(clean_price)
    df['categories_clean'] = df['categories'].apply(safe_literal_eval)
    df['images_clean'] = df['images'].apply(safe_literal_eval)
    
    # Keep original string versions for metadata
    df['price'] = df['price'].astype(str)
    
    # Convert all other columns to string to ensure compatibility
    for col in df.columns:
        if col not in ['price_clean', 'categories_clean', 'images_clean']:
            df[col] = df[col].astype(str)

    print(f"Creating {len(df)} documents...")
    documents = create_documents(df)
    
    print("Generating embeddings... This may take a moment.")
    embeddings = HuggingFaceEmbeddings(
        model_name=settings.EMBEDDING_MODEL_NAME,
        model_kwargs={'device': 'cpu'} # Use CPU for local demo
    )
    
    if settings.VECTOR_DB == "FAISS":
        print("Initializing FAISS index...")
        db = FAISS.from_documents(documents, embeddings)
        db.save_local(settings.LOCAL_FAISS_INDEX_PATH)
        print(f"FAISS index created and saved to {settings.LOCAL_FAISS_INDEX_PATH}")
        
    elif settings.VECTOR_DB == "PINECONE":
        if not settings.PINECONE_API_KEY or not settings.PINECONE_ENVIRONMENT:
            raise ValueError("PINECONE_API_KEY and PINECONE_ENVIRONMENT must be set in .env")
        
        print("Initializing Pinecone client...")
        pc = PineconeClient(api_key=settings.PINECONE_API_KEY)
        
        # Create index if it doesn't exist
        if settings.PINECONE_INDEX_NAME not in pc.list_indexes().names():
            print(f"Creating Pinecone index: {settings.PINECONE_INDEX_NAME}...")
            # Get embedding dimension
            sample_embedding = embeddings.embed_query("sample text")
            dimension = len(sample_embedding)
            
            pc.create_index(
                name=settings.PINECONE_INDEX_NAME,
                dimension=dimension,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region=settings.PINECONE_ENVIRONMENT
                )
            )
            print("Index created.")
        
        print("Uploading documents to Pinecone...")
        Pinecone.from_documents(
            documents,
            embeddings,
            index_name=settings.PINECONE_INDEX_NAME
        )
        print("Documents uploaded to Pinecone.")

    print("Data ingestion complete.")

if __name__ == "__main__":
    main()