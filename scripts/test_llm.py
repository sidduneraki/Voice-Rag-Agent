import asyncio
import sys
sys.path.insert(0, ".")
from app.llm.factory import get_llm
from app.core.logger import logger

async def test():
    llm = get_llm()

    # Test full response
    logger.info("Testing generate()...")
    response = await llm.generate("Say hello in one sentence.")
    logger.success(f"Response: {response}")

    # Test streaming
    logger.info("Testing stream()...")
    async for token in llm.stream("Count 1 to 5."):
        print(token, end="", flush=True)
    print()
    logger.success("Streaming works!")

asyncio.run(test())
