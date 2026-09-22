# Diagrams

## 1. Existing Voice Transcription Flow

This diagram shows the original voice-transcription workflow that existed in the project before the PDF mind-map extension.

```mermaid
flowchart LR

    Browser["🌐 React Browser UI"]
    API["🚀 FastAPI /api/transcribe"]
    Temp["📁 Temporary Audio File"]
    Whisper["🎙️ Faster-Whisper base.en"]
    Raw["📝 Raw Transcript"]
    CleanAPI["🧹 FastAPI /api/clean"]
    Service["⚙️ TranscriptionService"]
    LLM["🤖 Ollama / Gemma 3 4B"]
    Cleaned["✨ Cleaned Transcript"]

    Browser -->|Audio upload / recording| API
    API --> Temp
    Temp --> Whisper
    Whisper --> Raw
    Raw --> CleanAPI
    CleanAPI --> Service
    Service --> LLM
    LLM --> Cleaned
    Cleaned --> Browser
```

## 2. PDF-to-Mind-Map Data Flow

This diagram shows how a selected PDF paragraph moves through extraction, cleaning, topic extraction, hierarchy construction, Mermaid generation, and HTML rendering.

```mermaid
flowchart TD

    PDF["📑 Uploaded PDF"]
    Selection["📌 Page + Paragraph Selection"]

    Extract["📄 pdf_extraction.py
    Extract selected body paragraph"]

    Paragraph["📝 Extracted Paragraph"]

    Clean["🧹 pdf_cleaning.py
    Clean and normalize text"]

    LLM1["🤖 Ollama / Gemma 3 4B"]

    Transcript["✨ Cleaned Transcript"]

    Topics["🧠 topic_extraction.py
    Extract topics and subtopics"]

    TopicJSON["📦 Validated Topic JSON"]

    Hierarchy["🌳 hierarchy.py
    Build recursive hierarchy"]

    Tree["🌲 HierarchyNode Tree"]

    Mermaid["🗺️ mind_map.py
    Generate Mermaid mindmap"]

    Definition["📋 Mermaid Definition"]

    HTML["🖥️ html_renderer.py
    Generate HTML"]

    Visual["🎨 Visual Mind Map"]

    PDF --> Selection
    Selection --> Extract
    Extract --> Paragraph
    Paragraph --> Clean

    Clean -->|Cleaning request| LLM1
    LLM1 -->|Cleaned text| Clean

    Clean --> Transcript
    Transcript --> Topics

    Topics -->|Topic extraction request| LLM1
    LLM1 -->|Topics + subtopics JSON| Topics

    Topics --> TopicJSON
    TopicJSON --> Hierarchy
    Hierarchy --> Tree
    Tree --> Mermaid
    Mermaid --> Definition
    Definition --> HTML
    HTML --> Visual
```

## 3. Component Architecture

This diagram shows the main backend modules and their relationships.

```mermaid
flowchart TB

    subgraph API["API Layer"]
        App["🚀 backend/app.py
        FastAPI"]
    end

    subgraph Application["Application Layer"]

        Pipeline["🔄 pdf_mindmap_pipeline.py
        Pipeline Orchestration"]

        Extraction["📄 pdf_extraction.py
        PDF Extraction"]

        Cleaning["🧹 pdf_cleaning.py
        PDF Cleaning"]

        Topics["🧠 topic_extraction.py
        Topic Extraction"]

        Hierarchy["🌳 hierarchy.py
        Hierarchy Construction"]

        MindMap["🗺️ mind_map.py
        Mermaid Generation"]

        Renderer["🖥️ html_renderer.py
        HTML Rendering"]
    end

    subgraph ServiceLayer["Service / AI Layer"]

        Service["⚙️ transcription.py
        TranscriptionService"]

        Whisper["🎙️ Faster-Whisper
        Speech-to-Text"]

        Ollama["🤖 Ollama
        OpenAI-Compatible LLM"]

    end

    subgraph Observability["Observability"]

        Logs["📋 logging_config.py
        ai_transcript.pdf_pipeline"]

    end

    App -->|PDF request| Pipeline

    App -->|Creates / uses service| Service

    Pipeline --> Extraction
    Pipeline --> Cleaning
    Pipeline --> Topics
    Pipeline --> Hierarchy
    Pipeline --> MindMap
    Pipeline --> Renderer

    Cleaning -->|uses clean_with_llm()| Service
    Topics -->|uses LLM boundary| Service

    Service --> Whisper
    Service --> Ollama

    Pipeline -.->|logging| Logs
    Extraction -.->|logging| Logs
    Cleaning -.->|logging| Logs
    Topics -.->|logging| Logs
```

## 4. POST `/api/pdf-mindmap` Sequence

This sequence diagram shows the runtime interaction when the user uploads a PDF and requests a specific page and paragraph.

