import shutil
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.rag.ingestion import IngestionPipeline
from app.core.config import get_settings
from app.core.logger import logger

router = APIRouter()

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.endswith((".pdf", ".txt")):
        raise HTTPException(status_code=400, detail="Only PDF and TXT files supported")

    upload_dir = Path(get_settings().UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / file.filename

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    logger.info(f"Saved upload: {file.filename}")

    pipeline = IngestionPipeline()
    count = pipeline.ingest_pdf(str(file_path))

    return {"filename": file.filename, "chunks_ingested": count}
