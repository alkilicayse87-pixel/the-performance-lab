# Final Project Presentation Outline

Suggested 10-slide structure for an approximately 7–10 minute presentation. Replace placeholders with verified screenshots, actual test output, and deployment evidence; do not invent metrics or personal challenges.

| Slide | Title | Key content | Suggested visual/demo |
|---|---|---|---|
| 1 | THE PERFORMANCE LAB | Project name, tagline, Ironhack Project III, presenter name | Screenshot of the current application; add owner-confirmed attribution. |
| 2 | Problem and opportunity | Why locating specific ideas inside long educational videos is inconvenient; identify target audience as a project hypothesis, not validated market research. | Example: a viewer trying to find a passage about recovery. |
| 3 | Solution and business value | Searchable, conversational interface over a curated video library; possible applications in learning, coaching, and content discovery. | User journey: choose video → ask → inspect evidence. |
| 4 | Dataset and scope | Nine configured videos: six original sports-science entries and three added wellness entries. Explain that wellness transcripts must be indexed in the deployed backend before demoing them. | Video-card grid, topic list, and verified index/deployment status. |
| 5 | Architecture and RAG | Transcript prep, 1000-character chunk target/150-character overlap, embeddings, Chroma, top-five retrieval, model response. | Mermaid diagram from `ARCHITECTURE_EXPLAINED.md`. |
| 6 | Agent tools and memory | Model-selected transcript search, summary, references; selected-video context; SQLite checkpointer; distinguish LangChain helpers from custom LangGraph graph (none authored). | Ask one factual question and one summary question; show actual trace only if captured. |
| 7 | Multimodal interaction | Text chat plus optional browser recording and Whisper transcription of the user's question; this is not visual video analysis. | Live microphone flow, only if pretested. |
| 8 | Live demo | Select a supported video, ask a grounded question, show source timestamp, ask follow-up, try unsupported catalog video. | Live site; prepare a backup recording/screenshots and disclose any simulated step. |
| 9 | Testing, evaluation, and challenges | Teacher feedback reports 44 passing tests for an earlier version; attribute that result and show original output if available. Prioritize current LangSmith retrieval and answer-quality results before making quality claims. | Show reproducible test output and actual LangSmith experiment results; audit did not independently verify either. |
| 10 | Roadmap and reflection | Prioritized wellness expansion, citation evidence, cross-video mode, deployment reliability; personal lessons/thanks confirmed by presenter. | Three highest-impact next steps and Q&A. |

## Demo readiness gates

- Verify both frontend and backend are reachable on presentation day.
- Confirm production Chroma data exists and selected video loads.
- Test model response and timestamp reference in advance.
- Check microphone permission and transcription; have typed-question fallback.
- Avoid exposing environment variables or account dashboards.
- Attribute the earlier 44-test result to the teacher review unless its original output and revision can be confirmed.
- Use only real, dated test/evaluation results; otherwise state that measurements are pending.
