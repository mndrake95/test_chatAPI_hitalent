import pytest
from app.main import app

@pytest.mark.anyio
async def test_create_chat_success(client):
    response = await client.post("/chats/", json={"title": "My TDD Chat"})
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "My TDD Chat"
    assert "id" in data
