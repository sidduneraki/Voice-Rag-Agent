from app.rag.embeddings import get_embedding_model
from app.vectordb.factory import get_vectordb
from app.core.config import get_settings
from app.core.logger import logger

class Retriever:
    def __init__(self):
        self.embedder = get_embedding_model()
        self.vectordb = get_vectordb()
        self.top_k = get_settings().TOP_K

    def retrieve(self, query: str) -> list[dict]:
        logger.debug(f"Retrieving for: {query}")
        query_embedding = self.embedder.embed_one(query)
        chunks = self.vectordb.search(query_embedding, self.top_k)
        return chunks

    def build_context(self, query: str) -> str:
        chunks = self.retrieve(query)
        context = "\n\n".join([c["text"] for c in chunks])
        logger.debug(f"Built context from {len(chunks)} chunks")
        return context

    def build_prompt(self, query: str) -> str:
        context = self.build_context(query)
        return f"""You are a helpful voice assistant. Answer using ONLY the context below.
        If the answer is not in the context, say "I don't have that information in the document."
        Keep answers concise — 2 to 3 sentences. 
        Do NOT use bullet points, markdown, or lists. Speak in plain natural sentences only.

        Context:
        {context}

        User question: {query}

        Answer:"""
