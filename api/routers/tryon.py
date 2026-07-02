import os
import shutil
import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from api.database import get_db
from api.models.job import Job, JobStatus
from api.workers.tasks import generate_tryon

router = APIRouter(prefix="/api/v1/tryon", tags=["tryon"])

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/app/uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("", status_code=202)
async def create_tryon(
    selfie: UploadFile = File(...),
    garment_id: str = Form(...),
    seller_id: str = Form(...),
    fitzpatrick: int = Form(..., ge=1, le=6),
    consent: bool = Form(False),
    db: Session = Depends(get_db),
):
    ext = os.path.splitext(selfie.filename or "selfie.jpg")[1] or ".jpg"
    selfie_path = f"{UPLOAD_DIR}/{uuid.uuid4()}{ext}"
    with open(selfie_path, "wb") as f:
        shutil.copyfileobj(selfie.file, f)

    job = Job(
        garment_id=garment_id,
        seller_id=seller_id,
        fitzpatrick=fitzpatrick,
        selfie_path=selfie_path,
        estimated_seconds=10,
        consent=consent,
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    task = generate_tryon.delay(job.id, selfie_path, garment_id, fitzpatrick)
    job.celery_task_id = task.id
    db.commit()

    return {"job_id": job.id, "estimated_seconds": job.estimated_seconds}


@router.get("/{job_id}")
def get_tryon(job_id: str, db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {
        "job_id": job.id,
        "status": job.status,
        "progress": job.progress,
        "result_url": job.result_url,
        "error": job.error,
    }
