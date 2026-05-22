from pydantic import BaseModel
from typing import List


class TranscriptSegment(BaseModel):
    start: float
    end: float
    text: str


class VoiceTranscriptionResponse(BaseModel):
    transcript: str
    language: str
    confidence: float
    segments: List[TranscriptSegment]