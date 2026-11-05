# AI Video Knowledge Assistant

**Turn any YouTube video into knowledge you can explore.**

## Overview

AI Video Knowledge Assistant is a general-purpose AI application that allows users to ask questions about YouTube videos using natural language.

It retrieves and processes video transcripts, then uses Retrieval-Augmented Generation (RAG) and a LangGraph-powered agent to provide contextual answers, summaries, and timestamp-based references.

## Key Features

- YouTube transcript retrieval and processing
- Semantic search using vector embeddings
- AI-powered question answering
- Video summaries and key takeaways
- Timestamp-based references
- Conversational memory with LangGraph

## Tech Stack

- **Backend:** Python, FastAPI
- **AI:** OpenAI API, LangChain, LangGraph
- **Vector Database:** ChromaDB
- **Embeddings:** OpenAI `text-embedding-3-small`
- **Memory:** LangGraph SQLite Checkpointer
- **Testing:** Pytest, HTTPX

## Architecture

The application follows a RAG architecture:

1. Retrieve the YouTube transcript.
2. Clean and split it into timestamp-aware chunks.
3. Generate embeddings and store them in ChromaDB.
4. Retrieve relevant content based on user questions.
5. Use the LangGraph agent to select tools and generate answers grounded in the transcript.

## Installation

**1. Clone the repository**

```bash
git clone https://github.com/ivanmatteuzzi/AI-video-knowledge-assistant.git
cd AI-video-knowledge-assistant
```

**2. Set up the environment**

```bash
cd backend
python -m venv venv
```

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Configure environment variables**

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-5.4-mini
```

**5. Start the application**

From the `backend` directory:

```bash
python -m uvicorn app.main:app --reload
```

API documentation: `http://127.0.0.1:8000/docs`

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Application status |
| GET | `/health` | Health check |
| POST | `/videos/ingest` | Process a YouTube video |
| POST | `/agent-chat` | Ask questions about a video |

## Current Limitations

- Only spoken content is analysed; video frames and visual elements are not supported.
- Automatic speech-to-text fallback is not implemented.
- Answers about video content are grounded in the available transcript.

## Testing

Run the test suite from the `backend` directory:

```bash
python -m pytest tests/
```