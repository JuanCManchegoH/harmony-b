from typing import List
from pydantic import BaseModel

class Shift(BaseModel):
    id: str = None
    day: str
    startTime: str
    endTime: str
    color: str
    abbreviation: str
    description: str
    mode: str
    type: str
    active: bool
    keep: bool
    worker: str
    stall: str
    company: str = None
    createdBy: str = None
    updatedBy: str = None
    createdAt: str = None
    updatedAt: str = None
    
class UpdateShift(BaseModel):
    id: str
    startTime: str
    endTime: str
    color: str
    abbreviation: str
    description: str
    mode: str
    type: str
    active: bool
    keep: bool
    
class CreateShift(BaseModel):
    day: str
    startTime: str
    endTime: str
    color: str
    abbreviation: str
    description: str
    mode: str
    type: str
    active: bool
    keep: bool
    worker: str
    stall: str

class CreateShifts(BaseModel):
    shifts: List[CreateShift]
    
class DeleteShifts(BaseModel):
    shifts: List[str]
    
class CreateAndUpdateShifts(BaseModel):
    create: List[CreateShift] = None
    update: List[UpdateShift] = None