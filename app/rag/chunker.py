from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.core.config import get_settings
from app.core.logger import logger

class Chunker:
    def __init__(self):
        settings = get_settings()
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            separators=["\n\n", "\n", ".", "!", "?", " ", ""],
        )

    def split(self, text: str) -> list[str]:
        chunks = self.splitter.split_text(text)
        logger.debug(f"Split into {len(chunks)} chunks")
        return chunks
