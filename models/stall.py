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
    mode: str #projection or execution
    createdBy: str = None
    updatedBy: str = None
    createdAt: str = None
    updatedAt: str = None

class Stall(BaseModel):
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
    createdBy: str = None
    updatedBy: str = None
    createdAt: str = None
    updatedAt: str = None
    
class UpdateStall(BaseModel):
    name: str
    description: str
    ays: str
    branch: str
    stage: int
    
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


class GetStalls(BaseModel):
    months: List[str]
    years: List[str]
    customerId: str = None
    
class StallsAndShifts(BaseModel):
    stalls: List[Stall]
    shifts: List[Shift]
