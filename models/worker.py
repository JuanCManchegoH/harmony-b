"""Worker model module."""

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

class Worker(BaseModel):
    """Worker model."""
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
    """UpdateWorker model."""
    name: str
    identification: str
    city: str
    phone: str
    address: str
    fields: List[Field]
    tags: List[str]
    active: bool = True

class GetByIds(BaseModel):
    """GetByIds model."""
    ids: List[str]

class CreateAndUpdate(BaseModel):
    """CreateAndUpdate model."""
    workers: List[Worker]
