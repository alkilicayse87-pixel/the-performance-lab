import pytest
from app.ingestion import youtube_transcript


@pytest.mark.parametrize(
    "url",
    [
        "https://www.youtube.com/watch?v=abcdefghijk",
        "https://youtu.be/abcdefghijk",
        "https://www.youtube.com/shorts/abcdefghijk",
        "https://www.youtube.com/embed/abcdefghijk",
    ],
)
def test_extract_video_id_valid_urls(url):
    assert youtube_transcript.extract_video_id(url) == "abcdefghijk"


@pytest.mark.parametrize(
    "url",
    [
        "https://example.com/watch?v=abcdefghijk",
        "https://www.youtube.com/watch?v=invalid",
        "https://www.youtube.com/unsupported/abcdefghijk",
    ],
)
def test_extract_video_id_invalid_urls(url):
    with pytest.raises(ValueError):
        youtube_transcript.extract_video_id(url)


def test_fetch_youtube_transcript(monkeypatch):
    class FakeTranscript:
        video_id = "abcdefghijk"
        language = "English"
        language_code = "en"
        is_generated = False

        def to_raw_data(self):
            return [
                {
                    "text": "Hello world",
                    "start": 0.0,
                    "duration": 2.0,
                }
            ]

    class FakeYouTubeTranscriptApi:
        def fetch(self, video_id, languages):
            assert video_id == "abcdefghijk"
            assert languages == ["en"]
            return FakeTranscript()

    monkeypatch.setattr(
        youtube_transcript,
        "YouTubeTranscriptApi",
        FakeYouTubeTranscriptApi,
    )

    result = youtube_transcript.fetch_youtube_transcript("abcdefghijk")

    assert result["video_id"] == "abcdefghijk"
    assert result["language"] == "English"
    assert result["language_code"] == "en"
    assert result["is_generated"] is False
    assert len(result["segments"]) == 1
    assert result["segments"][0]["text"] == "Hello world"