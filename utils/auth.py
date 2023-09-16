"""This module contains the functions to handle the authentication of the users"""

import os
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from db.client import db_client
from models.auth import DecodedToken

db = db_client["harmony"]
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_WEEKS =  2

class Error(Exception):
    """Base class for exceptions in this module."""

def verify_password(plain_password: str, hashed_assword: str) -> bool:
    """Verify password with the hashed password."""
    return pwd_context.verify(plain_password, hashed_assword)

def get_hashed_password(password: str) -> str:
    """Get hashed password."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """Create access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(weeks=ACCESS_TOKEN_EXPIRE_WEEKS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> DecodedToken:
    """Decode access token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        roles: list = payload.get("roles")
        if email is None:
            raise Error("Could not validate credentials")
        return {"email": email, "roles": roles}
    except JWTError as exception:
        raise Error(f"Could not validate credentials: {exception}") from exception
