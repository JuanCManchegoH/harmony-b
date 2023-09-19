"""Shift model module."""

from typing import List
from pydantic import BaseModel
from models.company import Step

class Shift(BaseModel):
    """Shift model."""
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
    customer: str
    customerName: str
    company: str = None
    month: str
    year: str
    createdBy: str = None
    updatedBy: str = None
    createdAt: str = None
    updatedAt: str = None

class UpdateShift(BaseModel):
    """Update shift model."""
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
    """Create shift model."""
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
    customer: str
    customerName: str
    month: str
    year: str

class AppliedSequence(BaseModel):
    """Applied sequence model."""
    stall: str
    worker: str
    sequence: List[Step]
    index: int
    jump: int

class GetShifts(BaseModel):
    """Get shifts model."""
    months: List[str]
    years: List[str]
    types: List[str]

class CreateShifts(BaseModel):
    """Create shifts model."""
    shifts: List[CreateShift]

class UpdateShifts(BaseModel):
    """Update shifts model."""
    shifts: List[UpdateShift]

class DeleteShifts(BaseModel):
    """Delete shifts model."""
    shifts: List[str]

# class CreateAndUpdateShifts(BaseModel):
#     create: List[CreateShift] = None
#     update: List[UpdateShift] = None
#     appliedSequence: AppliedSequence = None
    