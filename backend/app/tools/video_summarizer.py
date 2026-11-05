from langchain.tools import tool

from app.retrieval.retriever import retrieve_all_chunks
from app.config import OPENAI_API_KEY, OPENAI_MODEL

from openai import OpenAI


client = OpenAI(api_key=OPENAI_API_KEY)


@tool
def summarize_video(
    video_id: str,
    summary_type: str = "detailed",
) -> str:
    """
    Generate a summary of a YouTube video's spoken content.

    Supported summary types:
    - quick: A short overview of the video.
    - detailed: A structured summary of the main topics.
    - key_takeaways: A list of the most important points.

    Use this tool when the user asks for a video summary.
    """

    if summary_type not in {
        "quick",
        "detailed",
        "key_takeaways",
    }:
        raise ValueError("Unsupported summary type.")

    chunks = retrieve_all_chunks(video_id=video_id)

    if not chunks:
        return "No transcript information was found for this video."

    transcript_context = "\n\n".join(
        f"[{chunk['start_time']:.1f}s - {chunk['end_time']:.1f}s]\n"
        f"{chunk['text']}"
        for chunk in sorted(
            chunks,
            key=lambda item: item["start_time"],
        )
    )

    summary_instructions = {
        "quick": "Provide a concise overview in one short paragraph.",
        "detailed": "Provide a structured summary covering the main topics and explanations.",
        "key_takeaways": "Provide a bullet-point list of the most important takeaways.",
    }

    response = client.responses.create(
        model=OPENAI_MODEL,
        instructions=(
            "Summarize only the information contained in the transcript. "
            "Do not invent facts or introduce external information. "
            "Include timestamps when relevant."
        ),
        input=(
            f"{summary_instructions[summary_type]}\n\n"
            f"VIDEO TRANSCRIPT:\n{transcript_context}"
        ),
    )

    return response.output_text