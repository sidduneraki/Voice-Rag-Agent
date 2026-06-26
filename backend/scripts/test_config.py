import sys
sys.path.insert(0, ".")
from app.core.config import get_settings
from app.core.logger import logger

if __name__ == "__main__":
    settings = get_settings()
    logger.info(f"LLM provider: {settings.LLM_PROVIDER}")
    logger.info(f"Model: {settings.GROQ_MODEL}")
    logger.info(f"VectorDB: {settings.VECTORDB_PROVIDER}")
    logger.info(f"Embedding: {settings.EMBEDDING_MODEL}")
    logger.success("Config loaded successfully!")

