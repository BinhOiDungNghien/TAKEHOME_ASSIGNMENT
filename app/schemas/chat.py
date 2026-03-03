import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from app.models.chat import MessageRole

class ChatMessageBase(BaseModel):
    role: MessageRole
    content: str
    created_at: datetime
    token_count: Optional[int] = None
    finish_reason: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class SessionHistoryResponse(BaseModel):
    session_id: uuid.UUID
    messages: List[ChatMessageBase]

    model_config = ConfigDict(from_attributes=True)

class SessionDeleteResponse(BaseModel):
    status: str
    message: str

class ChatStreamRequest(BaseModel):
    session_id: uuid.UUID
    user_id: str
    message: str
