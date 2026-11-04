
import re
from urllib.parse import urlparse, parse_qs

from youtube_transcript_api import YouTubeTranscriptApi


def extract_video_id(url: str) -> str:
    """
    Extract and validate the video ID from a YouTube URL.
    Supports standard, shortened, Shorts and embed URLs.
    """

    parsed_url = urlparse(url.strip())

    hostname = (parsed_url.hostname or "").lower()

    allowed_domains = {
        "youtube.com",
        "www.youtube.com",
        "m.youtube.com",
        "music.youtube.com",
        "youtu.be",
        "www.youtu.be",
    }

    if hostname not in allowed_domains:
        raise ValueError("Invalid YouTube URL.")

    if hostname.endswith("youtu.be"):
        video_id = parsed_url.path.strip("/")

    elif parsed_url.path == "/watch":
        video_id = parse_qs(parsed_url.query).get("v", [""])[0]

    elif parsed_url.path.startswith(("/shorts/", "/embed/")):
        video_id = parsed_url.path.split("/")[2]

    else:
        raise ValueError("Unsupported YouTube URL format.")

    if not re.fullmatch(r"[A-Za-z0-9_-]{11}", video_id):
        raise ValueError("Invalid YouTube video ID.")

    return video_id


def fetch_youtube_transcript(
    video_id: str,
    languages: list[str] | None = None,
) -> dict:
    """
    Fetch a YouTube transcript and preserve segment timestamps.
    """

    if languages is None:
        languages = ["en"]

    transcript_api = YouTubeTranscriptApi()

    fetched_transcript = transcript_api.fetch(
        video_id,
        languages=languages,
    )

    segments = fetched_transcript.to_raw_data()

    return {
        "video_id": fetched_transcript.video_id,
        "language": fetched_transcript.language,
        "language_code": fetched_transcript.language_code,
        "is_generated": fetched_transcript.is_generated,
        "segments": segments,
    }