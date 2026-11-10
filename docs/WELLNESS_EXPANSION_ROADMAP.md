# Sports Science and Wellness Expansion Roadmap

## Current domain representation

The interface and catalog configuration now include three wellness videos in addition to the original six: sleep/recovery, nutrition/hydration, and stress/mental wellness. Their transcripts and Chroma records have been generated locally and smoke-tested, but are not yet available in the deployed backend. One original transcript also includes sleep, nutrition, and hydration in the context of athletic recovery.

The backend's chat instructions frame answers around the spoken content of the currently selected video and permit clearly distinguished general explanations. They do not establish clinical triage, a medical knowledge base, personalized recommendations, or a safety classifier. Expansion should remain general education and source-grounded, not diagnosis or treatment.

## Feature proposals

Complexity is relative: Low (small UI/config change), Medium (feature across API/index/UI), High (new data or evaluation architecture).

| Feature | User benefit | Technical approach | Files likely to change | Complexity | Risks | Priority |
|---|---|---|---|---|---|---|
| Verify reproducible catalog setup | Evaluators can launch a working demo | Add documented catalog/index provisioning and health checks for required collection | `backend/scripts/build_video_catalog.py`, `backend/app/services/video_service.py`, README/docs | Medium | Rebuild costs, changing index contents, missing transcript rights | A — essential |
| Clear educational health boundary | Prevent confusion with personal medical care | Add concise boundary copy and out-of-scope response behavior; review with domain expert | `backend/app/agents/agent.py`, `frontend/src/app/page.tsx`, tests | Medium | False reassurance; users may disclose sensitive data | A — essential |
| API URL configuration | Easier local/dev/staging use | Read a public frontend environment variable with safe documented default or required setting | `frontend/src/app/page.tsx`, frontend env docs | Low | Misconfigured cross-origin URL | B — quick |
| Timestamp-linked source citations | Verify claims against video segments | Return structured source metadata alongside answer; render links that seek to timestamp | `backend/app/agents/agent.py`, tools, `backend/app/main.py`, frontend page | Medium | Incorrect citations if not checked against evidence | B — quick |
| Suggested questions | Help first-time users start | Static or per-video prompts grounded in each selected source | `frontend/src/app/page.tsx` and catalog metadata | Low | Prompts can overstate content coverage | B — quick |
| Answer feedback | Capture quality signals | Add thumbs-up/down UI and a minimal feedback API/storage path with privacy notice | Frontend, FastAPI route/service, storage/schema | Medium | Personal data retention, biased/noisy feedback | B — quick |
| Add curated wellness videos | Extend topics to sleep, nutrition/hydration, stress, general wellness, fitness and recovery | Review reputable sources, add catalog metadata/transcripts, rebuild Chroma and expand evaluation set | catalog builder, transcripts, frontend catalog, evaluation dataset | Medium | Misinformation, conflicts, health claims, licensing/attribution, stale advice | A/B — after source review |
| Topic filters | Narrow discovery by theme | Add explicit catalog tags and filter controls; attach topic metadata to documents if retrieval filtering is required | frontend catalog/page; catalog builder; Chroma metadata/retriever | Medium | Small corpus fragmentation and mislabeled topics | C |
| Cross-video semantic search | Compare themes across videos | Remove selected-video filter in a separate library search tool; return video title and time with every hit | retriever, tools, agent context, API, frontend | Medium | Mixed-source attribution; ranking and context confusion | C |
| Video-specific vs whole-library mode | Let users choose narrow or broad scope | Explicit scope selector, validated API field, controlled tool filter and visible mode indicator | frontend, `main.py`, agent context/tools, tests | Medium | Ambiguous scope can mix evidence or leak irrelevant context | C |
| Multilingual queries | Improve accessibility | Detect/select query language, use transcript translations or multilingual embeddings, test cross-language quality | ingestion, vector store, API/UI, evaluation | High | Translation drift; current model and transcript language assumptions | C |
| Out-of-scope detection | Reduce unsupported or medical-style answers | Add policy/in-domain checks and refusal/escalation wording, then evaluate adversarial and borderline prompts | agent prompt, service/API, test/evaluation datasets | High | Over-refusal or unsafe false acceptance; requires expert review | A — essential before wellness expansion |

## Recommended phases

### A. Essential before final submission

1. Confirm live API availability, actual Chroma catalog presence, and durable SQLite storage.
2. Run backend tests in a clean environment and record exact output.
3. Complete one real, end-to-end chat and microphone demo with a supported video.
4. Update conflicting README statements and clearly explain that runtime ingestion is catalog-only.
5. Establish source/citation checks and a clear educational-not-medical boundary before widening health topics.

### B. Quick improvements

- Make frontend API origin configurable.
- Add 3–4 source-specific suggested questions per video.
- Render source timestamps as links and identify which transcript title each passage comes from.
- Add a user feedback control with a documented, privacy-conscious retention approach.

### C. Future roadmap

- Add a reviewed collection for sleep, nutrition and hydration, stress, and general wellness.
- Introduce explicit search scope and cross-video mode with source attribution.
- Add topic filters and multilingual support only after dataset and evaluation coverage exist.
- Expand the evaluation dataset to cover contradictory evidence, missing answers, out-of-domain questions, context carryover, citation validity, and speech recognition.

## Safe content principles

- Prefer reputable primary or institutional educational sources and record source/title/date.
- Preserve the distinction between what a video says and broader educational context.
- Avoid diagnosis, individualized treatment, medication directions, and certainty beyond evidence.
- Do not imply that embedding similarity establishes scientific consensus.
- Show source provenance and uncertainty; provide a clear path to a qualified professional for personal health decisions.
- Have health-related safety wording reviewed by an appropriately qualified person before release.
