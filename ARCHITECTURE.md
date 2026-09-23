## System Architecture

```mermaid
graph TD

    %% =========================
    %% Client Layer
    %% =========================
    subgraph Client["Client Layer"]
        Browser["🌐 React Frontend
        User Interface
        Audio / PDF Upload
        Transcript / Mind Map Display"]
    end

    %% =========================
    %% Backend Layer
    %% =========================
    subgraph Backend["Backend Layer"]
        FastAPI["🚀 FastAPI Backend
        HTTP API
        Validation
        CORS
        Request Handling"]

        Voice["🎙️ Voice Workflow
        Audio → Transcript"]

        PDF["📄 PDF Mind-Map Workflow
        PDF → Mind Map"]
    end

    %% =========================
    %% AI Layer
    %% =========================
    subgraph AI["AI / ML Layer"]
        Whisper["🎙️ Faster-Whisper
        Speech-to-Text"]

        Ollama["🤖 Ollama / Gemma 3 4B
        Transcript Cleaning
        Topic Extraction"]
    end

    %% =========================
    %% Processing Layer
    %% =========================
    subgraph Processing["Processing Layer"]

        Transcript["📝 Transcript Processing
        Cleaning
        Topic / Subtopic Extraction"]

        Structure["🌳 Structure Generation
        Hierarchy Construction
        Mermaid Mind Map"]

        Render["🖥️ Visualization
        HTML Rendering"]
    end

    %% =========================
    %% Output Layer
    %% =========================
    subgraph Output["Output"]

        CleanTranscript["✨ Cleaned Transcript"]

        TopicData["📦 Topics & Subtopics"]

        MindMap["🧠 Visual Mind Map"]

    end

    %% =========================
    %% Main Flow
    %% =========================

    Browser -->|Audio / PDF Upload| FastAPI

    FastAPI --> Voice
    FastAPI --> PDF

    %% Voice workflow
    Voice --> Whisper
    Whisper -->|Raw Transcript| Transcript

    %% PDF workflow
    PDF -->|Selected Paragraph| Transcript

    %% AI processing
    Transcript --> Ollama
    Ollama -->|Cleaned Text| Transcript

    Transcript -->|Cleaned Transcript| CleanTranscript
    Transcript -->|Topic Request| Ollama
    Ollama -->|Topics + Subtopics| TopicData

    %% Structure and visualization
    TopicData --> Structure
    Structure --> Render
    Render --> MindMap

    %% Output
    CleanTranscript --> Browser
    TopicData --> Browser
    MindMap --> Browser


    %% =========================
    %% Clean Yellow Styling
    %% =========================

    style Client fill:#fff9c4,stroke:#c9b458,stroke-width:2px
    style Backend fill:#fff9c4,stroke:#c9b458,stroke-width:2px
    style AI fill:#fff9c4,stroke:#c9b458,stroke-width:2px
    style Processing fill:#fff9c4,stroke:#c9b458,stroke-width:2px
    style Output fill:#fff9c4,stroke:#c9b458,stroke-width:2px

    style Browser fill:#fffde7,stroke:#8d7b32
    style FastAPI fill:#fffde7,stroke:#8d7b32
    style Voice fill:#fffde7,stroke:#8d7b32
    style PDF fill:#fffde7,stroke:#8d7b32
    style Whisper fill:#fffde7,stroke:#8d7b32
    style Ollama fill:#fffde7,stroke:#8d7b32
    style Transcript fill:#fffde7,stroke:#8d7b32
    style Structure fill:#fffde7,stroke:#8d7b32
    style Render fill:#fffde7,stroke:#8d7b32
    style CleanTranscript fill:#fffde7,stroke:#8d7b32
    style TopicData fill:#fffde7,stroke:#8d7b32
    style MindMap fill:#fffde7,stroke:#8d7b32
