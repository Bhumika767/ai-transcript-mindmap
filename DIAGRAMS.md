# Diagrams

## 1. Existing Voice Transcription Flow

This diagram shows the original voice-transcription workflow that existed in the project before the PDF mind-map extension.

```mermaid
flowchart TD

    Browser["React Browser UI"]

    API["FastAPI /api/transcribe"]

    Whisper["Faster-Whisper<br/>base.en"]

    Raw["Raw Transcript"]

    CleanAPI["FastAPI /api/clean"]

    Service["TranscriptionService"]

    LLM["Ollama / Gemma 3 4B"]

    Cleaned["Cleaned Transcript"]

    Browser -->|Audio upload| API
    API -->|Audio file| Whisper
    Whisper -->|Transcribes audio| Raw
    Raw --> CleanAPI
    CleanAPI --> Service
    Service --> LLM
    LLM -->|Cleans transcript| Cleaned
    Cleaned --> Browser
```

---

## 2. PDF-to-Mind-Map Data Flow

This diagram shows how a selected PDF paragraph moves through extraction, cleaning, topic extraction, hierarchy construction, Mermaid generation, and HTML rendering.

```mermaid
flowchart TD

    PDF["Uploaded PDF"]

    Selection["Page + Paragraph Selection"]

    Extract["PDF Extraction<br/>pdf_extraction.py"]

    Paragraph["Extracted Paragraph"]

    Clean["PDF Cleaning<br/>pdf_cleaning.py"]

    LLM["Ollama / Gemma 3 4B"]

    Transcript["Cleaned Transcript"]

    Topics["Topic Extraction<br/>topic_extraction.py"]

    TopicJSON["Topic + Subtopic JSON"]

    Hierarchy["Hierarchy Builder<br/>hierarchy.py"]

    Tree["HierarchyNode Tree"]

    Mermaid["Mermaid Generator<br/>mind_map.py"]

    Definition["Mermaid Definition"]

    HTML["HTML Renderer<br/>html_renderer.py"]

    Visual["Visual Mind Map"]

    PDF --> Selection
    Selection --> Extract
    Extract --> Paragraph
    Paragraph --> Clean

    Clean -->|Cleaning request| LLM
    LLM -->|Cleaned text| Clean

    Clean --> Transcript
    Transcript --> Topics

    Topics -->|Topic extraction request| LLM
    LLM -->|Structured topics| Topics

    Topics --> TopicJSON
    TopicJSON --> Hierarchy
    Hierarchy --> Tree
    Tree --> Mermaid
    Mermaid --> Definition
    Definition --> HTML
    HTML --> Visual
```

---

## 3. Data Flow Diagram (DFD)

This DFD shows the main movement of data through the application from user input to the final outputs.

```mermaid
flowchart TD

    User["User"]

    Input["Audio / PDF Input"]

    Selection["Page + Paragraph Selection"]

    Application["AI Transcript Application"]

    Voice["Voice Transcription"]

    PDF["PDF Paragraph Extraction"]

    Cleaning["Transcript Cleaning"]

    Topics["Topic + Subtopic Extraction"]

    Hierarchy["Hierarchy Construction"]

    MindMap["Mind-Map Generation"]

    Output["Transcript / JSON / Visual Mind Map"]

    User --> Input
    Input --> Application
    Application --> Voice
    Application --> PDF

    PDF --> Selection
    Voice --> Cleaning
    Selection --> Cleaning

    Cleaning --> Topics
    Topics --> Hierarchy
    Hierarchy --> MindMap

    Cleaning --> Output
    Topics --> Output
    MindMap --> Output

    Output --> User
```

---

## 4. Component Architecture

This diagram shows the main components of the application and how they interact.

