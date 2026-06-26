import chromadb
from app.vectordb.base import BaseVectorDB
from app.core.config import get_settings
from app.core.logger import logger
import uuid

class ChromaVectorDB(BaseVectorDB):
    def __init__(self,collection_name: str = "default"):
        settings = get_settings()
        self.client = chromadb.PersistentClient(path=settings.CHROMA_PATH)
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info(f"ChromaDB ready | path={settings.CHROMA_PATH}")

    def add(self, texts: list[str], embeddings: list[list[float]], metadatas: list[dict]) -> None:
        # ids = [f"chunk_{i}_{hash(t)}" for i, t in enumerate(texts)]
        ids = [str(uuid.uuid4()) for _ in texts]
        self.collection.add(documents=texts, embeddings=embeddings, metadatas=metadatas, ids=ids)
        logger.debug(f"Added {len(texts)} chunks to ChromaDB")

    def search(self, query_embedding: list[float], top_k: int) -> list[dict]:
        results = self.collection.query(query_embeddings=[query_embedding], n_results=top_k)
        chunks = []
        if not results or not results.get("documents") or not results["documents"][0]:
            logger.debug(f"Retrieved {len(chunks)} chunks from ChromaDB")
            return chunks
        for i, doc in enumerate(results["documents"][0]):
            chunks.append({
                "text": doc,
                "metadata": results["metadatas"][0][i],
                "score": 1 - results["distances"][0][i],
            })
        logger.debug(f"Retrieved {len(chunks)} chunks from ChromaDB")
        return chunks

    def delete_collection(self) -> None:
        self.client.delete_collection(self.collection.name)
        logger.warning(f"ChromaDB collection'{self.collection.name}' deleted")
    def count(self) -> int:
        return self.collection.count()
