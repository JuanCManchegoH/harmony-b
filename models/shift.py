from typing import List
from pydantic import BaseModel

from models.company import Step

class Shift(BaseModel):
    id: str = None
    day: str
    startTime: str
    endTime: str
    color: str
    abbreviation: str
    description: str
    sequence: str
    position: str
    type: str
    active: bool
    keep: bool
    worker: str
    workerName: str
    stall: str
    stallName: str
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
    sequence: str
    position: str
    type: str
    active: bool
    keep: bool
    worker: str
    workerName: str
    stall: str
    stallName: str
    
class AppliedSequence(BaseModel):
    stall: str
    worker: str
    sequence: List[Step]
    index: int
    jump: int
    
class CreateShifts(BaseModel):
    shifts: List[CreateShift]
    
class DeleteShifts(BaseModel):
    shifts: List[str]
    
class CreateAndUpdateShifts(BaseModel):
    create: List[CreateShift] = None
    update: List[UpdateShift] = None
    appliedSequence: AppliedSequence = None
    