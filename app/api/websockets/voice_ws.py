import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.voice.pipeline import VoicePipeline
from app.core.logger import logger

router = APIRouter()

@router.websocket("/ws/voice")
async def voice_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("Voice WebSocket connected")

    audio_in_queue = asyncio.Queue()
    audio_out_queue = asyncio.Queue()
    pipeline = VoicePipeline()

    async def receive_audio():
        try:
            while True:
                audio_chunk = await websocket.receive_bytes()
                await audio_in_queue.put(audio_chunk)
        except WebSocketDisconnect:
            await audio_in_queue.put(None)
            logger.info("Client disconnected")

    async def send_audio():
        while True:
            audio = await audio_out_queue.get()
            if audio is None:
                break
            await websocket.send_bytes(audio)

    await asyncio.gather(
        receive_audio(),
        send_audio(),
        pipeline.run(audio_in_queue, audio_out_queue),
    )
