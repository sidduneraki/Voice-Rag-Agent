from app.vectordb.base import BaseVectorDB
from app.core.logger import logger

class QdrantVectorDB(BaseVectorDB):
    def __init__(self):
        from qdrant_client import QdrantClient
        from app.core.config import get_settings
        settings = get_settings()
        self.client = QdrantClient(url=settings.QDRANT_URL)
        self.collection = settings.QDRANT_COLLECTION
        logger.info(f"Qdrant ready | url={settings.QDRANT_URL}")

    def add(self, texts: list[str], embeddings: list[list[float]], metadatas: list[dict]) -> None:
        from qdrant_client.models import PointStruct
        points = [
            PointStruct(id=i, vector=emb, payload={"text": t, **meta})
            for i, (t, emb, meta) in enumerate(zip(texts, embeddings, metadatas))
        ]
        self.client.upsert(collection_name=self.collection, points=points)
        logger.debug(f"Added {len(texts)} chunks to quadrant_db")

    def search(self, query_embedding: list[float], top_k: int) -> list[dict]:
        results = self.client.search(collection_name=self.collection, query_vector=query_embedding, limit=top_k)
        return [{"text": r.payload["text"], "metadata": r.payload, "score": r.score} for r in results]

    def delete_collection(self) -> None:
        self.client.delete_collection(self.collection)
        logger.warning("quadrantDB collection deleted")
