from pydantic import Field, BaseModel


class SpeachToTextSegment(BaseModel):
    id: int
    start: float
    end: float
    text: str


class SpeachToTextResult(BaseModel):
    segments: list[SpeachToTextSegment] = Field(default_factory=list)
