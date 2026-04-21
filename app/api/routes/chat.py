from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.document import Document
from app.models.user import User
from app.schemas.chat import ChatRequest
from app.services.query import stream_answer

router = APIRouter()


@router.post("/query")
def query_document(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    doc = db.query(Document).filter(
        Document.uuid == request.document_uuid,
        Document.user_id == current_user.id,
    ).first()

    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    if doc.status != "complete":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Document is not ready for querying. Current status: {doc.status}",
        )

    return StreamingResponse(
        stream_answer(request.document_uuid, request.question, request.top_k),
        media_type="text/event-stream",
    )
