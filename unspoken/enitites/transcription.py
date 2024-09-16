from pydantic import BaseModel, Field


class TranscriptionSegment(BaseModel):
    start: float
    end: float
    text: str
    speaker: str


class TranscriptionResult(BaseModel):
    messages: list[TranscriptionSegment] = Field(default_factory=list)
    file_name: str | None = None
    duration: float | None = None
