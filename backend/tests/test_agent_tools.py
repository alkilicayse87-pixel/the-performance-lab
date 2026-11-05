import pytest

from types import SimpleNamespace

from app.agents import agent_tools


@pytest.fixture
def runtime():
    return SimpleNamespace(
        context={"video_id": "abcdefghijk"}
    )


def test_search_transcript_uses_video_context(monkeypatch, runtime):
    captured = {}

    def fake_search(arguments):
        captured.update(arguments)
        return [{"text": "Swimming technique"}]

    monkeypatch.setattr(
        agent_tools,
        "search_video_transcript",
        SimpleNamespace(invoke=fake_search),
    )

    result = agent_tools.search_transcript.func(
        query="swimming technique",
        runtime=runtime,
    )

    assert captured == {
        "query": "swimming technique",
        "video_id": "abcdefghijk",
    }

    assert result == [{"text": "Swimming technique"}]


def test_summarize_video_uses_video_context(monkeypatch, runtime):
    captured = {}

    def fake_summary(arguments):
        captured.update(arguments)
        return "Video summary"

    monkeypatch.setattr(
        agent_tools,
        "summarize_video",
        SimpleNamespace(invoke=fake_summary),
    )

    result = agent_tools.summarize_current_video.func(
        summary_type="detailed",
        runtime=runtime,
    )

    assert captured == {
        "video_id": "abcdefghijk",
        "summary_type": "detailed",
    }

    assert result == "Video summary"


def test_retrieve_references_uses_video_context(monkeypatch, runtime):
    captured = {}

    def fake_references(arguments):
        captured.update(arguments)
        return "Reference at 01:20"

    monkeypatch.setattr(
        agent_tools,
        "get_video_references",
        SimpleNamespace(invoke=fake_references),
    )

    result = agent_tools.retrieve_video_references.func(
        query="breathing technique",
        runtime=runtime,
    )

    assert captured == {
        "query": "breathing technique",
        "video_id": "abcdefghijk",
    }

    assert result == "Reference at 01:20"