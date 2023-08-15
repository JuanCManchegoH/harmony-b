from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from models.user import UpdateUser, UpdateUserRoles, UpdateUserCustomers, User, Login
from utils.auth import authenticateUser, decodeAccessToken, validateRoles
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
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired.")
    if not validateRoles(token["roles"], ["handle_user"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    if UsersServices(db).getByEmail(newUser.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered.")
    result = UsersServices(db).createUser(newUser)
    user = UsersServices(db).getByEmail(token["email"])
    if result:
        message = WebsocketResponse(event="user_created", data=result, userName=user["userName"], company=user["company"])
        await manager.broadcast(message)
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=result)
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error creating user.") 

# login
@users.post(path="/login", summary="Login", description="This endpoint logs a user in and returns a token.", status_code=200)
async def login(data: Login):
    user = authenticateUser(data.email, data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    result = UsersServices(db).login(user)
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)

# get user profile
@users.get(path="/profile", summary="Get user by token", description="This endpoint returns a user by token.", status_code=200)
async def getByProfile(token: str = Depends(oauth2_scheme)):
    token = decodeAccessToken(token)
    if token == False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired.")
    result = UsersServices(db).getProfile(token["email"])
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No user found.")
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)

# get all users by company
@users.get(path="/company/{company}", summary="Get all users by company", description="This endpoint returns all users by company.", status_code=200)
async def getByCompany(company: str, token: str = Depends(oauth2_scheme)):
    token = decodeAccessToken(token)
    if token == False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired.")
    if not validateRoles(token["roles"], ["handle_user"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    result = UsersServices(db).getByCompany(company)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No users found.")
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)

# update a user's roles
@users.put(path="/roles/{id}", summary="Update a user's roles", description="This endpoint updates a user's roles in the database and returns the user object.", status_code=200)
async def updateRoles(data: UpdateUserRoles, id: str, token: str = Depends(oauth2_scheme)):
    token = decodeAccessToken(token)
    if token == False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired.")
    if not validateRoles(token["roles"], ["handle_user"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    result = UsersServices(db).updateRoles(data.roles, id)
    user = UsersServices(db).getByEmail(token["email"])
    if result:
        message = WebsocketResponse(event="user_updated", data=result, userName=result["userName"], company=user["company"])
        await manager.broadcast(message)
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Error updating user roles.")
    
# update a user's customers
@users.put(path="/customers/{id}", summary="Update a user's customers", description="This endpoint updates a user's customers in the database and returns the user object.", status_code=200)
async def updateCustomers(data: UpdateUserCustomers, id: str, token: str = Depends(oauth2_scheme)):
    token = decodeAccessToken(token)
    if token == False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired.")
    if not validateRoles(token["roles"], ["handle_user"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    result = UsersServices(db).updateCustomers(data.customers, id)
    user = UsersServices(db).getByEmail(token["email"])
    if result:
        message = WebsocketResponse(event="user_updated", data=result, userName=result["userName"], company=user["company"])
        await manager.broadcast(message)
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Error updating user customers.")
    
# update a user
@users.put(path="/{id}", summary="Update a user", description="This endpoint updates a user in the database and returns the user object.", status_code=200)
async def update(user: UpdateUser, id: str, token: str = Depends(oauth2_scheme)):
    token = decodeAccessToken(token)
    print(id)
    if token == False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired.")
    if not validateRoles(token["roles"], ["handle_user"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    result = UsersServices(db).update(user, id)
    user = UsersServices(db).getByEmail(token["email"])
    if result:
        message = WebsocketResponse(event="user_updated", data=result, userName=result["userName"], company=user["company"])
        await manager.broadcast(message)
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Error updating user.")

# delete a user
@users.delete(path="/{id}", summary="Delete a user", description="This endpoint deletes a user in the database and returns a boolean.", status_code=200)
async def delete(id: str, token: str = Depends(oauth2_scheme)):
    token = decodeAccessToken(token)
    if token == False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired.")
    if not validateRoles(token["roles"], ["handle_user"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    result = UsersServices(db).delete(id)
    user = UsersServices(db).getByEmail(token["email"])
    if result:
        message = WebsocketResponse(event="user_deleted", data=result, userName=result["userName"], company=user["company"])
        await manager.broadcast(message)
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Error deleting user.")
