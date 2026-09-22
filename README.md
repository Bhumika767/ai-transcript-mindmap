# AI Transcript App

This project provides two local workflows:

1. Browser-based voice transcription and transcript cleanup.
2. PDF paragraph processing into topics, a hierarchy, Mermaid mind-map text, and an HTML visualization.

The original voice workflow remains independent from the PDF mind-map workflow.

## System Overview

### Voice Workflow

```text
Audio
  ↓
Faster-Whisper
  ↓
Raw Transcript
  ↓
Ollama / Gemma 3 4B
  ↓
Cleaned Transcript
```

### PDF Mind-Map Workflow

```text
PDF
  ↓
Paragraph Extraction
  ↓
Transcript Cleaning
  ↓
Topic / Subtopic Extraction
  ↓
Hierarchy Construction
  ↓
Mermaid Mind-Map
  ↓
HTML Visualization
```

The LLM is used for language-dependent tasks such as transcript cleaning and topic extraction. Deterministic Python code handles PDF selection, validation, hierarchy construction, Mermaid generation, HTML escaping, and pipeline orchestration.

## Project Structure

```text
local-ai-transcript-app/
│
├── backend/
│   ├── app.py
│   ├── transcription.py
│   ├── pdf_extraction.py
│   ├── pdf_cleaning.py
│   ├── topic_extraction.py
│   ├── hierarchy.py
│   ├── mind_map.py
│   ├── html_renderer.py
│   ├── pdf_mindmap_pipeline.py
│   ├── logging_config.py
│   ├── system_prompt.txt
│   └── tests/
│
├── frontend/
│   └── src/
│
├── ARCHITECTURE.md
├── DIAGRAMS.md
├── CHANGELOG.md
├── LOGS.md
└── README.md
```

## Prerequisites

For native Windows development, install:

- Python 3.13 or newer
- Node.js and npm
- Ollama
- Git

Docker and the Dev Container configuration are not required for the native Windows workflow.

The project uses a Python virtual environment for the backend.

## Backend Configuration

Create `backend/.env` from `backend/.env.example`.

For native Windows with Ollama, use:

```text
LLM_BASE_URL=http://localhost:11434/v1
LLM_API_KEY=ollama
LLM_MODEL=gemma3:4b
WHISPER_MODEL=base.en
```

Start Ollama and make sure the model is available:

```powershell
ollama pull gemma3:4b
```

## Running the Backend

From the repository root:

```powershell
cd backend
.\.venv\Scripts\python.exe -m uvicorn app:app --host 127.0.0.1 --port 8000
```

The backend will be available at:

```text
http://127.0.0.1:8000
```

## Running the Frontend

Open a second terminal:

```powershell
cd frontend
npm ci
npm run dev
```

Open the local URL displayed by Vite in the terminal.

The frontend communicates with the FastAPI backend through the configured `/api` proxy.

## Voice Transcription

The original application supports microphone recording and audio-file upload.

The voice workflow is:

```text
Audio Input
    ↓
POST /api/transcribe
    ↓
Temporary Audio File
    ↓
Faster-Whisper base.en
    ↓
Raw Transcript
    ↓
POST /api/clean
    ↓
Ollama / Gemma 3 4B
    ↓
Cleaned Transcript
```

Existing API endpoints:

- `GET /api/status`
- `GET /api/system-prompt`
- `POST /api/transcribe`
- `POST /api/clean`

The original voice functionality remains independent from the PDF mind-map workflow.

## PDF Mind-Map Feature

The extended application provides:

```text
PDF
 ↓
Body Paragraph Extraction
 ↓
LLM Cleaning
 ↓
Topic / Subtopic Extraction
 ↓
Hierarchy Construction
 ↓
Mermaid Generation
 ↓
HTML Rendering
```

The API endpoint is:

```text
POST /api/pdf-mindmap
```

It accepts multipart form data:

| Field              | Description                   |
| ------------------ | ----------------------------- |
| `file`             | PDF file                      |
| `page_number`      | 1-based page number           |
| `paragraph_number` | 1-based body-paragraph number |

### Example API Request

From the repository root, after starting the backend:

```powershell
curl.exe -X POST "http://127.0.0.1:8000/api/pdf-mindmap" `
  -F "file=@why-llm-cant-develop-software.pdf" `
  -F "page_number=1" `
  -F "paragraph_number=1"
