from app.vectordb.base import BaseVectorDB
from app.core.config import get_settings
from app.core.logger import logger

def get_vectordb(collection_name: str = "default") -> BaseVectorDB:
    provider = get_settings().VECTORDB_PROVIDER.lower()
    logger.info(f"Loading VectorDB provider: {provider}")

    if provider == "chroma":
        from app.vectordb.chroma_db import ChromaVectorDB
        return ChromaVectorDB(collection_name=collection_name)
    elif provider == "qdrant":
        from app.vectordb.qdrant_db import QdrantVectorDB
        return QdrantVectorDB()
    else:
        raise ValueError(f"Unknown VectorDB provider: {provider}")
