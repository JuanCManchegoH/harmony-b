from pydantic import BaseModel
from typing import List
from schemas.company import CompanyEntity

class User(BaseModel):
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
    id: str = None
    userName: str
    email: str
    password: str
    company: CompanyEntity
    customers: List[str]
    workers: List[str]
    roles: List[str]
    active: bool = True

class Login(BaseModel):
    email: str
    password: str
    
class UpdateUser(BaseModel):
    userName: str
    email: str
    customers: List[str]
    workers: List[str]
    roles: List[str]
