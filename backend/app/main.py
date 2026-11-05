from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from openai import OpenAIError

from app.services.video_service import ingest_youtube_video
from app.config import OPENAI_MODEL
from app.services.agent_service import generate_agent_answer

app = FastAPI(
    title="AI Video Knowledge Assistant",
    description="Turn any YouTube video into knowledge you can explore.",
    version="0.1.0",
)


class VideoIngestRequest(BaseModel):
    youtube_url: str = Field(
        min_length=1,
        description="The YouTube video URL",
    )


class ChatRequest(BaseModel):
    video_id: str = Field(
        min_length=11,
        max_length=11,
        description="The YouTube video ID",
    )

    conversation_id: str = Field(
        min_length=1,
        max_length=128,
        description="The conversation identifier",
    )

    message: str = Field(
        min_length=1,
        max_length=5000,
        description="The user's question",
    )


@app.get("/")
def root():
    return {
        "message": "AI Video Knowledge Assistant is running!",
        "status": "success",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "application": "AI Video Knowledge Assistant",
    }


@app.post("/videos/ingest")
def ingest_video(request: VideoIngestRequest):
    try:
        result = ingest_youtube_video(
            youtube_url=request.youtube_url,
        )

        return result

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="The video could not be processed.",
        )


@app.post(
    "/agent-chat",
    description="Ask questions about an ingested YouTube video using the LangGraph agent.",
)
def agent_chat(request: ChatRequest):
    try:
        answer = generate_agent_answer(
            message=request.message,
            video_id=request.video_id,
            conversation_id=request.conversation_id,
        )

        return {
            "question": request.message,
            "video_id": request.video_id,
            "conversation_id": request.conversation_id,
            "answer": answer,
            "model": OPENAI_MODEL,
            "agent": "LangGraph",
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except OpenAIError:
        raise HTTPException(
            status_code=502,
            detail="The AI service could not process the request.",
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="The agent could not process the request.",
        )