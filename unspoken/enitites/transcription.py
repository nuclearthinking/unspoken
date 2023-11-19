from pydantic import BaseModel, Field


class TranscriptionSegment(BaseModel):
    id: int
    start: float
    end: float
    text: str


class TranscriptionResult(BaseModel):
    segments: list[TranscriptionSegment] = Field(default_factory=list)
