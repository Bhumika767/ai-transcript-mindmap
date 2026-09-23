# Diagrams

These diagrams describe the main workflows, data flow, system components, and runtime interactions of the AI Transcript Application.

---

## 1. Existing Voice Transcription Flow

This diagram shows the original voice-transcription workflow that existed in the project before the PDF mind-map extension.

```mermaid
flowchart LR

    User["User<br/>Upload / Record Audio"]

    API["FastAPI<br/>/api/transcribe"]

    Whisper["Faster-Whisper<br/>Speech-to-Text"]

    Raw["Raw Transcript"]

    Clean["Ollama / Gemma 3 4B<br/>Transcript Cleaning"]

    Output["Cleaned Transcript<br/>Returned to User"]

    User --> API
    API --> Whisper
    Whisper --> Raw
    Raw --> Clean
    Clean --> Output

    style User fill:#f3f0ff,stroke:#8b7cc8
    style API fill:#f3f0ff,stroke:#8b7cc8
    style Whisper fill:#f3f0ff,stroke:#8b7cc8
    style Raw fill:#f3f0ff,stroke:#8b7cc8
    style Clean fill:#f3f0ff,stroke:#8b7cc8
    style Output fill:#f3f0ff,stroke:#8b7cc8
