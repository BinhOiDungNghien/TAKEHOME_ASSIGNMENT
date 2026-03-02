import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.chat import ChatSession, ChatMessage, MessageRole

@pytest.mark.asyncio
async def test_read_session_history_not_found(client: AsyncClient):
    """Test getting history for a non-existent session returns 404."""
    random_id = uuid.uuid4()
    response = await client.get(f"/api/v1/sessions/{random_id}/history?user_id=test-user")
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Session not found or unauthorized access"

@pytest.mark.asyncio
async def test_read_session_history_success(client: AsyncClient, db_session: AsyncSession):
    """Test getting history for an existing session returns correct data."""
    # 1. Manually create a session and messages in the test DB
    session_id = uuid.uuid4()
    user_id = "test-user"
    
    session = ChatSession(id=session_id, user_id=user_id)
    db_session.add(session)
    await db_session.flush()
    
    msg1 = ChatMessage(session_id=session_id, role=MessageRole.USER, content="Hello")
    msg2 = ChatMessage(session_id=session_id, role=MessageRole.ASSISTANT, content="Hi there!")
    db_session.add_all([msg1, msg2])
    await db_session.commit()
    
    # 2. Call the API
    response = await client.get(f"/api/v1/sessions/{session_id}/history?user_id={user_id}")
    
    # 3. Verify
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == str(session_id)
    assert len(data["messages"]) == 2
    assert data["messages"][0]["role"] == "user"
    assert data["messages"][1]["role"] == "assistant"

@pytest.mark.asyncio
async def test_delete_session_success(client: AsyncClient, db_session: AsyncSession):
    """Test deleting a session correctly removes it from the DB."""
    # 1. Create a session
    session_id = uuid.uuid4()
    user_id = "test-user"
    session = ChatSession(id=session_id, user_id=user_id)
    db_session.add(session)
    await db_session.commit()
    
    # 2. Delete via API
    response = await client.delete(f"/api/v1/sessions/{session_id}?user_id={user_id}")
    
    # 3. Verify
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    
    # 4. Confirm it's gone from DB
    history_response = await client.get(f"/api/v1/sessions/{session_id}/history?user_id={user_id}")
    assert history_response.status_code == 404
