import asyncio
import sys
sys.path.insert(0, ".")
from app.voice.tts import DeepgramTTS


async def main():
    tts = DeepgramTTS()
    # Request raw linear16, 16 kHz (configure your TTS client to emit this)
    audio = await tts.synthesize(
        "Hello, this is a test of the speech to text system.",
        encoding="linear16",
        sample_rate=16000,
    )
    with open("data/test_audio.raw", "wb") as f:
        f.write(audio)
    print("Saved test_audio.raw as raw linear16 16kHz")


asyncio.run(main())
# import asyncio
# import sys
# sys.path.insert(0, ".")
# from app.voice.tts import DeepgramTTS

# async def main():
#     tts = DeepgramTTS()
#     audio = await tts.synthesize("Hello, this is a test of the speech to text system.")
#     with open("data/test_audio.mp3", "wb") as f:
#         f.write(audio)
#     print("Saved test_audio.mp3")

# asyncio.run(main())
