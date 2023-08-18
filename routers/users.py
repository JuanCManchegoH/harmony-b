from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from models.user import UpdateUser, User, Login
from utils.auth import authenticateUser, decodeAccessToken
from utils.roles import validateRoles
from utils.errorsResponses import errors
from services.users import UsersServices
from db.client import db_client
from services.websocket import manager
from models.websocket import WebsocketResponse

users = APIRouter(prefix='/users', tags=['Users'], responses={404: {"description": "Not found"}})
db = db_client["harmony"]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# create a user
@users.post(path="/", summary="Create a user", description="This endpoint creates a user in the database and returns the user object.", status_code=201)
async def createUser(newUser: User, token: str = Depends(oauth2_scheme)):
    token = decodeAccessToken(token)
    if token == False:
        raise errors["Token expired"]
    if not validateRoles(token["roles"], ["admin"], []):
        raise errors["Unauthorized"]
    result = UsersServices(db).createUser(newUser)
    user = UsersServices(db).getByEmail(token["email"])
    message = WebsocketResponse(event="user_created", data=result, userName=user["userName"], company=user["company"])
    await manager.broadcast(message)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=result)

# login
@users.post(path="/login", summary="Login", description="This endpoint logs a user in and returns a token.", status_code=200)
async def login(data: Login):
    user = authenticateUser(data.email, data.password)
    if not user:
        raise errors["Unauthorized"]
    result = UsersServices(db).login(user)
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)

# get user profile
@users.get(path="/profile", summary="Get user by token", description="This endpoint returns a user by token.", status_code=200)
async def getByProfile(token: str = Depends(oauth2_scheme)):
    token = decodeAccessToken(token)
    if token == False:
        raise errors["Token expired"]
    result = UsersServices(db).getProfile(token["email"])
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)

# get all users by company
@users.get(path="/company/{company}", summary="Get all users by company", description="This endpoint returns all users by company.", status_code=200)
async def getByCompany(company: str, token: str = Depends(oauth2_scheme)):
    token = decodeAccessToken(token)
    if token == False:
        raise errors["Token expired"]
    result = UsersServices(db).getByCompany(company)
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)
    
# update a user
@users.put(path="/{id}", summary="Update a user", description="This endpoint updates a user in the database and returns the user object.", status_code=200)
async def update(user: UpdateUser, id: str, token: str = Depends(oauth2_scheme)):
    token = decodeAccessToken(token)
    print(id)
    if token == False:
        raise errors["Token expired"]
    if not validateRoles(token["roles"], ["admin"], []):
        raise errors["Unauthorized"]
    result = UsersServices(db).update(user, id)
    user = UsersServices(db).getByEmail(token["email"])
    message = WebsocketResponse(event="user_updated", data=result, userName=result["userName"], company=user["company"])
    await manager.broadcast(message)
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)

# delete a user
@users.delete(path="/{id}", summary="Delete a user", description="This endpoint deletes a user in the database and returns a boolean.", status_code=200)
async def delete(id: str, token: str = Depends(oauth2_scheme)):
    token = decodeAccessToken(token)
    if token == False:
        raise errors["Token expired"]
    if not validateRoles(token["roles"], ["admin"], []):
        raise errors["Unauthorized"]
    result = UsersServices(db).delete(id)
    user = UsersServices(db).getByEmail(token["email"])
    message = WebsocketResponse(event="user_deleted", data=result, userName=result["userName"], company=user["company"])
    await manager.broadcast(message)
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)
