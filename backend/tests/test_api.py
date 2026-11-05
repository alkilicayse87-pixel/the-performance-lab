import pytest

from fastapi.testclient import TestClient

from app.main import app
from app import main


@pytest.fixture
def client():
    return TestClient(app)


def test_root_endpoint(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["status"] == "success"


def test_health_endpoint(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_video_ingestion_success(client, monkeypatch):
    def fake_ingest(youtube_url):
        return {
            "video_id": "abcdefghijk",
            "status": "processed",
        }

    monkeypatch.setattr(
        main,
        "ingest_youtube_video",
        fake_ingest,
    )

    response = client.post(
        "/videos/ingest",
        json={"youtube_url": "https://www.youtube.com/watch?v=abcdefghijk"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "processed"


def test_video_ingestion_value_error(client, monkeypatch):
    def fake_ingest(youtube_url):
        raise ValueError("Invalid YouTube URL.")

    monkeypatch.setattr(
        main,
        "ingest_youtube_video",
        fake_ingest,
    )

    response = client.post(
        "/videos/ingest",
        json={"youtube_url": "invalid-url"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid YouTube URL."


def test_agent_chat_success(client, monkeypatch):
    def fake_agent_answer(message, video_id, conversation_id):
        return "This is a test answer."

    monkeypatch.setattr(
        main,
        "generate_agent_answer",
        fake_agent_answer,
    )

    response = client.post(
        "/agent-chat",
        json={
            "video_id": "abcdefghijk",
            "conversation_id": "test-conversation",
            "message": "What is this video about?",
        },
    )

    assert response.status_code == 200
    assert response.json()["answer"] == "This is a test answer."
    assert response.json()["agent"] == "LangGraph"


def test_agent_chat_value_error(client, monkeypatch):
    def fake_agent_answer(message, video_id, conversation_id):
        raise ValueError("Invalid input.")

    monkeypatch.setattr(
        main,
        "generate_agent_answer",
        fake_agent_answer,
    )

    response = client.post(
        "/agent-chat",
        json={
            "video_id": "abcdefghijk",
            "conversation_id": "test-conversation",
            "message": "Test question",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid input."


def test_agent_chat_internal_error(client, monkeypatch):
    def fake_agent_answer(message, video_id, conversation_id):
        raise RuntimeError("Internal test error.")

    monkeypatch.setattr(
        main,
        "generate_agent_answer",
        fake_agent_answer,
    )

    response = client.post(
        "/agent-chat",
        json={
            "video_id": "abcdefghijk",
            "conversation_id": "test-conversation",
            "message": "Test question",
        },
    )

    assert response.status_code == 500
    assert response.json()["detail"] == "The agent could not process the request."

def test_chat_success(client, monkeypatch):
    def fake_generate_answer(message, video_id, conversation_id):
        return "This is a legacy chat test answer."

    monkeypatch.setattr(
        main,
        "generate_answer",
        fake_generate_answer,
    )

    response = client.post(
        "/chat",
        json={
            "video_id": "abcdefghijk",
            "conversation_id": "test-conversation",
            "message": "What is this video about?",
        },
    )

    assert response.status_code == 200
    assert response.json()["answer"] == "This is a legacy chat test answer."


def test_agent_chat_rejects_invalid_request(client):
    response = client.post(
        "/agent-chat",
        json={
            "video_id": "short",
            "conversation_id": "test-conversation",
            "message": "Test question",
        },
    )

    assert response.status_code == 422

def test_video_ingestion_internal_error(client, monkeypatch):
    def fake_ingest(youtube_url):
        raise RuntimeError("Internal test error.")

    monkeypatch.setattr(
        main,
        "ingest_youtube_video",
        fake_ingest,
    )

    response = client.post(
        "/videos/ingest",
        json={"youtube_url": "https://www.youtube.com/watch?v=abcdefghijk"},
    )

    assert response.status_code == 500
    assert response.json()["detail"] == "The video could not be processed."