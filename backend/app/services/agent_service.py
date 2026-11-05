from pathlib import Path

from langgraph.checkpoint.sqlite import SqliteSaver

from app.agents.agent import create_video_agent


# Persistent database location
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATABASE_DIRECTORY = PROJECT_ROOT / "storage"
DATABASE_PATH = DATABASE_DIRECTORY / "agent_checkpoints.sqlite"


def generate_agent_answer(
    message: str,
    video_id: str,
    conversation_id: str,
) -> str:
    """
    Generate an answer using the LangGraph agent
    and persistent conversation memory.
    """

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

    # A separate thread is used for each conversation and video
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

    return result["messages"][-1].content