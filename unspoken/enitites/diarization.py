from pydantic import BaseModel, Field


class SpeakerSegment(BaseModel):
    id: int
    start: float
    end: float
    duration: float
    speaker: str


class DiarizationResult(BaseModel):
    segments: list[SpeakerSegment] = Field(default_factory=list)
    speakers: list[str] = Field(default_factory=list)
    speakers_count: int = 0
