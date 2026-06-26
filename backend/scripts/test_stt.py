import asyncio
import sys
sys.path.insert(0, ".")
from app.voice.stt import DeepgramSTT
from app.core.logger import logger

async def test():
    stt = DeepgramSTT()
    audio_queue = asyncio.Queue()
    transcript_queue = asyncio.Queue()

    # Run STT in background
    stt_task = asyncio.create_task(
        stt.transcribe_stream(audio_queue, transcript_queue)
    )

    # Feed a real audio file to test
    with open("data/test_audio.raw", "rb") as f:
        audio_data = f.read()

    # Send in chunks like mic would
    chunk_size = 8192
    bytes_per_second = 16000 * 2  # sample_rate * bytes_per_sample

    for i in range(0, len(audio_data), chunk_size):
        await audio_queue.put(audio_data[i:i+chunk_size])
        await asyncio.sleep(chunk_size / bytes_per_second)

    await audio_queue.put(None)
    await asyncio.sleep(1.5)
    await stt_task

    logger.info("Transcripts received:")
    while not transcript_queue.empty():
        logger.success(await transcript_queue.get())

if __name__ == "__main__":
    asyncio.run(test())

