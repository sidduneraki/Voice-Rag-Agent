import pymupdf
from pathlib import Path
from app.rag.chunker import Chunker
from app.rag.embeddings import get_embedding_model
from app.vectordb.factory import get_vectordb
from app.core.logger import logger

class IngestionPipeline:
    def __init__(self):
        self.chunker = Chunker()
        self.embedder = get_embedding_model()
        self.vectordb = get_vectordb()

    def ingest_pdf(self, file_path: str) -> int:
        path = Path(file_path)
        logger.info(f"Ingesting: {path.name}")
        if self.vectordb:
            try:
                self.vectordb.delete_collection()
            except Exception as e:
                logger.warning(f"Delete failed (maybe first run): {e}")

        self.vectordb = get_vectordb()

        # Extract text
        doc = pymupdf.open(file_path)
        full_text = ""
        for page in doc:
            full_text += page.get_text()
        doc.close()
        logger.debug(f"Extracted {len(full_text)} characters")

        # Chunk
        chunks = self.chunker.split(full_text)

        # Embed
        embeddings = self.embedder.embed(chunks)

        # Store
        metadatas = [{"source": path.name, "chunk_index": i} for i in range(len(chunks))]
        self.vectordb.add(chunks, embeddings, metadatas)

        logger.success(f"Ingested {len(chunks)} chunks from {path.name}")
        return len(chunks)

    def ingest_text(self, text: str, source: str = "manual") -> int:
        chunks = self.chunker.split(text)
        embeddings = self.embedder.embed(chunks)
        metadatas = [{"source": source, "chunk_index": i} for i in range(len(chunks))]
        self.vectordb.add(chunks, embeddings, metadatas)
        logger.success(f"Ingested {len(chunks)} chunks from {source}")
        return len(chunks)
