import uuid
import asyncio
from fastapi import APIRouter, Depends, status, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db, AsyncSessionLocal
from app.crud.chat import get_or_create_session, create_message
from app.schemas.chat import ChatStreamRequest
from app.services.chat_service import chat_service, AssistantContent
from app.models.chat import MessageRole

router = APIRouter()

async def save_assistant_message(session_id: uuid.UUID, content: str):
    """Background task to persist assistant message after streaming."""
    if content:
        async with AsyncSessionLocal() as fresh_db:
            await create_message(fresh_db, session_id, MessageRole.ASSISTANT, content)
            await fresh_db.commit()

@router.post("/stream", status_code=status.HTTP_200_OK)
async def chat_stream(
    request: ChatStreamRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Accept user message, persist to DB, and stream AI response via SSE.
    Assistant response is persisted to DB after streaming completes.
    """
    # 1. Atomic Persistence: Ensure session exists and persist user message BEFORE stream
    await get_or_create_session(db, request.session_id, request.user_id)
    await create_message(db, request.session_id, MessageRole.USER, request.message)
    await db.commit()

    # Tracker object to capture full content across the async generator
    tracker = AssistantContent()

    async def event_generator():
        # 2. Get the stream generator from ChatService
        stream = chat_service.stream_chat(
            message=request.message,
            session_id=request.session_id,
            content_tracker=tracker
        )
        
        async for chunk in stream:
            yield chunk

        # 3. Final Persistence: Schedule background persistence
        background_tasks.add_task(save_assistant_message, request.session_id, tracker.content)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
        }
    )
