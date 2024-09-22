from pydantic import Field, BaseModel


class SpeachToTextSegment(BaseModel):
    id: int
    start: float
    end: float
    text: str
    speaker: str = ''


class SpeachToTextResult(BaseModel):
    segments: list[SpeachToTextSegment] = Field(default_factory=list)
    speakers: list[str] = Field(default_factory=list)
