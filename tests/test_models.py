import pytest
import uuid
from app.main import app
from sqlalchemy import select
from app.models import Chat, Message

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

@pytest.mark.anyio
async def test_create_message_success(client):
    response = await client.post("/chats/", json={"title": "Test chat"})
    data = response.json()
    chat_id = data["id"]
    author = await client.post("/users/", json={"username": "admin_test", "email": "admin@test.com", "password": "admin_password"})
    author_data = author.json()
    author_id = author_data["id"]
    message = await client.post("/messages/", json={"text": "Hello test", "chat_id": chat_id, "author_id": author_id})
    assert message.status_code == 201
    message_data = message.json()
    print(f"\n[DB Check] Created Message: ID={message_data['id']}, Text='{message_data['text']}', CreatedAt={message_data.get('created_at')}, Chat ID={chat_id}, Author ID={author_id}")

@pytest.mark.anyio
async def test_create_message_fail_chat_not_found(client):
    author = await client.post("/users/", json={"username": "admin_test", "email": "admin@test.com", "password": "admin_password"})
    author_data = author.json()
    author_id = author_data["id"]
    chat_id = str(uuid.uuid4())
    message = await client.post("/messages/", json={"text": "Hello test", "chat_id": chat_id, "author_id": author_id})
    assert message.status_code == 404
    print(f"\n[Test Check] Status code is {message.status_code}")

@pytest.mark.anyio
async def test_delete_chat_cascade(client, session):
    chat = await client.post("/chats/", json={"title": "My TDD Chat"})
    chat_data = chat.json()
    chat_id = chat_data["id"]
    author = await client.post("/users/", json={"username": "admin_test", "email": "admin@test.com", "password": "admin_password"})
    author_data = author.json()
    author_id = author_data["id"]
    message = await client.post("/messages/", json={"text": "Hello test", "chat_id": chat_id, "author_id": author_id})
    message_data = message.json()
    message_id = message_data["id"]
    response = await client.delete(f"/chats/{chat_id}")
    assert response.status_code == 204
    query = select(Message).where(Message.id == message_id)
    db_result = await session.execute(query)
    deleted_message = db_result.scalar_one_or_none()
    assert deleted_message is None
    print(f"\n[Test Check] Item with id {chat_id} deleted successfully")

@pytest.mark.anyio
async def test_create_message_empty_text_fail(client):
    chat = await client.post("/chats/", json={"title": "My TDD Chat"})
    chat_data = chat.json()
    chat_id = chat_data["id"]
    author = await client.post("/users/", json={"username": "admin_test", "email": "admin@test.com", "password": "admin_password"})
    author_data = author.json()
    author_id = author_data["id"]
    message = await client.post("/messages/", json={"text": "", "chat_id": chat_id, "author_id": author_id})
    assert message.status_code == 422
    print(f"\n[Test Check] Can`t post empty message")

@pytest.mark.anyio
async def test_get_messages_success(client):
    chat = await client.post("/chats/", json={"title": "My TDD Chat"})
    chat_data = chat.json()
    chat_id = chat_data["id"]
    author = await client.post("/users/", json={"username": "admin_test", "email": "admin@test.com", "password": "admin_password"})
    author_data = author.json()
    author_id = author_data["id"]
    message_1 = await client.post("/messages/", json={"text": "First message", "chat_id": chat_id, "author_id": author_id})
    message_2 = await client.post("/messages/", json={"text": "Second message", "chat_id": chat_id, "author_id": author_id})
    all_messages = await client.get(f"/chats/{chat_id}/messages")
    assert all_messages.status_code == 200
    assert len(all_messages.json()) == 2
    print(f"\n[Test Check] There are {len(all_messages.json())} messages in chat {chat_id}")

@pytest.mark.anyio
async def test_patch_mesage(client):
    chat = await client.post("/chats/", json={"title": "My TDD Chat"})
    chat_data = chat.json()
    chat_id = chat_data["id"]
    author = await client.post("/users/", json={"username": "admin_test", "email": "admin@test.com", "password": "admin_password"})
    author_data = author.json()
    author_id = author_data["id"]
    message = await client.post("/messages/", json={"text": "wrong text", "chat_id": chat_id, "author_id": author_id})
    message_data = message.json()
    message_id = message_data["id"]
    response = await client.patch(f"/messages/{message_id}", json={"text": "Right text"})
    assert response.status_code == 200
    assert response.json()["text"] == "Right text"
    print(f"\n[Test check] Message {message.json()} has been patched to {response.json()}")