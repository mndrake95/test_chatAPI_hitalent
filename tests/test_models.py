import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_create_chat_success():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/chats/", json={"title": "My TDD Chat"})
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "My TDD Chat"
    assert "id" in data