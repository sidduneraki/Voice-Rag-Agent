import asyncio
import sys
sys.path.insert(0, ".")
from app.voice.tts import DeepgramTTS
from app.core.logger import logger

async def test():
    tts = DeepgramTTS()
    audio = await tts.synthesize("Hello! The voice RAG agent is working correctly.")
    with open("data/test_output.mp3", "wb") as f:
        f.write(audio)
    logger.success(f"TTS works! Audio saved to data/test_output.mp3 ({len(audio)} bytes)")

asyncio.run(test())
#########################################################
#to test stt
# import asyncio
# import sys
# sys.path.insert(0, ".")

# from app.voice.stt import DeepgramSTT
# from app.core.logger import logger

# async def test():
#     stt = DeepgramSTT()

#     # read an audio file instead of generating one
#     with open("data/test_input.wav", "rb") as f:
#         audio = f.read()

#     text = await stt.transcribe(audio)

#     logger.success(f"STT works! Transcription: {text}")

# asyncio.run(test())