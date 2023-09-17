"""Customer model module."""

from typing import List
from pydantic import BaseModel

class Field(BaseModel):
    """Field model."""
    id: str
    name: str
    type: str
    size: int
    value: str
    options: List[str]
    required: bool

class Customer(BaseModel):
    """Customer model."""
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
    """UpdateCustomer model."""
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
    