```mermaid
flowchart TD

    Frontend["React Frontend"]

    API["FastAPI Backend<br/>backend/app.py"]

    Pipeline["PDF Mind-Map Pipeline<br/>pdf_mindmap_pipeline.py"]

    Extraction["PDF Extraction<br/>pdf_extraction.py"]

    Cleaning["PDF Cleaning<br/>pdf_cleaning.py"]

    Topics["Topic Extraction<br/>topic_extraction.py"]

    Hierarchy["Hierarchy Builder<br/>hierarchy.py"]

    MindMap["Mermaid Generator<br/>mind_map.py"]

    Renderer["HTML Renderer<br/>html_renderer.py"]

    Service["TranscriptionService<br/>transcription.py"]

    AI["Ollama / Gemma 3 4B"]

    Logs["Pipeline Logging<br/>logging_config.py"]

    Frontend --> API
    API --> Pipeline

    Pipeline --> Extraction
    Extraction --> Cleaning
    Cleaning --> Topics
    Topics --> Hierarchy
    Hierarchy --> MindMap
    MindMap --> Renderer

    Cleaning --> Service
    Topics --> Service
    Service --> AI

    Pipeline -.-> Logs
```

---

## 5. POST `/api/pdf-mindmap` Sequence

This sequence diagram shows the runtime interaction when the user uploads a PDF and requests a specific page and paragraph.

```mermaid
sequenceDiagram

    participant User as React Browser
    participant API as FastAPI
    participant Pipeline as PDF Pipeline
    participant Extract as PDF Extraction
    participant Service as TranscriptionService
    participant LLM as Ollama
    participant Build as Hierarchy + Mind Map
    participant HTML as HTML Renderer

    User->>API: Upload PDF + page + paragraph

    API->>Pipeline: Process PDF

    Pipeline->>Extract: Extract paragraph
    Extract-->>Pipeline: Paragraph

    Pipeline->>Service: Clean paragraph
    Service->>LLM: Cleaning request
    LLM-->>Service: Cleaned paragraph
    Service-->>Pipeline: Cleaned transcript

    Pipeline->>Service: Extract topics
    Service->>LLM: Topic extraction request
    LLM-->>Service: Topic JSON
    Service-->>Pipeline: Validated topics

    Pipeline->>Build: Build hierarchy
    Build-->>Pipeline: Mind-map structure

    Pipeline->>HTML: Render Mermaid HTML
    HTML-->>Pipeline: HTML visualization

    Pipeline-->>API: PdfMindMapResult
    API-->>User: JSON + Mermaid + HTML
```

---

## 6. High-Level System Data Flow

This diagram summarizes the complete system from user input to the final transcript and mind-map outputs.

```mermaid
flowchart TD

    User["User"]

    Frontend["React Frontend"]

    Backend["FastAPI Backend"]

    Voice["Voice Workflow"]

    PDF["PDF Mind-Map Workflow"]

    AI["AI Services<br/>Faster-Whisper + Ollama"]

    Processing["Processing<br/>Cleaning + Topics + Hierarchy"]

    Visualization["Visualization<br/>Mermaid + HTML"]

    Results["Results<br/>Transcript + JSON + Mind Map"]

    User --> Frontend
    Frontend --> Backend

    Backend --> Voice
    Backend --> PDF

    Voice --> AI
    PDF --> Processing

    Processing --> AI
    AI --> Processing

    Processing --> Visualization
    Visualization --> Results

    Voice --> Results

    Results --> Frontend
    Frontend --> User
```

---

## Diagram Overview

The six diagrams describe the system at different levels:

1. **Existing Voice Transcription Flow**  
   Shows the original audio transcription workflow.

2. **PDF-to-Mind-Map Data Flow**  
   Shows the detailed processing of a selected PDF paragraph.

3. **Data Flow Diagram (DFD)**  
   Shows the overall movement of data through the application.

4. **Component Architecture**  
   Shows the main software components and their relationships.

5. **POST `/api/pdf-mindmap` Sequence**  
   Shows the runtime interaction between the frontend, backend, pipeline, LLM, and output components.

6. **High-Level System Data Flow**  
   Shows the complete system at a simplified architectural level.
