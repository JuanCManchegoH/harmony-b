from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from models.user import UpdateUser, User, Login
from schemas.user import UserEntity, UserEntityList
from utils.auth import decodeAccessToken
from utils.roles import required_roles
from utils.errorsResponses import errors
from services.users import UsersServices
from db.client import db_client
from services.websocket import manager
from models.websocket import WebsocketResponse

users = APIRouter(prefix='/users', tags=['Users'], responses={404: {"description": "Not found"}})
db = db_client["harmony"]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
user_services = UsersServices(db)

# create a user
@users.post(path="/", summary="Create a user", description="This endpoint creates a user in the database and returns the user object.", status_code=201)
async def createUser(new_user: User, token: str = Depends(oauth2_scheme)):
    # Validations
    token = decodeAccessToken(token)
    new_user_roles = new_user.roles
    required_role = "super_admin" if any(role in new_user_roles for role in ["super_admin"]) else "admin"
    required_roles(token["roles"], [required_role])
    # Create user
    result = user_services.createUser(new_user)
    result = UserEntity(result)
    print("Here")
    # Websocket
    user = UsersServices(db).getByEmail(token["email"])
    message = WebsocketResponse(event="user_created", data=result, userName=user["userName"], company=user["company"])
    await manager.broadcast(message)
    # Return
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=result)

# login
@users.post(path="/login", summary="Login", description="This endpoint logs a user in and returns a token.", status_code=200)
async def login(data: Login):
    # Create token
    result = UsersServices(db).login(data.email, data.password)
    # Return
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)

# get user profile
@users.get(path="/profile", summary="Get user by token", description="This endpoint returns a user by token.", status_code=200)
async def getByProfile(token: str = Depends(oauth2_scheme)):
    # Get token data
    token = decodeAccessToken(token)
    # Get profile
    result = UsersServices(db).getProfile(token["email"])
    result = UserEntity(result)
    # Return
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)

# get all users by company
@users.get(path="/company/{company}", summary="Get all users by company", description="This endpoint returns all users by company.", status_code=200)
async def getByCompany(company: str, token: str = Depends(oauth2_scheme)):
    # Get token data
    token = decodeAccessToken(token)
    # Get users
    result = UsersServices(db).getByCompany(company)
    result = UserEntityList(result)
    # Return
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)
    
# update a user
@users.put(path="/{id}", summary="Update a user", description="This endpoint updates a user in the database and returns the user object.", status_code=200)
async def update(user: UpdateUser, id: str, token: str = Depends(oauth2_scheme)):
    # Validations
    token = decodeAccessToken(token)
    user_to_update = UsersServices(db).getUser(id)
    if not user_to_update:
        raise errors["Update error"]
    user_roles = dict(user_to_update)["roles"]
    required_role = "super_admin" if any(role in user_roles for role in ["super_admin"]) else "admin"
    required_roles(token["roles"], [required_role])
    # Update user
    result = UsersServices(db).update(user, id)
    result = UserEntity(result)
    # Websocket
    user = UsersServices(db).getByEmail(token["email"])
    message = WebsocketResponse(event="user_updated", data=result, userName=result["userName"], company=user["company"])
    await manager.broadcast(message)
    # Return
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)
    
    
# delete a user
@users.delete(path="/{id}", summary="Delete a user", description="This endpoint deletes a user in the database and returns a boolean.", status_code=200)
async def delete(id: str, token: str = Depends(oauth2_scheme)):
    # Validations
    token = decodeAccessToken(token)
    user_to_delete = UsersServices(db).getUser(id)
    if not user_to_delete:
        raise errors["Delete error"]
    user_roles = dict(user_to_delete)["roles"]
    required_role = "super_admin" if any(role in user_roles for role in ["super_admin"]) else "admin"
    required_roles(token["roles"], [required_role])
    # Delete user
    result = UsersServices(db).delete(id)
    result = UserEntity(result)
    # Websocket
    user = UsersServices(db).getByEmail(token["email"])
    message = WebsocketResponse(event="user_deleted", data=result, userName=result["userName"], company=user["company"])
    await manager.broadcast(message)
    # Return
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)
