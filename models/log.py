from typing import List
from pydantic import BaseModel

class Log(BaseModel):
    id: str = None
    company: str = None
    user: str = None
    userName: str = None
    type: str = None
    message: str = None
    month: str = None
    year: str = None
    createdAt: str = None

class CreateLog(BaseModel):
    company: str = None
    user: str = None
    userName: str = None
    type: str = None
    message: str = None