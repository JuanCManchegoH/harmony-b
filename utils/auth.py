import os
from jose import JWTError, jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from db.client import db_client
from schemas.user import UserEntity

db = db_client["harmony"]
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 90

def verifyPassword(plainPassword, hashedPassword):
    return pwd_context.verify(plainPassword, hashedPassword)

def getHashedPassword(password):
    return pwd_context.hash(password)

def authenticateUser(email: str, password: str):
    user = db.users.find_one({"email": email})
    if not user:
        return False
    if not verifyPassword(password, user["password"]):
        return False
    return UserEntity(user)

def createAccessToken(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decodeAccessToken(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        roles: list = payload.get("roles")
        if email is None:
            return False
        return {"email": email, "roles": roles}
    except JWTError:
        return False

def validateRoles(roles: list, required_roles: list):
    if "admin" in roles:
        return True
    for role in required_roles:
        if role not in roles:
            return False
    return True