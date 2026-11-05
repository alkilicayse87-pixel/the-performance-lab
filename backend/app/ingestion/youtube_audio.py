import tempfile
from pathlib import Path

import yt_dlp
from openai import OpenAI

from app.config import OPENAI_API_KEY


MAX_AUDIO_SIZE = 25 * 1024 * 1024
TRANSCRIPTION_MODEL = "whisper-1"

client = OpenAI(api_key=OPENAI_API_KEY)


def transcribe_youtube_audio(video_id: str) -> dict:
    """
    Download YouTube audio and transcribe it with OpenAI.
    Preserve segment-level timestamps.
    """

    with tempfile.TemporaryDirectory() as temp_dir:
        output_template = str(Path(temp_dir) / "%(id)s.%(ext)s")

        ydl_options = {
            "format": "bestaudio[ext=m4a]/bestaudio",
            "outtmpl": output_template,
            "quiet": True,
            "no_warnings": True,
        }

        with yt_dlp.YoutubeDL(ydl_options) as ydl:
            info = ydl.extract_info(
                f"https://www.youtube.com/watch?v={video_id}",
                download=True,
            )
            audio_path = Path(ydl.prepare_filename(info))

        if not audio_path.exists():
            raise FileNotFoundError("Downloaded audio file not found.")

        if audio_path.stat().st_size > MAX_AUDIO_SIZE:
            raise ValueError(
                "Audio file exceeds OpenAI's 25 MB transcription limit."
            )

        with audio_path.open("rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model=TRANSCRIPTION_MODEL,
                file=audio_file,
                response_format="verbose_json",
                timestamp_granularities=["segment"],
            )

        segments = [
            {
                "text": segment.text,
                "start": segment.start,
                "duration": segment.end - segment.start,
            }
            for segment in transcription.segments
        ]

        return {
            "video_id": video_id,
            "language": transcription.language,
            "language_code": transcription.language,
            "is_generated": True,
            "segments": segments,
        }
