from pydantic import BaseModel


class SpeakerResponse(BaseModel):
    id: int
    name: str
    task_id: int

    class Config:
        orm_mode = True
        from_attributes = True


class UpdateSpeakerNameRequest(BaseModel):
    name: str
