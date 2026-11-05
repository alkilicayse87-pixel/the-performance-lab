from langchain.tools import tool, ToolRuntime

from app.agents.context import AgentContext

from app.tools.transcript_search import search_video_transcript
from app.tools.video_summarizer import summarize_video
from app.tools.video_references import get_video_references


@tool
def search_transcript(
    query: str,
    runtime: ToolRuntime[AgentContext],
) -> list[dict]:
    """
    Search the current video's transcript for information
    relevant to the user's question.
    """

    video_id = runtime.context["video_id"]

    return search_video_transcript.invoke({
        "query": query,
        "video_id": video_id,
    })


@tool
def summarize_current_video(
    summary_type: str,
    runtime: ToolRuntime[AgentContext],
) -> str:
    """
    Generate a summary of the current video.

    Supported types: quick, detailed, key_takeaways.
    """

    video_id = runtime.context["video_id"]

    return summarize_video.invoke({
        "video_id": video_id,
        "summary_type": summary_type,
    })


@tool
def retrieve_video_references(
    query: str,
    runtime: ToolRuntime[AgentContext],
) -> str:
    """
    Retrieve relevant transcript passages and timestamps
    from the current video.
    """

    video_id = runtime.context["video_id"]

    return get_video_references.invoke({
        "query": query,
        "video_id": video_id,
    })