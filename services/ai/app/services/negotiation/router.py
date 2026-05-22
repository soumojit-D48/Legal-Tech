from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException,
    Form
)

from fastapi.responses import StreamingResponse

import os
import uuid
import json
import asyncio

from .voice_service import VoiceService
from .avatar_service import AvatarService

router = APIRouter(
    tags=["Voice Coach"]
)

TEMP_DIR = "app/audio_tmp"

os.makedirs(TEMP_DIR, exist_ok=True)


@router.get("/health")
async def health_check():

    return {
        "status": "ok",
        "service": "voice-service"
    }


async def stream_llm_response(user_text: str):

    response = (
        f"I understood your question as: {user_text}. "
        f"This contract clause may contain legal obligations and negotiation risks."
    )

    avatar_payload = AvatarService.build_avatar_payload(
        response
    )

    yield f"data: {json.dumps({'avatar': avatar_payload})}\n\n"

    words = response.split()

    for word in words:

        chunk = {
            "token": word + " "
        }

        yield f"data: {json.dumps(chunk)}\n\n"

        await asyncio.sleep(0.04)

    yield f"data: {json.dumps({'done': True})}\n\n"


@router.post("/api/v1/voice/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...)
):

    try:

        print("========== TRANSCRIBE REQUEST ==========")
        print("Filename:", file.filename)
        print("Content Type:", file.content_type)

        if not file.filename:

            raise HTTPException(
                status_code=400,
                detail="No filename provided"
            )

        file_ext = file.filename.split(".")[-1].lower()

        allowed_extensions = [
            "mp3",
            "wav",
            "webm",
            "ogg",
            "m4a"
        ]

        if file_ext not in allowed_extensions:

            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format: {file_ext}"
            )

        temp_filename = f"{uuid.uuid4()}.{file_ext}"

        input_path = os.path.join(
            TEMP_DIR,
            temp_filename
        )

        content = await file.read()

        if not content:

            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty"
            )

        with open(input_path, "wb") as buffer:
            buffer.write(content)

        print("Saved file to:", input_path)

        result = VoiceService.transcribe(input_path)

        if os.path.exists(input_path):
            os.remove(input_path)

        return result

    except Exception as e:

        print("TRANSCRIBE ERROR:", str(e))

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.post("/api/v1/voice/coach/session")
async def voice_coach_session(
    contract_id: str = Form(...),
    user_id: str = Form(...),
    file: UploadFile = File(...)
):

    try:

        print("========== COACH SESSION ==========")

        file_ext = file.filename.split(".")[-1].lower()

        temp_filename = f"{uuid.uuid4()}.{file_ext}"

        input_path = os.path.join(
            TEMP_DIR,
            temp_filename
        )

        content = await file.read()

        with open(input_path, "wb") as buffer:
            buffer.write(content)

        transcription = VoiceService.transcribe(
            input_path
        )

        transcript = transcription["transcript"]

        print("Transcript:", transcript)

        if os.path.exists(input_path):
            os.remove(input_path)

        return StreamingResponse(
            stream_llm_response(transcript),
            media_type="text/event-stream"
        )

    except Exception as e:

        print("VOICE COACH ERROR:", str(e))

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )