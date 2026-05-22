from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import StreamingResponse

import asyncio
import json
import os
import uuid

from .voice_service import VoiceService
from .avatar_service import AvatarService

router = APIRouter(
    tags=["Voice Coach"]
)


async def fake_llm_stream(user_text: str):

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


async def transcribe_internal(file: UploadFile):

    TEMP_DIR = "app/audio_tmp"

    os.makedirs(TEMP_DIR, exist_ok=True)

    file_ext = file.filename.split(".")[-1]

    temp_filename = f"{uuid.uuid4()}.{file_ext}"

    input_path = os.path.join(
        TEMP_DIR,
        temp_filename
    )

    content = await file.read()

    with open(input_path, "wb") as buffer:
        buffer.write(content)

    result = VoiceService.transcribe(input_path)

    os.remove(input_path)

    return result


@router.post(
    "/api/v1/voice/coach/session"
)
async def voice_coach_session(
    contract_id: str = Form(...),
    user_id: str = Form(...),
    file: UploadFile = File(...)
):

    transcription = await transcribe_internal(file)

    transcript = transcription["transcript"]

    return StreamingResponse(
        fake_llm_stream(transcript),
        media_type="text/event-stream"
    )