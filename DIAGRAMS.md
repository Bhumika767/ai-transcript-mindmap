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
