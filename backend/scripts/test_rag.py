import asyncio
import sys
sys.path.insert(0, ".")
from app.rag.ingestion import IngestionPipeline
from app.rag.retriever import Retriever
from app.llm.factory import get_llm
from app.core.logger import logger

async def test():
    # Ingest
    pipeline = IngestionPipeline()
    count = pipeline.ingest_pdf("data/uploads/sample.pdf")
    logger.success(f"Ingested {count} chunks")
    #print(chunks)

    # Retrieve + LLM
    retriever = Retriever()
    llm = get_llm()

    query = "What is this document about?"
    prompt = retriever.build_prompt(query)
    logger.info(f"Query: {query}")

    response = await llm.generate(prompt)
    logger.success(f"Answer: {response}")

asyncio.run(test())
