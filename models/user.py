"""User models module."""

from typing import List
from pydantic import BaseModel
from schemas.company import company_entity

class User(BaseModel):
    """User model."""
    id: str = None
    userName: str
    email: str
    password: str
    company: str
    customers: List[str]
    workers: List[str]
    roles: List[str]
    active: bool = True

class Profile(BaseModel):
    """User models module."""
    id: str = None
    userName: str
    email: str
    password: str
    company: company_entity
    customers: List[str]
    workers: List[str]
    roles: List[str]
    active: bool = True

class Login(BaseModel):
    """Login model."""
    email: str
    password: str

class UpdateUser(BaseModel):
    """Update user model."""
    userName: str
    email: str
    customers: List[str]
    workers: List[str]
    roles: List[str]
