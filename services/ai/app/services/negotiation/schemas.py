from pydantic import BaseModel
from typing import Optional


class NegotiationRequest(BaseModel):
    clause: str
    risk_level: str = "medium"
    contract_type: Optional[str] = None
    jurisdiction: Optional[str] = None


class NegotiationResponse(BaseModel):
    risk_explanation: str
    leverage_points: list[str]
    counter_offer: str
    negotiation_strategy: str
    communication_tone: str
    avatar_message: str

class TranscriptSegment(BaseModel):
    start: float 
    end: float
    text: str

class TranscriptResponse(BaseModel):
    transcript: str
    language: str
    confidence: float
    segments: List[TranscriptSegment]

class Viseme(BaseModel):
    time: float
    value: str

class AvatarPayload(BaseModel):
    emotion: str
    visemes: List[Viseme]
    animation: str