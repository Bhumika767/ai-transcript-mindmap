# Diagrams

## 1. Existing Voice Transcription Flow

This diagram shows the original voice-transcription workflow that existed in the project before the PDF mind-map extension.

```mermaid
flowchart LR

    Browser["🌐 React Browser UI"]

    API["🚀 FastAPI<br/>/api/transcribe"]

    Temp["📁 Temporary<br/>Audio File"]

    Whisper["🎙️ Faster-Whisper<br/>base.en"]

    Raw["📝 Raw<br/>Transcript"]

    CleanAPI["🧹 FastAPI<br/>/api/clean"]

    Service["⚙️ TranscriptionService"]

    LLM["🤖 Ollama<br/>Gemma 3 4B"]

    Cleaned["✨ Cleaned<br/>Transcript"]

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

---

## 2. PDF-to-Mind-Map Data Flow

This diagram shows how a selected PDF paragraph moves through extraction, cleaning, topic extraction, hierarchy construction, Mermaid generation, and HTML rendering.

```mermaid
flowchart LR

    PDF["📑 Uploaded PDF"]

    Selection["📌 Page + Paragraph<br/>Selection"]

    Extract["📄 pdf_extraction.py<br/>Extract selected body paragraph"]

    Paragraph["📝 Extracted<br/>Paragraph"]

    Clean["🧹 pdf_cleaning.py<br/>Clean and normalize text"]

    LLM1["🤖 Ollama / Gemma 3 4B"]

    Transcript["✨ Cleaned<br/>Transcript"]

    Topics["🧠 topic_extraction.py<br/>Extract topics and subtopics"]

    TopicJSON["📦 Validated<br/>Topic JSON"]

    Hierarchy["🌳 hierarchy.py<br/>Build recursive hierarchy"]

    Tree["🌲 HierarchyNode<br/>Tree"]

    Mermaid["🗺️ mind_map.py<br/>Generate Mermaid mindmap"]

    Definition["📋 Mermaid<br/>Definition"]

    HTML["🖥️ html_renderer.py<br/>Generate HTML"]

    Visual["🎨 Visual<br/>Mind Map"]

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

---

## 3. Data Flow Diagram (DFD)

This DFD shows how data moves through the extended application from user input to transcript and mind-map outputs.

```mermaid
flowchart LR

    User["👤 User"]

    subgraph Input["Input"]
        Audio["🎙️ Audio Input"]
        PDF["📑 PDF Input"]
        Selection["📌 Page + Paragraph<br/>Selection"]
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
        Whisper["🎙️ Faster-Whisper"]
        Ollama["🤖 Ollama / Gemma 3 4B"]
    end

    subgraph Data["Data / Outputs"]
        RawTranscript["📝 Raw Transcript"]
        CleanTranscript["✨ Cleaned Transcript"]
        TopicData["📦 Topic / Subtopic JSON"]
        HierarchyData["🌳 Hierarchy Tree"]
        MermaidData["🗺️ Mermaid Definition"]
        VisualMap["🎨 Visual Mind Map"]
    end

    User --> Audio
    User --> PDF
    User --> Selection

    Audio --> VoiceProcess
    VoiceProcess --> Whisper
    Whisper --> RawTranscript
    RawTranscript --> Clean

    PDF --> PDFExtract
    Selection --> PDFExtract
    PDFExtract --> Clean

    Clean --> Ollama
    Ollama --> CleanTranscript

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

---

## 4. Component Architecture

This diagram shows the main backend modules and their relationships.

```mermaid
flowchart LR

    subgraph Client["Client Layer"]
        Browser["🌐 React Frontend<br/>User Interface"]
    end

    subgraph API["API Layer"]
        App["🚀 FastAPI<br/>backend/app.py"]
    end

    subgraph Application["Application Layer"]
        Pipeline["🔄 PDF Mind-Map Pipeline<br/>pdf_mindmap_pipeline.py"]

        Extraction["📄 PDF Extraction<br/>pdf_extraction.py"]

        Cleaning["🧹 PDF Cleaning<br/>pdf_cleaning.py"]

        Topics["🧠 Topic Extraction<br/>topic_extraction.py"]

        Hierarchy["🌳 Hierarchy Construction<br/>hierarchy.py"]

        MindMap["🗺️ Mermaid Generation<br/>mind_map.py"]

        Renderer["🖥️ HTML Rendering<br/>html_renderer.py"]
    end

    subgraph ServiceLayer["Service / AI Layer"]
        Service["⚙️ TranscriptionService<br/>transcription.py"]

        Whisper["🎙️ Faster-Whisper<br/>Speech-to-Text"]

        Ollama["🤖 Ollama<br/>Gemma 3 4B"]
    end

    subgraph Observability["Observability"]
        Logs["📋 logging_config.py<br/>ai_transcript.pdf_pipeline"]
    end

    Browser -->|HTTP requests| App

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

---

## 5. POST `/api/pdf-mindmap` Sequence

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

---

## 6. High-Level System Data Flow

The following diagram summarizes the complete extended system from user input to transcript and mind-map outputs.

```mermaid
flowchart LR

    User["👤 User"]

    subgraph Client["Client Layer"]
        Frontend["🌐 React Frontend"]
    end

    subgraph API["API Layer"]
        Backend["🚀 FastAPI Backend"]
    end

    subgraph Application["Application / Processing Layer"]
        Voice["🎙️ Voice Workflow"]
        PDFPipeline["📑 PDF Mind-Map Pipeline"]
        Processing["⚙️ Processing Modules<br/>Extraction • Cleaning • Topics • Hierarchy"]
        Visualization["🗺️ Mermaid + HTML"]
    end

    subgraph AI["AI / ML Layer"]
        Whisper["🎙️ Faster-Whisper"]
        Ollama["🤖 Ollama / Gemma 3 4B"]
    end

    subgraph Output["Output Layer"]
        Transcript["📝 Cleaned Transcript"]
        JSON["📦 Structured Topic JSON"]
        MindMap["🎨 Visual Mind Map"]
    end

    User --> Frontend
    Frontend --> Backend

    Backend --> Voice
    Backend --> PDFPipeline

    Voice --> Whisper
    Whisper --> Transcript

    Voice --> Ollama
    Ollama --> Transcript

    PDFPipeline --> Processing
    Processing --> Ollama
    Ollama --> Processing

    Processing --> Visualization
    Visualization --> MindMap
    Processing --> JSON

    Transcript --> Frontend
    JSON --> Frontend
    MindMap --> Frontend
```
