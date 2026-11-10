from pathlib import Path

from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.messages import ToolMessage

from app.agents.agent import create_video_agent


# Persistent database location
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATABASE_DIRECTORY = PROJECT_ROOT / "storage"
DATABASE_PATH = DATABASE_DIRECTORY / "agent_checkpoints.sqlite"


def _invoke_agent(
    message: str,
    video_id: str,
    conversation_id: str,
) -> list:
    """Run the agent and return its messages."""

    if not message.strip():
        raise ValueError("Message cannot be empty.")

    if not video_id:
        raise ValueError("Video ID cannot be empty.")

    if not conversation_id:
        raise ValueError("Conversation ID cannot be empty.")

    DATABASE_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    thread_id = f"{conversation_id}:{video_id}"

    with SqliteSaver.from_conn_string(
        str(DATABASE_PATH)
    ) as checkpointer:

        agent = create_video_agent(checkpointer)

        result = agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": message,
                    }
                ]
            },
            config={
                "configurable": {
                    "thread_id": thread_id,
                }
            },
            context={
                "video_id": video_id,
            },
        )

    return result["messages"]


def generate_agent_answer(
    message: str,
    video_id: str,
    conversation_id: str,
) -> str:
    """Generate an answer using the agent and persistent memory."""

    messages = _invoke_agent(
        message=message,
        video_id=video_id,
        conversation_id=conversation_id,
    )

    return messages[-1].content


def generate_agent_answer_with_evidence(
    message: str,
    video_id: str,
    conversation_id: str,
) -> dict:
    """Generate an answer and collect actual tool outputs."""

    messages = _invoke_agent(
        message=message,
        video_id=video_id,
        conversation_id=conversation_id,
    )

    answer = messages[-1].content

    tool_evidence = []

    for message in messages:
        if isinstance(message, ToolMessage):
            tool_evidence.append({
                "tool_name": message.name,
                "content": message.content,
            })

    return {
        "answer": answer,
        "tool_evidence": tool_evidence,
    }