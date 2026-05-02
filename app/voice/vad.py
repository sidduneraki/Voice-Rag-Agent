import asyncio
from app.core.logger import logger

class VAD:
    """
    Simple energy-based VAD.
    Deepgram handles true VAD on their end via vad_events=True.
    This class manages the silence timeout on our side.
    """
    def __init__(self, silence_threshold_ms: int = 1000):
        self.silence_threshold_ms = silence_threshold_ms
        self._last_speech_time = None
        self._speaking = False

    def process(self, audio_chunk: bytes) -> bool:
        # Calculate RMS energy of chunk
        import struct
        samples = struct.unpack(f"{len(audio_chunk)//2}h", audio_chunk)
        rms = (sum(s**2 for s in samples) / len(samples)) ** 0.5
        is_speech = rms > 300
        if is_speech:
            self._speaking = True
        return is_speech

    @property
    def is_speaking(self) -> bool:
        return self._speaking

    def reset(self):
        self._speaking = False
        logger.debug("VAD reset")
