from openai import AsyncOpenAI
from typing import AsyncGenerator
from app.llm.base import BaseLLM
from app.core.config import get_settings
from app.core.logger import logger

class OllamaLLM(BaseLLM):
    def __init__(self):
        settings = get_settings()
        self.client = AsyncOpenAI(
            api_key="ollama",
            base_url=f"{settings.OLLAMA_BASE_URL}/v1",
        )
        self.model = settings.OLLAMA_MODEL

    async def generate(self, prompt: str) -> str:
        logger.debug(f"Ollama generate | model={self.model}")
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content

    async def stream(self, prompt: str) -> AsyncGenerator[str, None]:
        logger.debug(f"Ollama stream | model={self.model}")
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            stream=True,
        )
        async for chunk in response:
            token = chunk.choices[0].delta.content
            if token:
                yield token
