from typing import TypedDict


class AgentContext(TypedDict):
    """
    Context shared with the agent and its tools.
    """

    video_id: str