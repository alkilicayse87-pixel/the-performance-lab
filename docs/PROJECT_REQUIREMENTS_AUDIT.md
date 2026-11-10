# Ironhack Final Project Requirements Audit

**Scope:** Repository evidence only. A source implementation is not equivalent to a verified production deployment. Statuses distinguish capability in code from missing data or unverified live operation.

| Requirement | Status | Evidence file/function | How to demonstrate | Remaining gap | Priority |
|---|---|---|---|---|---|
| 1. Text-based question answering | **LOCALLY SMOKE-TESTED** | `backend/app/main.py` `agent_chat`; `backend/app/services/agent_service.py` | Ask a transcript-based question for each indexed video. | Three new videos returned agent answers locally; deployed results were not tested. | High |
| 2. YouTube ingestion and preprocessing | **LOCALLY SMOKE-TESTED** | `backend/app/ingestion/youtube_transcript.py`; `backend/app/processing/transcript_processor.py`; `backend/scripts/build_video_catalog.py`; `backend/app/services/video_service.py` | Run the catalog-build workflow with required external access; inspect resulting JSON and Chroma records. | The three new videos were indexed locally. Runtime endpoint only accepts preloaded videos; deployed indexing is still required. | High |
| 3. Audio/speech recognition | **IMPLEMENTED; LIVE TEST REPORTED BY TEACHER** | `frontend/src/app/page.tsx` `toggleRecording`; `backend/app/main.py` `/transcribe`; `backend/app/ingestion/youtube_audio.py` | Teacher feedback supplied by the owner says Whisper voice input was tested live. Repeat the demo on the current deployment if possible. | The teacher's earlier review is not a reproducible test record; no audio endpoint unit tests. Whisper is external and size-limited. | Low |
| 4. Conversational UI | **NINE VIDEO OPTIONS IMPLEMENTED IN SOURCE** | `frontend/src/app/page.tsx` | Open the site, select an indexed catalog card, type a question, and observe messages/status. | The new cards require deployment and their index must be provisioned in the deployed backend. | High |
| 5. Vector DB and RAG | **NEW VIDEOS SMOKE-TESTED LOCALLY** | `backend/app/vector_store/chroma_store.py`; `backend/app/retrieval/retriever.py` | Ask a question and inspect retrieved chunks. | The local Chroma index is not tracked by Git; deployed indexing and answer quality remain unverified. | High |
| 6. Agent with several tools | **VERIFIED IMPLEMENTED IN SOURCE** | `backend/app/agents/agent.py`; `backend/app/agents/agent_tools.py` | Ask a factual question, request a summary, and request timestamps; inspect traces/tool outputs if tracing is enabled. | No live tool-selection trace verified. Tools are search, full-video summary, references. | Medium |
| 7. Conversational memory | **IMPLEMENTED IN CODE; DEPLOYMENT PERSISTENCE UNVERIFIED** | `backend/app/services/agent_service.py` | Send a follow-up with the same conversation/video IDs and compare; restart service to test persistence. | SQLite is local to `backend/storage`; Render disk persistence and user/session isolation are not established. Frontend uses a stable per-video ID. | High |
| 8. LangChain integration | **VERIFIED IMPLEMENTED** | `backend/app/agents/agent.py`; `backend/app/vector_store/chroma_store.py`; `backend/app/tools/` | Inspect agent/tools and execute a configured request. | Runtime behavior requires packages, credentials, and indexed data. | Low |
| 9. LangSmith tracing, testing, evaluation | **TRACING/EVALUATION CODE PRESENT; SYSTEMATIC RESULTS NOT VERIFIED** | `.env.example`; `backend/evaluation/langsmith_dataset.py`; `backend/evaluation/langsmith_evaluation.py`; `backend/evaluation/langsmith_answer_evaluation.py` | Configure credentials, run the 12-example retrieval and answer-quality datasets across the six videos, and preserve experiment links/results. | Teacher feedback identifies systematic answer-quality and retrieval evaluation as the main remaining gap. Environment key names differ (`LANGCHAIN_API_KEY` vs `LANGSMITH_API_KEY`); results were not available in this audit. | **Highest** |
| 10. Deployed web application | **DEPLOYMENT REPORTED BY TEACHER; SOURCE CONFIGURATION PRESENT** | URL supplied in task; `frontend/src/app/page.tsx` API URL; `backend/app/main.py` CORS origins | Open the supplied URL and exercise selection, chat, and voice; save a dated smoke-test record. | Teacher feedback says the project was already deployed at the time of review; current uptime, backend index, deployment manifests, and persistence were not independently checked here. | Medium |
| 11. Automated tests and performance evaluation | **48 BACKEND TESTS PASSED LOCALLY** | `backend/tests/`; `backend/evaluation/retrieval_evaluation.py` | Run the suite in an isolated environment and preserve evaluation results. | Teacher's earlier review reported 44 passing tests; the expanded suite passed 48 locally. No latency or LangSmith evaluation scores were measured. | Medium |
| 12. Technical documentation | **PARTIALLY IMPLEMENTED** | Root `README.md`; proposed docs in this folder | Review and approve README draft; run setup instructions from a clean clone. | Existing README is stale relative to current catalog-only and audio behavior; drafts need owner review. | High |
| 13. Final presentation readiness | **PARTIALLY IMPLEMENTED** | `docs/PRESENTATION_OUTLINE.md` | Rehearse a demo and present only verified test/deployment results. | Need owner-confirmed personal reflection, live demo, screenshots, and actual evaluation outputs. | Medium |

