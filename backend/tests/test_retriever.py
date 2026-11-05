import pytest
from types import SimpleNamespace

from app.retrieval import retriever


class FakeVectorStore:
    def __init__(self, documents):
        self.documents = documents
        self.received_query = None
        self.received_k = None
        self.received_filter = None

    def similarity_search(self, query, k, filter=None):
        self.received_query = query
        self.received_k = k
        self.received_filter = filter
        return self.documents


@pytest.fixture
def fake_documents():
    return [
        SimpleNamespace(
            page_content="Freestyle swimming technique",
            metadata={
                "video_id": "video123456",
                "chunk_index": 2,
                "start_time": 10.0,
                "end_time": 20.0,
                "segment_count": 5,
            },
        )
    ]


def test_retrieve_chunks_returns_expected_data(monkeypatch, fake_documents):
    fake_store = FakeVectorStore(fake_documents)

    monkeypatch.setattr(
        retriever,
        "get_vector_store",
        lambda: fake_store,
    )

    result = retriever.retrieve_chunks(
        query="swimming technique",
        video_id="video123456",
        k=3,
    )

    assert len(result) == 1
    assert result[0]["text"] == "Freestyle swimming technique"
    assert result[0]["video_id"] == "video123456"
    assert result[0]["chunk_index"] == 2
    assert result[0]["start_time"] == 10.0
    assert result[0]["end_time"] == 20.0
    assert result[0]["segment_count"] == 5


def test_retrieve_chunks_applies_video_filter(monkeypatch, fake_documents):
    fake_store = FakeVectorStore(fake_documents)

    monkeypatch.setattr(
        retriever,
        "get_vector_store",
        lambda: fake_store,
    )

    retriever.retrieve_chunks(
        query="swimming",
        video_id="video123456",
        k=5,
    )

    assert fake_store.received_filter == {
        "video_id": "video123456"
    }


def test_retrieve_chunks_without_video_id(monkeypatch, fake_documents):
    fake_store = FakeVectorStore(fake_documents)

    monkeypatch.setattr(
        retriever,
        "get_vector_store",
        lambda: fake_store,
    )

    retriever.retrieve_chunks(
        query="swimming",
        k=5,
    )

    assert fake_store.received_filter is None


def test_retrieve_chunks_rejects_empty_query():
    with pytest.raises(ValueError):
        retriever.retrieve_chunks(query="   ")


def test_retrieve_chunks_rejects_invalid_k():
    with pytest.raises(ValueError):
        retriever.retrieve_chunks(
            query="swimming",
            k=0,
        )
