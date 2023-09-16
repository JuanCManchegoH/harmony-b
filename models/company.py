"""Company models module."""

from typing import List
from pydantic import BaseModel

class Field(BaseModel):
    """Field model."""
    id: str = None
    name: str
    type: str
    options: List[str]
    size: int
    required: bool
    active: bool = True

class Position(BaseModel):
    """Position model."""
    id: str = None
    name: str
    value: int
    year: int

class Convention(BaseModel):
    """Convention model."""
    id: str = None
    name: str
    color: str
    abbreviation: str
    keep: bool

class Step(BaseModel):
    """Step model."""
    startTime: str
    endTime: str
    color: str

class Sequence(BaseModel):
    """Sequence model."""
    id: str = None
    name: str
    steps: List[Step]

class Tag(BaseModel):
    """Tag model."""
    id: str = None
    name: str
    color: str
    scope: str

class Company(BaseModel):
    """Company model."""
    id: str = None
    name: str
    db: str
    website: str
    workerFields: List[Field]
    customerFields: List[Field]
    positions: List[Position]
    conventions: List[Convention]
    sequences: List[Sequence]
    tags: List[Tag]
    pColor: str
    sColor: str
    logo: str
    active: bool = True

class UpdateCompany(BaseModel):
    """Update company model."""
    name: str = None
    website: str = None
    pColor: str = None
    sColor: str = None
    logo: str = None
    active: bool = None
