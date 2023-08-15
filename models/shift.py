from pydantic import BaseModel

class Shift(BaseModel):
    id: str = None
    day: str
    startTime: str
    endTime: str
    color: str
    abreviation: str
    description: str
    mode: int
    event: bool
    customerEvent: bool
    active: bool
    keep: bool
    worker: str
    stall: str
    customer: str
    createdBy: str = None
    updatedBy: str = None
    createdAt: str = None
    updatedAt: str = None