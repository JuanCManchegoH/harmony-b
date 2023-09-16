"""Log models module."""

from pydantic import BaseModel

class Log(BaseModel):
    """Log model."""
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
    """CreateLog model."""
    company: str = None
    user: str = None
    userName: str = None
    type: str = None
    message: str = None
