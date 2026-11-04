
import re


def clean_segments(segments: list[dict]) -> list[dict]:
    """
    Remove empty segments and isolated music markers.
    Preserve timestamps and original segment indices.
    """

    cleaned_segments = []

    for segment_index, segment in enumerate(segments):
        text = re.sub(r"\s+", " ", segment["text"]).strip()

        # Skip empty text
        if not text:
            continue

        # Skip isolated musical notation, such as [♪♪♪]
        if re.fullmatch(r"\[[♪♫]+\]", text):
            continue

        cleaned_segments.append({
            "segment_index": segment_index,
            "text": text,
            "start": float(segment["start"]),
            "duration": float(segment["duration"]),
        })

    return cleaned_segments


def create_chunks(
    segments: list[dict],
    chunk_size: int = 1000,
    overlap: int = 150,
) -> list[dict]:
    """
    Group transcript segments into overlapping chunks.
    Preserve timestamps and original segment indices.
    """

    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive.")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be >= 0 and smaller than chunk_size.")

    chunks = []
    current_segments = []
    current_length = 0

    def save_chunk(items):
        text = " ".join(item["text"] for item in items)

        chunks.append({
            "chunk_index": len(chunks),
            "text": text,
            "start_time": items[0]["start"],
            "end_time": items[-1]["start"] + items[-1]["duration"],
            "segment_count": len(items),
            "segment_indices": [
                item["segment_index"] for item in items
            ],
        })

    for segment in segments:
        segment_length = len(segment["text"]) + (
            1 if current_segments else 0
        )

        if current_segments and current_length + segment_length > chunk_size:
            save_chunk(current_segments)

            # Keep the last segments as overlap for the next chunk
            overlap_segments = []
            overlap_length = 0

            for item in reversed(current_segments):
                item_length = len(item["text"]) + 1

                if overlap_segments and overlap_length + item_length > overlap:
                    break

                overlap_segments.insert(0, item)
                overlap_length += item_length

            current_segments = overlap_segments
            current_length = sum(
                len(item["text"]) + 1 for item in current_segments
            )

        current_segments.append(segment)
        current_length += len(segment["text"]) + (
            1 if len(current_segments) > 1 else 0
        )

    if current_segments:
        save_chunk(current_segments)

    return chunks
