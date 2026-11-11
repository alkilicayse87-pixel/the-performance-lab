import pytest

from app.retrieval import retriever


def test_retrieve_chunks_returns_expected_data(monkeypatch):
    expected = [{
        "text": "Freestyle swimming technique",
        "video_id": "video123456",
        "chunk_index": 2,
        "start_time": 10.0,
        "end_time": 20.0,
        "segment_count": 5,
    }]

    def fake_retrieve_chunks(query, video_id=None, k=5):
        return expected

    monkeypatch.setattr(
        retriever,
        "neon_retrieve_chunks",
        fake_retrieve_chunks,
    )

    result = retriever.retrieve_chunks(
        query="swimming technique",
        video_id="video123456",
        k=3,
    )

    assert result == expected


def test_retrieve_chunks_passes_parameters_to_neon(monkeypatch):
    received = {}

    def fake_retrieve_chunks(query, video_id=None, k=5):
        received.update({
            "query": query,
            "video_id": video_id,
            "k": k,
        })
        return []

    monkeypatch.setattr(
        retriever,
        "neon_retrieve_chunks",
        fake_retrieve_chunks,
    )

    retriever.retrieve_chunks(
        query="swimming",
        video_id="video123456",
        k=5,
    )

    assert received == {
        "query": "swimming",
        "video_id": "video123456",
        "k": 5,
    }


def test_retrieve_chunks_without_video_id(monkeypatch):
    received = {}

    def fake_retrieve_chunks(query, video_id=None, k=5):
        received["video_id"] = video_id
        return []

    monkeypatch.setattr(
        retriever,
        "neon_retrieve_chunks",
        fake_retrieve_chunks,
    )

    retriever.retrieve_chunks(query="swimming")

    assert received["video_id"] is None


def test_retrieve_chunks_rejects_empty_query():
    with pytest.raises(ValueError):
        retriever.retrieve_chunks(query="   ")


def test_retrieve_chunks_rejects_invalid_k():
    with pytest.raises(ValueError):
        retriever.retrieve_chunks(query="swimming", k=0)


def test_retrieve_all_chunks_delegates_to_neon(monkeypatch):
    expected = [{"video_id": "video123456", "text": "Swimming"}]

    monkeypatch.setattr(
        retriever,
        "neon_retrieve_all_chunks",
        lambda video_id: expected,
    )

    assert retriever.retrieve_all_chunks("video123456") == expected


def test_retrieve_all_chunks_rejects_empty_video_id():
    with pytest.raises(ValueError):
        retriever.retrieve_all_chunks("")
