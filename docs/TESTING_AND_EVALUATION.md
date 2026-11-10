# Testing and Evaluation

## What exists

The backend declares `pytest` and `httpx` in `backend/requirements.txt`. Test files under `backend/tests/` cover:

| Area | Coverage in source |
|---|---|
| FastAPI | Root and health responses; ingestion and chat success/error paths; invalid chat request. |
| Agent tool wrappers | Verify that selected `video_id` and query/summary arguments reach underlying tools. |
| Chroma integration | Deterministic chunk IDs; document content and metadata; invalid input guards. |
| Retrieval | Similarity-search arguments, selected-video filter, result fields, blank query and invalid `k`. |
| Transcript processing | Whitespace and music cleanup; source indices; timestamps; chunk argument validation. |
| YouTube transcript | URL formats and rejection; mocked English transcript retrieval. |
| Evaluation metric | Precision-at-k arithmetic and invalid inputs. |

There are no dedicated tests for audio upload/transcription, actual SQLite checkpoint persistence, live OpenAI behavior, frontend behavior, citation correctness, or production hosting. No frontend test command is present in `frontend/package.json`.

## Execution result for this audit

Attempted command:

```powershell
python -m pytest backend\tests -q
```

**Initial audit result:** The selected terminal Python reported `No module named pytest`. Separately, the project owner shared teacher feedback for an earlier version/deployment reporting **44 passing tests** and live-tested Whisper voice input. The exact test command, commit, output, and date were not included.

**Local test run on 2026-11-10:** After combining the partner's changes and adding the wellness video lists, the backend suite passed **48 tests** in an isolated Python 3.12 environment. The command was `python -m pytest tests -q` from `backend`, with a temporary dummy `OPENAI_API_KEY`; no real OpenAI calls were made. Four tests in `backend/tests/test_build_video_catalog.py` use mocks to check selective indexing, rejection of unknown IDs, the existing full-catalog behavior, and transcript-fetch failures. This is not a live transcript, Chroma, or deployment test, and no LangSmith experiment scores or latency results were measured.

The same day, a read-only transcript check found English transcripts for the three proposed wellness videos: 2,829 segments for `h2aWYjSA1Jc`, 1,089 for `mLn2X2JSrbg`, and 284 for `RcGyVTAoXEU`. Availability may change; this did not index or evaluate their contents.

After that check, the three transcripts were indexed **locally**, creating 134, 53, and 14 chunks respectively. Live semantic retrieval returned five selected-video results for each. One real agent question per new video produced a nonempty answer and a `search_transcript` tool output. These are smoke checks, not measurements of answer correctness, citation accuracy, or production performance. The deployed backend and its existing videos were not modified.

Frontend ESLint completed with no errors and one existing `@next/next/no-img-element` warning. On this Windows workspace path, `npm run lint` failed because the path contains ampersands; invoking the installed ESLint JavaScript entry point with Node worked. The TypeScript check passed after generating Next.js route types with `next typegen`.

## Evaluation assets present in code

- `backend/evaluation/evaluation_dataset.py`: 12 question examples over six catalog videos with relevant chunk indices.
- `backend/evaluation/retrieval_evaluation.py`: local `precision_at_k` calculation and aggregate over the dataset.
- `backend/evaluation/langsmith_dataset.py`: creates a named LangSmith dataset with questions, reference answers, and relevant chunk indices.
- `backend/evaluation/langsmith_evaluation.py`: remote retrieval evaluation with hit-rate-at-5 and precision-at-5.
- `backend/evaluation/langsmith_answer_evaluation.py`: remote generation evaluation with LLM-judge criteria for correctness, relevance, and groundedness.

These are methods and fixtures, not proof that the dataset was uploaded or that experiments ran. Evaluation code makes external model/vector-store and LangSmith calls and should be run deliberately with credentials and a provisioned index.

## Recommended immediate priority

The teacher review specifically identifies systematic retrieval accuracy and answer-quality evaluation as the main remaining gap. The existing 12 examples cover the original six videos only. After indexing the three wellness videos, add reviewed questions, reference answers, and relevant chunk IDs for them before claiming evaluation coverage across all nine. Prioritize:

1. Run the existing 12-question retrieval dataset against the intended catalog/index and save the LangSmith experiment link and scores.
2. Run the existing answer evaluation for correctness, relevance, and groundedness; inspect representative failures rather than reporting only an aggregate.
3. Verify the dataset's labels and add human review for evidence/citation correctness and unanswerable or out-of-scope questions.
4. Record the code revision, model, dataset version, and evaluation date so results are reproducible.

This evaluation work should precede polishing the final README and presentation claims. Documentation can continue as a draft while the measurements are being collected.

## Recommended reproducible test plan

### 1. Deterministic automated tests

In a disposable virtual environment:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m pytest tests -q
```

Record the Python version, dependency lock/versions, exact command, collected/passed/failed/skipped counts, and full failure output. The requirements are not version-pinned, so reproducibility would improve with a tested lock file or constraints.

### 2. API smoke and edge cases

Use FastAPI `TestClient` tests for schema validation, unsupported catalog IDs, malformed URLs, empty/oversized audio, upstream AI errors, and malformed upstream responses. Mock expensive external services for unit tests. Do not represent a mocked test as proof that production services work.

### 3. Retrieval relevance

For a fixed catalog/index snapshot, run every labeled question and save query, video ID, retrieved chunk IDs, labels, and metric definitions. Report hit-rate@5, precision@5, and optionally recall@5/MRR. Clarify that current labels use chunk indices and one expected relevant chunk per question; human review and multiple relevant labels would strengthen the dataset.

### 4. Answer quality and evidence

Blindly review a stratified sample for:

- Correctness against source transcript and reference answer.
- Whether each factual claim is supported.
- Citation/timestamp existence and whether the passage actually supports the claim.
- Relevance, clarity, and uncertainty communication.
- Hallucination when the selected transcript does not contain the answer.
- Response to questions outside the selected video and outside the educational domain.

Use the existing LLM judge as a screening signal, not the sole quality measure. Preserve prompt/model/dataset versions and have a human adjudicate disagreements.

### 5. Context, speech, latency, and usability

- Ask follow-up questions that depend on earlier turns; test same-thread continuity, new thread isolation, service restart persistence, and two users sharing one video.
- Record representative audio in supported browser/device combinations; compare transcription to a human reference using word error rate and note noise/accent effects.
- Measure p50/p95 end-to-end and per-stage latency over a fixed set of queries; report sample size and whether cold starts and network waits are included.
- Have representative users complete video selection, answer discovery, source verification, and microphone flows; record task completion and observed friction.

Do not invent target values or report unmeasured quality. Establish acceptance thresholds with the project owner and evaluator.

## LangSmith setup caution

`.env.example` contains `LANGCHAIN_TRACING_V2`, `LANGCHAIN_API_KEY`, and `LANGCHAIN_PROJECT`. The dataset script explicitly reads `LANGSMITH_API_KEY`. Confirm which key name/version the installed LangSmith client expects and use one documented configuration before claiming traces or evaluations work. Never paste secrets into reports, commits, screenshots, or chat.

## Reporting template

| Run date / commit | Environment | Dataset/index version | Tests collected / pass / fail / skip | Evaluation metrics | Notes |
|---|---|---|---|---|---|
| Teacher feedback shared by owner (earlier version; date/commit not supplied) | Not supplied | Not supplied | 44 passed reported; not reproduced here | No score shared | Obtain original output; run systematic LangSmith evaluations on current revision |
