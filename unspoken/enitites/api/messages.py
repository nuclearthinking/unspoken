from pydantic import Field, BaseModel


class UpdateMessageSpeakerRequest(BaseModel):
    speaker_id: int


class MessageResponse(BaseModel):
    id: int
    text: str
    start_time: float
    end_time: float
    task_id: int
    speaker_id: int | None = Field(default=None)

    class Config:
        from_attributes = True
