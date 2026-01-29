import pytest
from app.main import app
from sqlalchemy import select
from app.models import Chat

@pytest.mark.anyio
async def test_create_chat_success(client, session):
    response = await client.post("/chats/", json={"title": "My TDD Chat"})
    assert response.status_code == 201
    data = response.json()
    chat_id = data["id"]
    query = select(Chat).where(Chat.id == chat_id)
    result = (await session.execute(query)).scalar_one_or_none()
    assert result is not None
    assert result.title == "My TDD Chat"
    assert str(result.id) == chat_id
    assert data["title"] == "My TDD Chat"
    assert "id" in data
    assert result.created_at is not None
    print(f"\n[DB Check] Created Chat: ID={result.id}, Title='{result.title}', CreatedAt={result.created_at}")