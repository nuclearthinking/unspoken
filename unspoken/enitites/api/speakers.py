from pydantic import BaseModel


class SpeakerResponse(BaseModel):
    id: int
    name: str
    task_id: int

    class Config:
        from_attributes = True


class UpdateSpeakerNameRequest(BaseModel):
    name: str
