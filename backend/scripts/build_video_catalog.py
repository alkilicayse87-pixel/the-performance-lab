
import argparse
import json
from pathlib import Path

from app.ingestion.youtube_transcript import fetch_youtube_transcript
from app.processing.transcript_processor import clean_segments, create_chunks
from app.vector_store.chroma_store import get_vector_store, add_video_chunks


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TRANSCRIPTS_DIR = PROJECT_ROOT / "storage" / "transcripts"

VIDEOS = [
    {"title": "How Playing Sports Benefits Your Body and Your Brain", "video_id": "hmFQqjMF_f0"},
    {"title": "The Brain-Changing Benefits of Exercise", "video_id": "BHY0FxzoKZE"},
    {"title": "How the Heart Changes with Exercise", "video_id": "OM-AeVyW1kk"},
    {"title": "Reduce Your Risk of Injury", "video_id": "Att-yGdYfgI"},
    {"title": "Recovery Strategies for Athletes", "video_id": "W2-UL8P610k"},
    {"title": "What is Strength?", "video_id": "nUsmc4FgfBE"},
    {"title": "Sleep Toolkit: Tools for Optimizing Sleep & Sleep-Wake Timing", "video_id": "h2aWYjSA1Jc"},
    {"title": "Food is Fuel: Nutrients for Endurance, Optimal Sports Nutrition, and Handling Plateaus", "video_id": "mLn2X2JSrbg"},
    {"title": "How to Make Stress Your Friend", "video_id": "RcGyVTAoXEU"},
]

OLD_VIDEO_ID = "KTDGYjcR0Yc"


def main(video_ids: list[str] | None = None):
    if video_ids is None:
        videos_to_process = VIDEOS
    else:
        videos_by_id = {
            video["video_id"]: video
            for video in VIDEOS
        }
        unknown_video_ids = set(video_ids) - videos_by_id.keys()

        if unknown_video_ids:
            raise ValueError(
                "Unknown video IDs: "
                + ", ".join(sorted(unknown_video_ids))
            )

        videos_to_process = [
            videos_by_id[video_id]
            for video_id in dict.fromkeys(video_ids)
        ]

        if not videos_to_process:
            raise ValueError("At least one video ID must be provided.")

    TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)

    prepared_videos = []

    # 1. Fetch and prepare all catalog transcripts.
    for video in videos_to_process:
        video_id = video["video_id"]
        print(f"\nProcessing: {video['title']}")

        transcript = fetch_youtube_transcript(
            video_id=video_id,
            languages=["en"],
        )

        cleaned = clean_segments(transcript["segments"])

        if not cleaned:
            raise ValueError(f"No usable transcript for {video_id}")

        chunks = create_chunks(
            segments=cleaned,
            chunk_size=1000,
            overlap=150,
        )

        if not chunks:
            raise ValueError(f"No chunks created for {video_id}")

        prepared_videos.append({
            **video,
            "transcript": transcript,
            "cleaned_segments": cleaned,
            "chunks": chunks,
        })

        print(
            f"Segments: {len(transcript['segments'])} | "
            f"Cleaned: {len(cleaned)} | "
            f"Chunks: {len(chunks)}"
        )

    # 2. Save the original transcript data locally.
    for video in prepared_videos:
        video_id = video["video_id"]

        output = {
            "video_id": video_id,
            "title": video["title"],
            "language": video["transcript"]["language"],
            "language_code": video["transcript"]["language_code"],
            "is_generated": video["transcript"]["is_generated"],
            "segments": video["transcript"]["segments"],
        }

        path = TRANSCRIPTS_DIR / f"{video_id}.json"
        path.write_text(
            json.dumps(output, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    # 3. Remove old and existing entries to avoid duplicates.
    vector_store = get_vector_store()

    video_ids_to_refresh = [
        *(
            [OLD_VIDEO_ID]
            if video_ids is None
            else []
        ),
        *[video["video_id"] for video in videos_to_process],
    ]

    for video_id in video_ids_to_refresh:
        vector_store.delete(where={"video_id": video_id})

    # 4. Index the validated videos.
    total_chunks = 0

    for video in prepared_videos:
        stored_ids = add_video_chunks(
            video_id=video["video_id"],
            chunks=video["chunks"],
        )

        total_chunks += len(stored_ids)
        print(f"Indexed: {video['title']} | Chunks: {len(stored_ids)}")

    print("\nCATALOG BUILD COMPLETED")
    print(f"Videos: {len(prepared_videos)}")
    print(f"Total indexed chunks: {total_chunks}")
    print(f"Transcripts saved in: {TRANSCRIPTS_DIR}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Build or refresh the YouTube video transcript catalog."
    )
    parser.add_argument(
        "--video-ids",
        nargs="+",
        help="Refresh only these catalog video IDs, preserving other indexed videos.",
    )
    arguments = parser.parse_args()
    main(video_ids=arguments.video_ids)
