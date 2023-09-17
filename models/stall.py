"""Stall models module."""

from typing import List
from pydantic import BaseModel
from models.company import Step
from models.shift import Shift

class StallWorker(BaseModel):
    """Stall worker model."""
    id: str #Worker id
    name: str #Worker name
    identification: str #Worker identification
    position: str #Worker position
    sequence: List[Step]
    index: int #first step
    jump: int #days jumped
    createdBy: str = None
    updatedBy: str = None
    createdAt: str = None
    updatedAt: str = None

class Stall(BaseModel):
    """Stall model."""
    id: str = None
    name: str
    description: str
    ays: str
    branch: str
    month:str
    year:str
    customer: str
    customerName: str
    workers: List[StallWorker]
    stage: int
    tag: str
    createdBy: str = None
    updatedBy: str = None
    createdAt: str = None
    updatedAt: str = None

class UpdateStall(BaseModel):
    """Update stall model."""
    name: str
    description: str
    ays: str
    branch: str
    stage: int
    tag: str

class UpdateStallWorker(BaseModel):
    """Update stall worker model."""
    sequence: List[Step]
    index: int
    jump: int

class GetStalls(BaseModel):
    """Get stalls model."""
    months: List[str]
    years: List[str]
    types: List[str]
    customerId: str = None

class StallsAndShifts(BaseModel):
    """Stalls and shifts model."""
    stalls: List[Stall]
    shifts: List[Shift]
