import logging
import os
import tempfile
from contextlib import asynccontextmanager
from typing import Annotated

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from pdf_extraction import (
    InvalidPageNumberError,
    InvalidParagraphNumberError,
    PdfExtractionError,
)
from pdf_mindmap_pipeline import PdfMindMapResult, process_pdf_to_mind_map
from transcription import TranscriptionService

load_dotenv()
logger = logging.getLogger(__name__)


class CleanRequest(BaseModel):
    text: str
    system_prompt: str | None = None


service = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Uses OpenAI-compatible API (Ollama, OpenAI, LM Studio, etc.). Configure via .env file."""
    global service
    print("🚀 Starting AI Transcript App...")

    service = TranscriptionService(
        whisper_model=os.getenv("WHISPER_MODEL"),
        llm_base_url=os.getenv("LLM_BASE_URL"),
        llm_api_key=os.getenv("LLM_API_KEY"),
        llm_model=os.getenv("LLM_MODEL"),
    )
    print("✅ Ready!")
    yield


app = FastAPI(title="AI Transcript App", lifespan=lifespan)

# CORS for localhost development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server (Vite)
        "http://localhost:5173",  # React dev server (Vite alternative port)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/status")
async def get_status():
    return {
        "status": "ready" if service else "initializing",
        "whisper_model": os.getenv("WHISPER_MODEL"),
        "llm_model": os.getenv("LLM_MODEL"),
        "llm_base_url": os.getenv("LLM_BASE_URL"),
    }


@app.get("/api/system-prompt")
async def get_system_prompt():
    if not service:
        raise HTTPException(status_code=503, detail="Service not ready")

    return {"default_prompt": service.get_default_system_prompt()}


@app.post("/api/transcribe")
async def transcribe_audio(audio: Annotated[UploadFile, File()]):
    if not service:
        raise HTTPException(
            status_code=503, detail="Service not ready, still initializing models"
        )

    suffix = os.path.splitext(audio.filename)[1] or ".webm"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await audio.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        raw_text = service.transcribe(tmp_path)
        return {"success": True, "text": raw_text}

    except Exception as e:
        print(f"❌ Transcription error: {e}")
        raise HTTPException(
            status_code=500, detail=f"Transcription failed: {str(e)}"
        ) from e

    finally:
        # Always clean up temp file
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


@app.post("/api/clean")
async def clean_text(request: CleanRequest):
    if not service:
        raise HTTPException(status_code=503, detail="Service not ready")

    try:
        cleaned_text = service.clean_with_llm(
            request.text, system_prompt=request.system_prompt
        )
        return {"success": True, "text": cleaned_text}

    except Exception as e:
        # Log the full error to the backend terminal; keep the response generic so no
        # raw error detail leaks to the frontend.
        print(f"❌ LLM cleaning failed: {e}")
        raise HTTPException(
            status_code=502,
            detail="LLM cleaning failed. Check the backend terminal for details.",
        ) from e


@app.post("/api/pdf-mindmap", response_model=PdfMindMapResult)
async def create_pdf_mind_map(
    file: Annotated[UploadFile, File()],
    page_number: Annotated[int, Form(ge=1)],
    paragraph_number: Annotated[int, Form(ge=1)],
):
    if not service:
        raise HTTPException(status_code=503, detail="Service not ready")
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Uploaded file must be a PDF")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded PDF is empty")

    tmp_path = None
    logger.info(
        "PDF mind-map upload received: filename=%s page=%d paragraph=%d",
        file.filename,
        page_number,
        paragraph_number,
    )

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        result = process_pdf_to_mind_map(
            service,
            tmp_path,
            page_number,
            paragraph_number,
        )
        result = result.model_copy(
            update={"source_pdf": os.path.basename(file.filename or "uploaded.pdf")}
        )
        logger.info(
            "PDF mind-map upload processed: filename=%s elapsed_ms=%.1f",
            file.filename,
            result.processing_time_ms,
        )
        return result
    except (InvalidPageNumberError, InvalidParagraphNumberError, PdfExtractionError) as error:
        logger.warning("PDF mind-map request rejected: filename=%s error=%s", file.filename, error)
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:
        logger.exception("PDF mind-map processing failed: filename=%s", file.filename)
        raise HTTPException(
            status_code=500,
            detail="PDF mind-map processing failed. Check the backend terminal for details.",
        ) from error
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)
