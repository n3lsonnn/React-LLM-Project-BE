import uuid
import os

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.document import Document
from app.models.user import User
from app.schemas.document import DocumentResponse, DocumentStatusResponse
from app.services.ingestion import run_ingestion

router = APIRouter()

UPLOADS_DIR = "uploads"


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_202_ACCEPTED)
def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are accepted",
        )

    document_uuid = str(uuid.uuid4())

    os.makedirs(UPLOADS_DIR, exist_ok=True)
    file_path = f"{UPLOADS_DIR}/{document_uuid}.pdf"
    with open(file_path, "wb") as f:
        f.write(file.file.read())

    doc = Document(
        uuid=document_uuid,
        user_id=current_user.id,
        filename=file.filename,
        status="pending",
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    background_tasks.add_task(run_ingestion, file_path, document_uuid)

    return doc


@router.get("/{document_uuid}/status", response_model=DocumentStatusResponse)
def get_document_status(
    document_uuid: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    doc = db.query(Document).filter(
        Document.uuid == document_uuid,
        Document.user_id == current_user.id,
    ).first()

    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    return doc
