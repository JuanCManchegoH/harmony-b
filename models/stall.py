from pydantic import BaseModel
from typing import List

from models.shift import Shift

class StallWorker(BaseModel):
    id: str #Worker id
    name: str #Worker name
    identification: str #Worker identification
    position: str #Worker position
    sequence: str #sequence aplied to the worker
    index: int #first step
    jump: int #days jumped
    tag: str #tag
    mode: str #projection or execution
    userName: str = None
    updatedBy: str = None
    createdAt: str = None
    updatedAt: str = None

class Stall(BaseModel):
    id: str = None
    name: str
    description: str
    ays: int
    place: str
    monthAndYear: str
    customer: str
    customerName: str
    workers: List[StallWorker]
    createdBy: str = None
    updatedBy: str = None
    createdAt: str = None
    updatedAt: str = None
    
class UpdateStall(BaseModel):
    name: str
    description: str
    ays: int
    place: str
    
class UpdateStallWorker(BaseModel):
    id: str
    name: str
    identification: str
    position: str
    sequence: str
    index: int
    jump: int
    tag: str
    mode: str
    
class StallsAndShifts(BaseModel):
    stalls: List[Stall]
    shifts: List[Shift]