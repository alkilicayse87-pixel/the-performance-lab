from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from openai import OpenAIError

from app.services.chat_service import generate_answer
from app.services.video_service import ingest_youtube_video
from app.config import OPENAI_MODEL


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


@app.post("/chat")
def chat(request: ChatRequest):
    try:
        answer = generate_answer(
            message=request.message,
            video_id=request.video_id,
        )

        return {
            "question": request.message,
            "video_id": request.video_id,
            "answer": answer,
            "model": OPENAI_MODEL,
        }

    except OpenAIError:
        raise HTTPException(
            status_code=502,
            detail="The AI service could not process the request.",
        )