```

The API returns:

- original PDF filename
- page number
- paragraph number
- extracted text
- cleaned transcript
- topics and subtopics
- hierarchy
- Mermaid mind-map definition
- generated HTML
- processing time

### Example Output

A simplified response has the following structure:

```json
{
  "source_pdf": "why-llm-cant-develop-software.pdf",
  "page_number": 1,
  "paragraph_number": 1,
  "extracted_text": "One of the things I have spent a lot of time doing is interviewing software engineers.",
  "cleaned_text": "One of the things I have spent a lot of time doing is interviewing software engineers.",
  "topics": {
    "topics": [
      {
        "name": "Software Engineering Interviews",
        "subtopics": []
      }
    ]
  },
  "hierarchy": {
    "name": "Topics",
    "children": [
      {
        "name": "Software Engineering Interviews",
        "children": []
      }
    ]
  },
  "mermaid": "mindmap\n  root((Topics))\n    Software Engineering Interviews",
  "html": "...",
  "processing_time_ms": 6061.75
}
```

## Visual Mind Map

The backend generates both Mermaid mind-map text and an HTML document.

The generated HTML can be opened in a browser to display the visual mind map.

The HTML renderer currently loads Mermaid from the external jsDelivr CDN. Therefore, internet access is required when opening the generated HTML visualization.

## Frontend PDF Workflow

The React frontend provides a PDF mind-map panel where the user can:

1. Select a PDF.
2. Enter the page number.
3. Enter the paragraph number.
4. Submit the PDF for processing.
5. View the extracted paragraph.
6. View the cleaned transcript.
7. View extracted topics and subtopics.
8. View the processing time.
9. View the generated visual mind map.

The existing voice-transcription interface remains available.

## Architecture and Diagrams

Detailed architecture documentation is available in:

- `ARCHITECTURE.md` — system architecture, runtime behavior, module responsibilities, LLM boundary, API boundary, logging, and deterministic/LLM stages.
- `DIAGRAMS.md` — Mermaid architecture, DFD, data-flow, component, and sequence diagrams.

The diagrams document both the original voice workflow and the extended PDF-to-mind-map workflow.

## Logging and Observability

The PDF pipeline uses the dedicated logger:

```text
ai_transcript.pdf_pipeline
```

The logging captures information including:

- PDF source
- page and paragraph
- extracted text length
- cleaning input/output lengths
- processing durations
- topic and subtopic counts
- Mermaid output size
- HTML output size
- pipeline errors
- peak Python memory allocation measured with `tracemalloc`

Token usage is currently logged as unavailable because the existing LLM client method returns the generated text without exposing response usage metadata.

The memory value reported by `tracemalloc` represents Python allocation tracking, not total operating-system process memory.

See `LOGS.md` for logging examples and observations.

## Testing

The backend contains unit, integration, pipeline, API, logging, and regression tests.

From the `backend` directory:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

The current verified result is:

```text
52 passed, 1 warning
```

The warning is an existing dependency deprecation warning related to `ctranslate2` importing the deprecated `pkg_resources` API. It is not an application test failure.

## Development Approach

The implementation separates LLM-based interpretation from deterministic processing.

### LLM-Based Stages

- PDF paragraph cleaning
- Topic and subtopic extraction

### Deterministic Stages

- PDF paragraph selection
- Text normalization
- Pydantic validation
- Hierarchy construction
- Mermaid generation
- HTML escaping
- Temporary-file cleanup
- Pipeline orchestration

This separation makes the structural and formatting stages predictable and testable while using the LLM where language understanding is required.

## Documentation

The repository contains the following supporting documentation:

| File              | Purpose                                                                |
| ----------------- | ---------------------------------------------------------------------- |
| `README.md`       | Setup, usage, API, testing, and feature overview                       |
| `ARCHITECTURE.md` | Technical architecture and runtime behavior                            |
| `DIAGRAMS.md`     | Mermaid architecture, DFD, component, data-flow, and sequence diagrams |
| `CHANGELOG.md`    | Implementation stages and major changes                                |
| `LOGS.md`         | Logging and observability information                                  |

## Current Limitations

- The PDF API currently accepts an uploaded PDF together with page and paragraph numbers rather than a filesystem path.
- The generated HTML visualization loads Mermaid from jsDelivr, so the visualization requires network access when opened.
- Token usage is not currently available from the existing LLM response handling.
- The current PDF workflow processes one selected paragraph per API request.

## Verification

The extended workflow has been manually verified end-to-end:

```text
PDF Upload
    ↓
Page / Paragraph Selection
    ↓
PDF Extraction
    ↓
LLM Cleaning
    ↓
Topic / Subtopic Extraction
    ↓
Hierarchy Construction
    ↓
Mermaid Generation
    ↓
HTML Rendering
    ↓
React Frontend Visualization
```

The backend test suite has also been verified with 52 passing tests.
