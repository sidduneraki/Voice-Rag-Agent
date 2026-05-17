import httpx
from app.core.config import get_settings
from app.core.logger import logger

class DeepgramTTS:
    def __init__(self):
        settings = get_settings()
        self.api_key = settings.DEEPGRAM_API_KEY
        self.url = "https://api.deepgram.com/v1/speak"
        self.params = {"model": "aura-asteria-en"}
        logger.info("DeepgramTTS ready")

    async def synthesize(self, text: str) -> bytes:
        logger.debug(f"TTS synthesize: {text[:50]}...")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.url,
                params=self.params,
                headers={
                    "Authorization": f"Token {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={"text": text},
                timeout=10.0,
            )
            response.raise_for_status()
            logger.debug(f"TTS received {len(response.content)} bytes")
            return response.content
