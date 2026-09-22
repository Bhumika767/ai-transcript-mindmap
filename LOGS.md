# Verification Logs

This file records verification evidence observed during implementation. It does not claim unobserved timings, screenshots, or production behavior.

## Setup and Existing Application

- The project requires Python `>=3.12` according to `backend/pyproject.toml`.
- Native Windows setup used a uv-managed Python 3.13 environment because the locked Faster-Whisper dependency did not provide a compatible Windows wheel for Python 3.14.
- `uv sync --locked` completed successfully.
- The native configuration used Ollama at `http://localhost:11434/v1`, model `gemma3:4b`, and Faster-Whisper model `base.en`.
- The frontend production build, TypeScript check, and lint passed during setup validation.

## Focused Stage Verification

- PDF extraction tests initially passed 4 tests.
- After heading correction, PDF extraction tests passed 5 tests and manual page 1 body paragraphs were verified against `why-llm-cant-develop-software.pdf`.
- PDF cleaning tests passed with mocked LLM responses.
- A real cleaning integration test used the actual assignment PDF page 1 paragraph 1 and native Ollama/Gemma. The output remained semantically equivalent.
- Topic extraction tests covered valid JSON, multiple topics, code fences, invalid JSON, schema errors, empty input, and LLM failure.
- A real topic integration test used the actual extraction and cleaning stages. It returned a valid topic structure for the assignment paragraph.
- Hierarchy tests covered empty topics, ordering, duplicates, multiple topics, subtopics, and invalid input.
- Mermaid tests covered recursion, ordering, duplicates, special characters, empty hierarchies, and invalid input.
- Pipeline orchestration tests covered stage chaining, result serialization, and stage failure propagation.

## API Smoke Test

- `POST /api/pdf-mindmap` was manually exercised with the assignment PDF, page 1, paragraph 1.
- The response preserved the original uploaded filename instead of the temporary server path.
- The response included extracted text, cleaned text, topics, hierarchy, Mermaid, HTML, and processing metadata.

## Quality Fixes

The smoke test identified:

- A temporary path appearing in `source_pdf`.
- A missing space in cleaned text, such as `doingis`.
- A risk of losing word boundaries in labels.

The fixes were:

- Restore the original upload filename at the API boundary.
- Add generic deterministic whitespace, punctuation, and source-aware word-boundary normalization after PDF cleaning.
- Add regression coverage confirming topic and hierarchy labels preserve spaces.

## HTML Verification

- HTML renderer tests verified basic HTML structure, inclusion of the Mermaid definition, Mermaid script reference, and escaping of angle brackets/script-like label content.
- Pipeline and API tests verified that the generated HTML is included in the result.
- The generated HTML uses the external jsDelivr Mermaid CDN, so browser rendering requires internet access.

## Logging Verification

- Focused logging tests verified stage metadata for extraction, cleaning, topics, hierarchy, Mermaid, HTML, and pipeline completion.
- Error tests verified pipeline error logs include stage context and peak Python allocation metadata.
- The dedicated logger name is `ai_transcript.pdf_pipeline`.
- Memory logging uses `tracemalloc` peak Python allocation, not total operating-system process memory.
- Current LLM calls do not expose usage metadata through the existing text-returning service method, so logs explicitly use `token_usage=unavailable`.

## Final Test Result

The final observed backend result is:

```text
52 passed, 1 warning
```

The warning is emitted by the `ctranslate2` dependency because it imports the deprecated `pkg_resources` API from setuptools. It is a dependency deprecation warning, not an application test failure.

Existing voice-related endpoint tests continued to pass, and the voice transcription implementation was not replaced.
