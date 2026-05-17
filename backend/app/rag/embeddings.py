from sentence_transformers import SentenceTransformer
from app.core.config import get_settings
from app.core.logger import logger

_instance = None

class EmbeddingModel:
    def __init__(self):
        model_name = get_settings().EMBEDDING_MODEL
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        logger.success(f"Embedding model ready")

    def embed(self, texts: list[str]) -> list[list[float]]:
        return self.model.encode(texts, convert_to_numpy=True).tolist()

    def embed_one(self, text: str) -> list[float]:
        return self.embed([text])[0]

def get_embedding_model() -> EmbeddingModel:
    global _instance
    if _instance is None:
        _instance = EmbeddingModel()
    return _instance
