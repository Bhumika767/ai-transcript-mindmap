# Changelog

No release versions or dates are recorded in the repository. The entries below document the implementation sequence.

## Implementation Stages

- **PDF extraction:** Added deterministic PDF page and body-paragraph selection with heading exclusion and validation.
- **PDF cleaning:** Added PDF paragraph cleanup through the existing `TranscriptionService` and Ollama/Gemma, followed by deterministic whitespace normalization.
- **Topic/subtopic extraction:** Added LLM topic extraction with strict JSON and Pydantic validation.
- **Hierarchy:** Added deterministic recursive `HierarchyNode` construction preserving order and duplicates.
- **Mermaid generation:** Added deterministic recursive Mermaid `mindmap` generation with safe labels.
- **Pipeline orchestration:** Added `process_pdf_to_mind_map()` and the serializable `PdfMindMapResult`.
- **FastAPI endpoint:** Added `POST /api/pdf-mindmap` with multipart PDF upload, page/paragraph selection, temporary-file cleanup, and original filename preservation.
- **Output quality fixes:** Added generic cleanup for missing word boundaries and punctuation/whitespace artifacts. Confirmed hierarchy labels preserve word boundaries.
- **HTML visualization:** Added HTML generation from the existing Mermaid definition. The document loads Mermaid from the external jsDelivr CDN.
- **Logging/observability:** Added the `ai_transcript.pdf_pipeline` logger, stage metadata, durations, counts, errors, explicit unavailable token usage, and `tracemalloc` peak Python allocation.
- **Tests/verification:** Added focused tests for each stage, orchestration, API behavior, HTML escaping, logging, error handling, serialization, and regression coverage for the existing voice endpoints.