```mermaid
sequenceDiagram

    participant Client as React Browser
    participant API as FastAPI app.py
    participant Pipeline as PDF Pipeline
    participant Extract as PDF Extraction
    participant Service as TranscriptionService
    participant LLM as Ollama / Gemma
    participant Hierarchy as Hierarchy Builder
    participant Mermaid as Mermaid Generator
    participant HTML as HTML Renderer

    Client->>API: Upload PDF + page + paragraph

    API->>API: Validate request
    API->>API: Save PDF to temporary file

    API->>Pipeline: process_pdf_to_mind_map()

    Pipeline->>Extract: extract_paragraph()
    Extract-->>Pipeline: Extracted paragraph

    Pipeline->>Service: Clean paragraph
    Service->>LLM: Cleaning request
    LLM-->>Service: Cleaned paragraph
    Service-->>Pipeline: Cleaned transcript

    Pipeline->>Service: Extract topics/subtopics
    Service->>LLM: Topic extraction request
    LLM-->>Service: Structured topic JSON
    Service-->>Pipeline: Validated topics

    Pipeline->>Hierarchy: build_hierarchy()
    Hierarchy-->>Pipeline: HierarchyNode tree

    Pipeline->>Mermaid: generate_mermaid_mindmap()
    Mermaid-->>Pipeline: Mermaid definition

    Pipeline->>HTML: render_mermaid_html()
    HTML-->>Pipeline: HTML visualization

    Pipeline-->>API: PdfMindMapResult

    API->>API: Restore original filename
    API->>API: Delete temporary PDF

    API-->>Client: JSON + Mermaid + HTML
```

## 5. High-Level System Data Flow

The following diagram summarizes the complete extended system from user input to output.

```mermaid
graph TD

    subgraph Input["Input"]
        User["👤 User"]
        Audio["🎙️ Audio"]
        PDF["📑 PDF"]
    end

    subgraph System["AI Transcript Application"]

        Frontend["⚛️ React Frontend"]

        Backend["🚀 FastAPI Backend"]

        Voice["🎙️ Voice Pipeline"]

        PDFPipeline["📄 PDF Mind-Map Pipeline"]

        AI["🤖 Ollama / Gemma 3 4B"]

        Whisper["🎙️ Faster-Whisper"]

        Structure["🌳 Hierarchy"]

        Visualization["🗺️ Mermaid + HTML"]

    end

    subgraph Output["Output"]
        Transcript["📝 Cleaned Transcript"]
        MindMap["🧠 Visual Mind Map"]
        JSON["📦 Structured JSON"]
    end

    User --> Frontend

    Audio --> Frontend
    PDF --> Frontend

    Frontend --> Backend

    Backend --> Voice
    Voice --> Whisper
    Whisper --> Transcript
    Voice --> AI
    AI --> Transcript

    Backend --> PDFPipeline
    PDFPipeline --> AI
    AI --> PDFPipeline

    PDFPipeline --> Structure
    Structure --> Visualization

    Visualization --> MindMap
    Structure --> JSON

    Transcript --> Frontend
    MindMap --> Frontend
    JSON --> Frontend
```

## 3. Data Flow Diagram (DFD)

This DFD shows how data moves through the extended application, from user input to transcript and mind-map outputs.

```mermaid
flowchart LR

    User["👤 User"]

    subgraph Input["Input"]
        Audio["🎙️ Audio Input"]
        PDF["📑 PDF Input"]
        Selection["📌 Page + Paragraph
        Selection"]
    end

    subgraph Processing["Processing"]
        VoiceProcess["1. Voice Transcription"]
        PDFExtract["2. PDF Paragraph Extraction"]
        Clean["3. Transcript Cleaning"]
        Topics["4. Topic / Subtopic Extraction"]
        Hierarchy["5. Hierarchy Construction"]
        MindMap["6. Mind-Map Generation"]
        HTML["7. HTML Rendering"]
    end

    subgraph AI["AI Services"]
        Whisper["Faster-Whisper"]
        Ollama["Ollama / Gemma 3 4B"]
    end

    subgraph Data["Data / Outputs"]
        RawTranscript["Raw Transcript"]
        CleanTranscript["Cleaned Transcript"]
        TopicData["Topic / Subtopic JSON"]
        HierarchyData["Hierarchy Tree"]
        MermaidData["Mermaid Definition"]
        VisualMap["Visual Mind Map"]
    end

    User --> Audio
    User --> PDF
    User --> Selection

    Audio --> VoiceProcess
    VoiceProcess --> Whisper
    Whisper --> RawTranscript
    RawTranscript --> Clean
    Clean --> Ollama
    Ollama --> CleanTranscript

    PDF --> PDFExtract
    Selection --> PDFExtract
    PDFExtract --> Clean
    Clean --> Ollama

    CleanTranscript --> Topics
    Topics --> Ollama
    Ollama --> TopicData

    TopicData --> Hierarchy
    Hierarchy --> HierarchyData

    HierarchyData --> MindMap
    MindMap --> MermaidData

    MermaidData --> HTML
    HTML --> VisualMap

    CleanTranscript --> User
    VisualMap --> User
```
