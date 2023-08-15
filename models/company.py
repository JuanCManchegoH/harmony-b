from pydantic import BaseModel
from typing import List

# campo
class Field(BaseModel):
    id: str = None
    name: str
    type: str
    options: List[str]
    size: int
    required: bool
    active: bool = True

# cargo  
class Position(BaseModel):
    id: str = None
    name: str
    value: int
    year: int

# convencion   
class Convention(BaseModel):
    id: str = None
    name: str
    color: str
    abbreviation: str

# paso   
class Step(BaseModel):
    startTime: str
    endTime: str
    color: str

# secuencia
class Sequence(BaseModel):
    id: str = None
    name: str
    steps: List[Step]
    
# etiqueta
class Tag(BaseModel):
    id: str = None
    name: str
    color: str
    scope: str
    
class Company(BaseModel):
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
    name: str = None
    website: str = None
    pColor: str = None
    sColor: str = None
    logo: str = None
    active: bool = None