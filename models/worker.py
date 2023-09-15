from pydantic import BaseModel
from typing import List

class Field(BaseModel):
    id: str
    name: str
    type: str
    size: int
    value: str
    options: List[str]
    required: bool

class Worker(BaseModel):
    id: str = None
    name: str
    identification: str
    city: str
    phone: str
    address: str
    fields: List[Field]
    tags: List[str]
    company: str = None
    active: bool = True
    userName: str = None
    updatedBy: str = None
    createdAt: str = None
    updatedAt: str = None
    
class UpdateWorker(BaseModel):
    name: str
    identification: str
    city: str
    phone: str
    address: str
    fields: List[Field]
    tags: List[str]
    active: bool = True
    
class GetByIds(BaseModel):
    ids: List[str]