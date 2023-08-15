from pydantic import BaseModel
from typing import List

class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    id: str = None
    userName: str
    email: str
    password: str
    company: str
    customers: List[str]
    roles: List[str]
    active: bool = True

class Login(BaseModel):
    email: str
    password: str
    
class UpdateUser(BaseModel):
    userName: str
    email: str
    active: bool = True
    
class UpdateUserRoles(BaseModel):
    roles: List[str]
    
class UpdateUserCustomers(BaseModel):
    customers: List[str]