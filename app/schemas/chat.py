from pydantic import BaseModel


class ChatRequest(BaseModel):
    document_uuid: str
    question: str
    top_k: int = 5
