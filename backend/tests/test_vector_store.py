import pytest

from app.vector_store import chroma_store


@pytest.fixture
def sample_chunks():
    return [
        {
            "chunk_index": 0,
            "text": "Freestyle swimming technique",
            "start_time": 10.0,
            "end_time": 20.0,
            "segment_count": 3,
            "segment_indices": [0, 1, 2],
        },
        {
            "chunk_index": 1,
            "text": "Breathing and body position",
            "start_time": 20.0,
            "end_time": 30.0,
            "segment_count": 2,
            "segment_indices": [3, 4],
        },
    ]


def test_generate_chunk_id_is_deterministic(sample_chunks):
    first_id = chroma_store.generate_chunk_id(
        "video123456",
        sample_chunks[0],
    )

    second_id = chroma_store.generate_chunk_id(
        "video123456",
        sample_chunks[0],
    )

    assert first_id == second_id


def test_generate_chunk_id_changes_with_video_id(sample_chunks):
    first_id = chroma_store.generate_chunk_id(
        "video123456",
        sample_chunks[0],
    )

    second_id = chroma_store.generate_chunk_id(
        "video654321",
        sample_chunks[0],
    )

    assert first_id != second_id


def test_add_video_chunks_creates_documents_and_ids(
    monkeypatch,
    sample_chunks,
):
    captured = {}

    class FakeVectorStore:
        def add_documents(self, documents, ids):
            captured["documents"] = documents
            captured["ids"] = ids

    fake_store = FakeVectorStore()

    monkeypatch.setattr(
        chroma_store,
        "get_vector_store",
        lambda: fake_store,
    )

    result = chroma_store.add_video_chunks(
        video_id="video123456",
        chunks=sample_chunks,
    )

    documents = captured["documents"]

    assert len(documents) == 2
    assert len(captured["ids"]) == 2
    assert result == captured["ids"]

    assert documents[0].page_content == "Freestyle swimming technique"
    assert documents[0].metadata["video_id"] == "video123456"
    assert documents[0].metadata["chunk_index"] == 0
    assert documents[0].metadata["segment_indices"] == "0,1,2"


def test_add_video_chunks_rejects_empty_video_id():
    with pytest.raises(ValueError):
        chroma_store.add_video_chunks(
            video_id="",
            chunks=[{"chunk_index": 0, "text": "Test"}],
        )


def test_add_video_chunks_rejects_empty_chunks():
    with pytest.raises(ValueError):
        chroma_store.add_video_chunks(
            video_id="video123456",
            chunks=[],
        )
