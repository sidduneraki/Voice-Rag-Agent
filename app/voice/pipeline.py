import asyncio
import re
from enum import Enum
from app.voice.stt import DeepgramSTT
from app.voice.tts import DeepgramTTS
from app.voice.vad import VAD
from app.rag.retriever import Retriever
from app.llm.factory import get_llm
from app.core.logger import logger


class PipelineState(Enum):
    LISTENING = "listening"
    THINKING  = "thinking"
    SPEAKING  = "speaking"


class VoicePipeline:
    def __init__(self):
        self.stt        = DeepgramSTT()
        self.tts        = DeepgramTTS()
        self.vad        = VAD()
        self.retriever  = Retriever()
        self.llm        = get_llm()
        self.state      = PipelineState.LISTENING
        self._speak_task: asyncio.Task | None = None
        self._last_transcript = ""
        logger.info("VoicePipeline ready")

    def _split_sentences(self, text: str) -> list[str]:
        return [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]

    def _is_user_speaking(self, audio_chunk: bytes) -> bool:
        import struct
        if len(audio_chunk) < 2:
            return False
        samples = struct.unpack(f"{len(audio_chunk)//2}h", audio_chunk)
        rms = (sum(s**2 for s in samples) / len(samples)) ** 0.5
        return rms > 500

    def _cancel_speaking(self):
        if self._speak_task and not self._speak_task.done():
            self._speak_task.cancel()
            logger.info("TTS interrupted by user")
        self._speak_task = None
        self.state = PipelineState.LISTENING
    def _clean_for_tts(self, text: str) -> str:
        import re
        text = re.sub(r'\*+', '', text)          # remove bold/italic
        text = re.sub(r'^[-•]\s+', '', text, flags=re.MULTILINE)  # remove bullets
        text = re.sub(r'^\d+\.\s+', '', text, flags=re.MULTILINE) # remove numbered lists
        text = re.sub(r'\s+', ' ', text)          # collapse whitespace
        return text.strip()

    async def _speak(self, prompt: str, audio_out_queue: asyncio.Queue):
        self.state = PipelineState.SPEAKING
        await audio_out_queue.put(b"__TTS_START__")

        try:
            buffer = ""
            async for token in self.llm.stream(prompt):
                buffer += token
                sentences = self._split_sentences(buffer)
                if len(sentences) > 1:
                    for sentence in sentences[:-1]:
                        sentence = self._clean_for_tts(sentence)
                        if not sentence:
                            continue
                        logger.debug(f"TTS: {sentence}")
                        audio = await self.tts.synthesize(sentence)
                        await audio_out_queue.put(audio)
                    buffer = sentences[-1]

            if buffer.strip():
                buffer = self._clean_for_tts(buffer)
                audio = await self.tts.synthesize(buffer)
                await audio_out_queue.put(audio)

        except asyncio.CancelledError:
            logger.info("Speaking cancelled")

        finally:
            await audio_out_queue.put(b"__TTS_END__")
            self.state = PipelineState.LISTENING
            logger.info("State → LISTENING")

    async def run(self, audio_in_queue: asyncio.Queue, audio_out_queue: asyncio.Queue):
        transcript_queue = asyncio.Queue()
        filtered_queue   = asyncio.Queue()

        async def audio_filter():
            while True:
                chunk = await audio_in_queue.get()
                if chunk is None:
                    await filtered_queue.put(None)
                    break
                # Detect interruption FIRST (before any drop)
                if self.state != PipelineState.LISTENING:
                    if self._is_user_speaking(chunk):
                        logger.info("Interruption detected — cancelling")
                        self._cancel_speaking()
                # Block STT during speaking (prevent feedback loop)
                if self.state == PipelineState.SPEAKING:
                    continue
                await filtered_queue.put(chunk)

        stt_task    = asyncio.create_task(self.stt.transcribe_stream(filtered_queue, transcript_queue))
        filter_task = asyncio.create_task(audio_filter())

        logger.info(f"State → {self.state.value}")

        try:
            while True:
                transcript = await transcript_queue.get()
                if transcript is None:
                    break

                transcript = transcript.strip()

                if len(transcript) < 3:
                    continue

                if transcript == self._last_transcript:
                    continue

                self._last_transcript = transcript
                logger.info(f"Transcript: {transcript}")

                self._cancel_speaking()

                self.state = PipelineState.THINKING
                logger.info("State → THINKING")

                prompt = await asyncio.get_event_loop().run_in_executor(
                    None, self.retriever.build_prompt, transcript
                )

                self._speak_task = asyncio.create_task(
                    self._speak(prompt, audio_out_queue)
                )
                await self._speak_task
                self.vad.reset()

        finally:
            filter_task.cancel()
            stt_task.cancel()
            await audio_out_queue.put(None)
            logger.info("Voice pipeline stopped")
