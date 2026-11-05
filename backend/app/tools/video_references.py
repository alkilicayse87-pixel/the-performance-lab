from langchain.tools import tool

from app.retrieval.retriever import retrieve_chunks


@tool
def get_video_references(
    query: str,
    video_id: str,
) -> str:
    """
    Retrieve relevant video transcript references.

    Return an organized list of relevant passages,
    including timestamps and transcript excerpts.
    """

    chunks = retrieve_chunks(
        query=query,
        video_id=video_id,
        k=5,
    )

    if not chunks:
        return "No relevant video references were found."

    sorted_chunks = sorted(
        chunks,
        key=lambda item: item["start_time"],
    )

    references = []

    for index, chunk in enumerate(sorted_chunks, start=1):

        start = int(chunk["start_time"])
        end = int(chunk["end_time"])

        start_time = (
            f"{start // 3600:02d}:"
            f"{(start % 3600) // 60:02d}:"
            f"{start % 60:02d}"
        )

        end_time = (
            f"{end // 3600:02d}:"
            f"{(end % 3600) // 60:02d}:"
            f"{end % 60:02d}"
        )

        reference = (
            f"Reference {index}\n"
            f"- Timestamp: {start_time} – {end_time}\n"
            f"- Transcript excerpt: {chunk['text']}\n"
        )

        references.append(reference)

    return "\n".join(references)