import pytest

from app.processing.transcript_processor import (
    clean_segments,
    create_chunks,
)


def test_clean_segments_removes_empty_text():
    segments = [
        {"text": "Hello", "start": 0, "duration": 2},
        {"text": "   ", "start": 2, "duration": 1},
        {"text": "World", "start": 3, "duration": 2},
    ]

    result = clean_segments(segments)

    assert len(result) == 2
    assert result[0]["text"] == "Hello"
    assert result[1]["text"] == "World"


def test_clean_segments_removes_isolated_music_markers():
    segments = [
        {"text": "Hello", "start": 0, "duration": 2},
        {"text": "[♪♪♪]", "start": 2, "duration": 1},
        {"text": "World", "start": 3, "duration": 2},
    ]

    result = clean_segments(segments)

    assert len(result) == 2
    assert all("♪" not in item["text"] for item in result)


def test_clean_segments_normalizes_whitespace():
    segments = [
        {"text": "  Hello   world  ", "start": 0, "duration": 2},
    ]

    result = clean_segments(segments)

    assert result[0]["text"] == "Hello world"


def test_clean_segments_preserves_original_indices():
    segments = [
        {"text": "Hello", "start": 0, "duration": 2},
        {"text": "", "start": 2, "duration": 1},
        {"text": "World", "start": 3, "duration": 2},
    ]

    result = clean_segments(segments)

    assert result[0]["segment_index"] == 0
    assert result[1]["segment_index"] == 2


def test_create_chunks_preserves_timestamps():
    segments = [
        {
            "segment_index": 0,
            "text": "Hello world",
            "start": 10.0,
            "duration": 2.0,
        },
        {
            "segment_index": 1,
            "text": "How are you",
            "start": 12.0,
            "duration": 3.0,
        },
    ]

    result = create_chunks(
        segments,
        chunk_size=100,
        overlap=10,
    )

    assert len(result) == 1
    assert result[0]["start_time"] == 10.0
    assert result[0]["end_time"] == 15.0


def test_create_chunks_preserves_segment_indices():
    segments = [
        {
            "segment_index": 4,
            "text": "Hello",
            "start": 0.0,
            "duration": 1.0,
        },
        {
            "segment_index": 5,
            "text": "World",
            "start": 1.0,
            "duration": 1.0,
        },
    ]

    result = create_chunks(
        segments,
        chunk_size=100,
        overlap=10,
    )

    assert result[0]["segment_indices"] == [4, 5]


def test_create_chunks_rejects_invalid_chunk_size():
    with pytest.raises(ValueError):
        create_chunks([], chunk_size=0)


def test_create_chunks_rejects_invalid_overlap():
    segments = [
        {
            "segment_index": 0,
            "text": "Hello",
            "start": 0.0,
            "duration": 1.0,
        },
    ]

    with pytest.raises(ValueError):
        create_chunks(segments, chunk_size=100, overlap=100)