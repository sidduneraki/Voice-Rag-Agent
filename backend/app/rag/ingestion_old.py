import hashlib
import pymupdf
from pathlib import Path
from app.rag.chunker import Chunker
from app.rag.embeddings import get_embedding_model
from app.vectordb.factory import get_vectordb
from app.core.logger import logger


def _collection_name_for(filename: str) -> str:
    """Stable, unique collection name derived from the PDF filename."""
    digest = hashlib.md5(filename.encode()).hexdigest()[:16]
    return f"pdf_{digest}"


class IngestionPipeline:
    def __init__(self):
        self.chunker = Chunker()
        self.embedder = get_embedding_model()
        # Initialize to standard default vector db reference
        self.vectordb = get_vectordb()
        self.active_collection: str | None = "default"

    def ingest_pdf(self, file_path: str) -> int:
        path = Path(file_path)
        collection_name = _collection_name_for(path.name)
        logger.info(f"Ingesting: {path.name} → collection '{collection_name}'")

        # Switch vectordb to this PDF's own collection
        self.vectordb = get_vectordb(collection_name=collection_name)
        self.active_collection = collection_name

        # Skip re-ingestion if this PDF was already processed
        if self.vectordb.count() > 0:
            logger.info("Already ingested — skipping embedding step")
            return self.vectordb.count()

        # Extract text while keeping track of page numbers
        doc = pymupdf.open(file_path)
        all_chunks = []
        all_metadatas = []
        
        for page_idx, page in enumerate(doc):
            page_text = page.get_text()
            if not page_text.strip():
                continue
                
            # Chunk page by page so we don't lose the structural page reference
            page_chunks = self.chunker.split(page_text)
            for chunk_idx, chunk in enumerate(page_chunks):
                all_chunks.append(chunk)
                all_metadatas.append({
                    "source": path.name,
                    "page": page_idx + 1, # Humans count pages starting at 1
                    "chunk_index": chunk_idx
                })
        doc.close()
        logger.debug(f"Extracted {len(all_chunks)} total chunks from PDF steps")

        if not all_chunks:
            logger.warning(f"No text extracted from {path.name}")
            return 0

        # Embed all chunks at once
        embeddings = self.embedder.embed(all_chunks)
        self.vectordb.add(all_chunks, embeddings, all_metadatas)

        logger.success(f"Ingested {len(all_chunks)} chunks from {path.name}")
        return len(all_chunks)

    def switch_pdf(self, filename: str) -> bool:
        """Switch active context to a previously ingested PDF."""
        collection_name = _collection_name_for(filename)
        candidate = get_vectordb(collection_name=collection_name)
        if candidate.count() == 0:
            logger.warning(f"No ingested data found for '{filename}'")
            return False
        self.vectordb = candidate
        self.active_collection = collection_name
        logger.info(f"Switched active PDF to '{filename}'")
        return True

    def ingest_text(self, text: str, source: str = "manual", target_collection: str = "default") -> int:
        """Ingest raw text into a designated collection safely without messing with global state."""
        # Force switch target collection to avoid polluting previously active PDF collections
        temp_db = get_vectordb(collection_name=target_collection)
        
        chunks = self.chunker.split(text)
        embeddings = self.embedder.embed(chunks)
        metadatas = [{"source": source, "chunk_index": i} for i in range(len(chunks))]
        
        temp_db.add(chunks, embeddings, metadatas)
        logger.success(f"Ingested {len(chunks)} chunks from {source} into '{target_collection}'")
        return len(chunks)