## Evidence update from teacher feedback

The project owner shared a teacher review of an earlier version/deployment. It describes the ChromaDB retrieval, LangChain/LangGraph agent and three tools, SQLite memory, live-tested Whisper input, an existing deployment, and 44 passing tests. It recommends prioritizing systematic LangSmith answer-quality and retrieval-accuracy evaluation before documentation and presentation. These are **teacher-reported results**, not independently reproduced during this repository audit; the exact test command, commit, test output, deployment date, and LangSmith experiment results were not included.

The audit's earlier test attempt failed at environment setup. A later run in an isolated environment passed 48 backend tests, including four new catalog tests.

## Strict findings

- The frontend and catalog builder now list nine videos: the six original entries and three wellness videos. The backend verifies that a selected video's Chroma chunks already exist. The endpoint name `/videos/ingest` can therefore be mistaken for arbitrary live ingestion.
- Six original transcript JSON files are tracked. The new wellness transcripts and local Chroma index were generated later and are ignored by Git. Runtime retrieval uses Chroma, not JSON files directly.
- The project has three agent tools and a conversational checkpointer in source. Local agent smoke tests for the three new videos each returned an answer and a transcript-search tool output.
- Teacher feedback reports 44 passing tests for the earlier version. A later isolated-environment run passed 48 backend tests.
- LangSmith evaluation code and a 12-item dataset exist. Evaluation runs and scores were not verified.
- The teacher review reports an existing deployment; the URL and source URL/CORS configuration support that claim, but current availability and backend data persistence were not independently checked.
- Existing root README states that automatic speech-to-text fallback is not implemented and general video processing is available; those statements conflict with current source in opposite ways. User questions are transcribed, while runtime video ingestion is restricted to the catalog.

## Demonstration checklist

1. Confirm production frontend and API are reachable.
2. Select each supported video or at minimum one known-good sample.
3. Ask a transcript-grounded question, then a follow-up, and show source time references.
4. Request a summary to exercise the separate summary tool.
5. Record a short question, review the transcription, then submit.
6. Show a request for a non-catalog video and explain the current limitation.
7. Present actual backend test output and LangSmith experiment links, if available.
8. Explain that this is educational, transcript-only assistance, not health diagnosis or individualized medical guidance.
