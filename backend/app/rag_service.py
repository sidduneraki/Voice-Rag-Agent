from app.rag.ingestion import IngestionPipeline
from app.rag.retriever import Retriever


class RAGService:
    """Single shared instance — keeps ingestion, retrieval, and voice all in sync."""

    def __init__(self):
        self.pipeline = IngestionPipeline()
        self.retriever = Retriever(pipeline=self.pipeline)


# Module-level singleton — imported by routers and voice pipeline
rag_service = RAGService()
