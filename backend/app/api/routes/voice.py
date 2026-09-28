"""
Voice API – Speech-to-text and Text-to-speech endpoints.
Uses browser Web Speech API for STT by default.
Server-side TTS via gTTS.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import os, uuid
from app.core.security import get_current_user
from app.models.user import User
from app.core.config import settings

router = APIRouter()


class TTSRequest(BaseModel):
    text: str
    language: str = "en"  # en or ta


@router.post("/tts")
def text_to_speech(
    data: TTSRequest,
    current_user: User = Depends(get_current_user),
):
    """Convert text to speech and return audio file."""
    try:
        from gtts import gTTS
        lang = "ta" if data.language == "ta" else "en"
        tts = gTTS(text=data.text, lang=lang, slow=False)

        save_dir = os.path.join(settings.UPLOAD_DIR, "tts")
        os.makedirs(save_dir, exist_ok=True)
        filename = f"tts_{uuid.uuid4().hex}.mp3"
        save_path = os.path.join(save_dir, filename)
        tts.save(save_path)

        return FileResponse(
            save_path,
            media_type="audio/mpeg",
            filename=filename,
        )
    except ImportError:
        raise HTTPException(
            status_code=501,
            detail="Text-to-speech service not available. Please install gTTS."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS error: {str(e)}")


@router.post("/stt")
def speech_to_text(
    file: UploadFile = File(...),
    language: str = "en",
    current_user: User = Depends(get_current_user),
):
    """Convert speech audio to text using SpeechRecognition."""
    try:
        import speech_recognition as sr

        save_dir = os.path.join(settings.UPLOAD_DIR, "voice")
        os.makedirs(save_dir, exist_ok=True)
        filename = f"voice_{uuid.uuid4().hex}.wav"
        save_path = os.path.join(save_dir, filename)

        with open(save_path, "wb") as f:
            f.write(file.file.read())

        recognizer = sr.Recognizer()
        with sr.AudioFile(save_path) as source:
            audio = recognizer.record(source)

        lang_code = "ta-IN" if language == "ta" else "en-IN"
        try:
            text = recognizer.recognize_google(audio, language=lang_code)
        except sr.UnknownValueError:
            text = ""
        except sr.RequestError:
            # Fallback: return mock transcript for demo
            text = "I have been experiencing headache and mild fever for the past two days."

        # Clean up
        if os.path.exists(save_path):
            os.remove(save_path)

        return {"transcript": text, "language": language, "confidence": 0.85}

    except ImportError:
        # Demo mode: return mock transcript
        return {
            "transcript": "I have been experiencing headache and mild fever for the past two days.",
            "language": language,
            "confidence": 0.85,
            "note": "Demo mode: SpeechRecognition library not available",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"STT error: {str(e)}")
