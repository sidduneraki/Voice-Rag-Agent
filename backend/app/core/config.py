from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache

class Settings(BaseSettings):
    # LLM
    LLM_PROVIDER: str = Field(default="groq")
    GROQ_API_KEY: str = Field(default="")
    GROQ_MODEL: str = Field(default="llama-3.1-8b-instant")
    OLLAMA_BASE_URL: str = Field(default="http://localhost:11434")
    OLLAMA_MODEL: str = Field(default="llama3.2")

    # Vector DB
    VECTORDB_PROVIDER: str = Field(default="chroma")
    CHROMA_PATH: str = Field(default="./data/chroma_db")
    QDRANT_URL: str = Field(default="http://localhost:6333")
    QDRANT_COLLECTION: str = Field(default="voice_rag")

    # Embeddings
    EMBEDDING_MODEL: str = Field(default="all-MiniLM-L6-v2")

    # Voice
    DEEPGRAM_API_KEY: str = Field(default="")

    # RAG
    CHUNK_SIZE: int = Field(default=512)
    CHUNK_OVERLAP: int = Field(default=64)
    TOP_K: int = Field(default=4)

    # App
    APP_HOST: str = Field(default="0.0.0.0")
    APP_PORT: int = Field(default=8000)
    UPLOAD_DIR: str = Field(default="./data/uploads")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
