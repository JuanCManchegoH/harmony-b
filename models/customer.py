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

class Customer(BaseModel):
    id: str = None
    name: str
    identification: str
    city: str
    contact: str
    phone: str
    address: str
    fields: List[Field]
    tags: List[str]
    branches: List[str]
    company: str = None
    active: bool = True
    userName: str = None
    updatedBy: str = None
    createdAt: str = None
    updatedAt: str = None
    
class UpdateCustomer(BaseModel):
    name: str
    identification: str
    city: str
    contact: str
    phone: str
    address: str
    fields: List[Field]
    tags: List[str]
    branches: List[str]
    active: bool = True
    