from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from app.rag.retriever import Retriever
from app.llm.factory import get_llm
from app.core.logger import logger

router = APIRouter()

class ChatRequest(BaseModel):
    question: str

@router.post("/chat")
async def chat(request: ChatRequest):
    logger.info(f"Chat question: {request.question}")
    retriever = Retriever()
    llm = get_llm()
    prompt = retriever.build_prompt(request.question)

    async def token_stream():
        async for token in llm.stream(prompt):
            yield token

    return StreamingResponse(token_stream(), media_type="text/plain")
