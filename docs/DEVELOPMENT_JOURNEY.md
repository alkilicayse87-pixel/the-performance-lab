# Development Journey and Challenges

## Timeline supported by Git history

The timeline below is limited to commit dates and subjects visible in repository history. Commit subjects do not prove the motivation, exact work completed, or the developer's personal experience.

| Date | Commit | Evidence-supported milestone |
|---|---|---|
| 2026-11-04 | `d822e1d` — Initial project setup and RAG implementation | Initial setup and RAG are named in the subject. |
| 2026-11-05 | `4ed823c` — Implement LangGraph agent and update project documentation | Agent integration milestone. |
| 2026-11-05 | `32b6f55` — Add YouTube audio transcription fallback and transcript caching | Audio fallback and caching work named in history. Current code has a YouTube audio transcription helper, but the live service uses a fixed local catalog. |
| 2026-11-06 | `ba6edb7` — Handle YouTube transcript request failures | Transcript failure handling milestone. |
| 2026-11-06 | `5473f08` — Update video catalog and disable runtime YouTube ingestion | Catalog-based operation and runtime ingestion restriction are explicit in the subject and current code. |
| 2026-11-06 | `393401c` — Add Next.js frontend and expand video knowledge catalog | Frontend/catalog milestone. |
| 2026-11-09 | `1f91474` — Add Vercel frontend to CORS allowed origins | Frontend origin was added to the API CORS allowlist. |
| 2026-11-09 | `0d1db04` — Add microphone voice input with Whisper transcription | User-question voice input milestone. |
| 2026-11-09 | `600874a` — Complete LangSmith evaluation and update retrieval metrics | Evaluation scripts/assets milestone; this does not prove a remote experiment ran or establish its result. |

## Current development flow reconstructed from source

1. **Dataset definition:** the initial six YouTube IDs/titles were declared in the catalog builder and frontend; three wellness videos have since been added to both source lists. Their deployed Chroma indexing remains a separate required step.
2. **Transcript preparation:** transcript API access, optional translation/fallback, segment cleanup, and timestamp-aware chunking.
3. **Vector indexing:** OpenAI embeddings and Chroma documents with video/time metadata; deterministic IDs support repeatable chunk identity.
4. **Agent features:** transcript search, summary, and references are wired as tools. SQLite checkpointing provides conversation state in code.
5. **Application interface:** a Next.js client presents nine video cards, a text chat panel, and microphone recording.
6. **Speech input:** browser audio is posted to a FastAPI endpoint and transcribed with Whisper into editable question text.
7. **Evaluation assets:** local retrieval metrics and LangSmith dataset/retrieval/answer-quality scripts are present.
8. **Deployment intent:** source contains a Render API URL and CORS entry for the Vercel frontend. A deploy configuration or successful production run was not verified.

## Challenges established by implementation changes or current constraints

| Evidence | What can be stated | What should not be claimed without confirmation |
|---|---|---|
| Commit `5473f08` and `video_service.py` | Runtime processing was restricted to a preloaded catalog; unsupported IDs are rejected. | Why the change was made or whether transcript access, reliability, cost, or deployment was the cause. |
| `youtube_transcript.py` fallback logic and `ba6edb7` subject | The code handles transcript lookup fallback and request failure conditions. | A specific incident, user impact, or that a specific failure was fully resolved in production. |
| `youtube_audio.py` and `0d1db04` subject | YouTube-audio transcription support exists in a helper; microphone-question transcription was added separately. | That audio transcription works across all browsers, formats, or production request sizes. |
| `main.py` CORS configuration and `1f91474` subject | Local and Vercel frontend origins are explicitly allowed. | That CORS was the only integration issue or that the deployed frontend/API integration is currently healthy. |
| `agent_service.py` | SQLite checkpointing is configured under backend storage with video-scoped thread IDs. | That deployed storage is durable, concurrent access is safe, or user isolation is sufficient. |
| `langsmith_*` evaluation scripts and `600874a` subject | Dataset and evaluation logic were added. | Actual retrieval scores, answer accuracy, experiment results, or performance gains. |

## Developer Reflection — Questions to Confirm

To turn source evidence into a truthful first-person project story, the owner should answer:

1. What user problem or personal motivation led to the sports-science focus?
2. Why were these six video sources selected, and were they reviewed for content quality and reuse?
3. What issue led to disabling arbitrary runtime ingestion? Was the driver reliability, quota/cost, platform constraints, or another reason?
4. Which debugging task took the most time, and what was the specific symptom and fix?
5. Was SQLite persistence tested across a Render restart or redeploy? Is persistent storage configured?
6. Did the deployed app pass a live end-to-end test? On what date and with which supported videos?
7. Were LangSmith traces or experiments actually run? What were the recorded results and dataset/experiment URLs?
8. Which tests were run locally, with which Python version, and what were the actual totals?
9. Which project skills or lessons did the developer personally gain? These cannot be inferred from code.
10. Which acknowledgments, mentor/course credits, and content attributions are desired?

Do not add personal claims or measured outcomes to a portfolio README until confirmed.
