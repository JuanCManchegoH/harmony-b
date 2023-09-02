import os
from jose import JWTError, jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from db.client import db_client
from models.auth import DecodedToken
from .errorsResponses import errors

db = db_client["harmony"]
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120

def verifyPassword(plainPassword, hashedPassword) -> bool:
    return pwd_context.verify(plainPassword, hashedPassword)

def getHashedPassword(password) -> str:
    return pwd_context.hash(password)

def createAccessToken(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decodeAccessToken(token: str) -> DecodedToken:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        roles: list = payload.get("roles")
        if email is None:
            raise errors["Token expired"]
        return {"email": email, "roles": roles}
    except JWTError:
        raise errors["Token expired"]