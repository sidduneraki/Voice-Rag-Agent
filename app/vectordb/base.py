from abc import ABC, abstractmethod

class BaseVectorDB(ABC):

    @abstractmethod
    def add(self, texts: list[str], embeddings: list[list[float]], metadatas: list[dict]) -> None:
        """Store chunks with their embeddings"""
        pass

    @abstractmethod
    def search(self, query_embedding: list[float], top_k: int) -> list[dict]:
        """Return top_k most similar chunks"""
        pass

    @abstractmethod
    def delete_collection(self) -> None:
        """Wipe the collection"""
        pass
