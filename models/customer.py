from pydantic import BaseModel
from typing import List
from .company import Field

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
    active: bool = True