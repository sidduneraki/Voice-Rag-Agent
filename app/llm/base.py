from abc import ABC, abstractmethod
from typing import AsyncGenerator

class BaseLLM(ABC):

    @abstractmethod
    async def generate(self, prompt: str) -> str:
        """Full response, no streaming"""
        pass

    @abstractmethod
    async def stream(self, prompt: str) -> AsyncGenerator[str, None]:
        """Yield tokens as they arrive"""
        pass
