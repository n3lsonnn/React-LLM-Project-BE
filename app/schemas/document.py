from datetime import datetime

from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: int
    uuid: str
    filename: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentStatusResponse(BaseModel):
    uuid: str
    status: str

    model_config = {"from_attributes": True}
