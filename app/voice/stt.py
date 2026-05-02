import asyncio
from deepgram import DeepgramClient, LiveTranscriptionEvents, LiveOptions
from app.core.config import get_settings
from app.core.logger import logger

class DeepgramSTT:
    def __init__(self):
        settings = get_settings()
        self.client = DeepgramClient(settings.DEEPGRAM_API_KEY)
        self.options = LiveOptions(
            model="nova-2",
            language="en-US",
            smart_format=True,
            interim_results=True,
            encoding="linear16",
            sample_rate=16000,
            utterance_end_ms="2000",  # wait 2s of silence before final
            endpointing=800,   # wait 800ms pause before sending
        )
        logger.info("DeepgramSTT ready")

    async def transcribe_stream(self, audio_queue: asyncio.Queue, transcript_queue: asyncio.Queue):
        connection = self.client.listen.asynclive.v("1")

        async def on_transcript(self_inner, result, **kwargs):
            try:
                transcript = result.channel.alternatives[0].transcript
                if not transcript:
                    return
                if result.is_final:
                    logger.debug(f"STT final: {transcript}")
                    await transcript_queue.put(transcript)
                else:
                    logger.debug(f"STT interim: {transcript}")
            except Exception as e:
                logger.error(f"STT handler error: {e}")

        async def on_error(self_inner, error, **kwargs):
            logger.error(f"STT error: {error}")

        connection.on(LiveTranscriptionEvents.Transcript, on_transcript)
        connection.on(LiveTranscriptionEvents.Error, on_error)

        await connection.start(self.options)
        logger.info("STT stream started")

        async def keepalive():
            while True:
                await asyncio.sleep(5)
                try:
                    await connection.keep_alive()
                    logger.debug("STT keepalive sent")
                except Exception:
                    break

        keepalive_task = asyncio.create_task(keepalive())

        try:
            while True:
                audio_chunk = await audio_queue.get()
                if audio_chunk is None:
                    break
                await connection.send(audio_chunk)
        finally:
            keepalive_task.cancel()
            await connection.finish()
            logger.info("STT stream closed")
