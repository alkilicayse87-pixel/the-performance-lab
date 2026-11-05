from langchain.tools import tool

from app.retrieval.retriever import retrieve_chunks


@tool
def search_video_transcript(
    query: str,
    video_id: str,
) -> list[dict]:
    """
    Search the transcript of a specific YouTube video.

    Retrieve relevant passages from the spoken content
    based on the user's question.

    Return transcript passages with their timestamps.
    """

    return retrieve_chunks(
        query=query,
        video_id=video_id,
        k=5,
    )