from fastapi import APIRouter, UploadFile, File, HTTPException, status
from pathlib import Path
import shutil, uuid

UPLOAD_DIR = Path("uploaded_docs")
UPLOAD_DIR.mkdir(exist_ok=True)

router = APIRouter(prefix="/upload", tags=["upload"])

@router.post("/doc")
async def upload_doc(file: UploadFile = File(...)):
    # simple type guard (extend as needed)
    if not file.filename.lower().endswith((".pdf", ".txt", ".docx")):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Only PDF, TXT, or DOCX allowed")

    # save with a unique name
    dest = UPLOAD_DIR / f"{uuid.uuid4()}_{file.filename}"
    with dest.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # TODO: forward to data‑ingestion‑service if/when ready

    return {"filename": file.filename, "stored_as": dest.name}
