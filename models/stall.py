from pydantic import BaseModel
from typing import List
from models.company import Step

from models.shift import Shift

class StallWorker(BaseModel):
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
    name: str
    description: str
    ays: str
    branch: str
    stage: int
    tag: str
    
class UpdateStallWorker(BaseModel):
    sequence: List[Step]
    index: int
    jump: int

class GetStalls(BaseModel):
    months: List[str]
    years: List[str]
    customerId: str = None
    
class StallsAndShifts(BaseModel):
    stalls: List[Stall]
    shifts: List[Shift]
