"""Users router module."""

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi.encoders import jsonable_encoder
from pymongo.database import Database
from db.client import db_client
from models.user import UpdateUser, User, Login
from models.websocket import WebsocketResponse
from schemas.user import user_entity, user_entity_list
from utils.auth import decode_access_token
from utils.roles import required_roles
from utils.errorsResponses import errors
from services.companies import CompaniesServices
from services.websocket import manager
from services.users import UsersServices
from services.logs import LogsServices

users = APIRouter(prefix='/users', tags=['Users'], responses={404: {"description": "Not found"}})
database = db_client["harmony"]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
user_services = UsersServices(database)
companies_services = CompaniesServices(database)
def logs_services(company_db: Database):
    """Logs services."""
    return LogsServices(company_db)

@users.post(
    path="",
    summary="Create a user",
    description="This endpoint creates a user in the database and returns the user object.",
    status_code=201)
async def create_user(new_user: User, token: str = Depends(oauth2_scheme)):
    """Create a user."""
    # Validations
    token = decode_access_token(token)
    new_user_roles = new_user.roles
    required_role = "super_admin" if any(
        role in new_user_roles for role in ["super_admin"]) else "admin"
    required_roles(token["roles"], [required_role])
    # encode user
    new_user = jsonable_encoder(new_user)
    # Create user
    result = user_services.create_user(new_user)
    result = user_entity(result)
    # Websocket
    user = user_services.get_by_email(token["email"])
    message = WebsocketResponse(
        event="user_created",
        data=result, userName=user["userName"],
        company=user["company"])
    await manager.broadcast(message)
    # Log
    company = companies_services.get_company(user["company"])
    company_db = db_client[company["db"]]
    _ = logs_services(company_db).create_log({
        "company": user["company"],
        "user": user["email"],
        "userName": user["userName"],
        "type": "Usuarios",
        "message": f"El usuario {user['userName']} ha creado el usuario {result['userName']}"
    })
    # Return
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=result)

@users.post(
    path="/login",
    summary="Login",
    description="This endpoint logs a user in and returns a token.",
    status_code=200)
async def login(data: Login):
    """Login a user."""
    # Create token
    result = user_services.login(data.email, data.password)
    # Return
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)

@users.get(
    path="/profile",
    summary="Get user by token",
    description="This endpoint returns a user by token.",
    status_code=200)
async def get_by_profile(token: str = Depends(oauth2_scheme)):
    """Get user by token."""
    # Get token data
    token = decode_access_token(token)
    # Get profile
    result = user_services.get_profile(token["email"])
    result = user_entity(result)
    # Return
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)

@users.get(
    path="/company/{company}",
    summary="Get all users by company",
    description="This endpoint returns all users by company.",
    status_code=200)
async def get_by_company(company: str, token: str = Depends(oauth2_scheme)):
    """Get all users by company."""
    # Get token data
    token = decode_access_token(token)
    # Get users
    result = user_services.get_by_company(company)
    result = user_entity_list(result)
    # Return
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)

@users.put(
    path="/{user_id}",
    summary="Update a user",
    description="This endpoint updates a user in the database and returns the user object.",
    status_code=200)
async def update_user(user: UpdateUser, user_id: str, token: str = Depends(oauth2_scheme)):
    """Update a user."""
    # Validations
    token = decode_access_token(token)
    user_to_update = user_services.get_user(user_id)
    user_roles = dict(user_to_update)["roles"]
    required_role = "super_admin" if any(
        role in user_roles for role in ["super_admin"]) else "admin"
    required_roles(token["roles"], [required_role])
    # encode user
    user = jsonable_encoder(user)
    # Update user
    result = user_services.update_user(user, user_id)
    result = user_entity(result)
    # Websocket
    user = user_services.get_by_email(token["email"])
    message = WebsocketResponse(
        event="user_updated",
        data=result, userName=result["userName"],
        company=user["company"])
    await manager.broadcast(message)
    # Log
    company = companies_services.get_company(user["company"])
    company_db = db_client[company["db"]]
    _ = logs_services(company_db).create_log({
        "company": user["company"],
        "user": user["email"],
        "userName": user["userName"],
        "type": "Usuarios",
        "message": f"El usuario {user['userName']} ha actualizado el usuario {result['userName']}"
    })
    # Return
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)

# delete a user
@users.delete(
    path="/{user_id}",
    summary="Delete a user",
    description="This endpoint deletes a user in the database and returns a boolean.",
    status_code=200)
async def delete_user(user_id: str, token: str = Depends(oauth2_scheme)):
    """Delete a user."""
    # Validations
    token = decode_access_token(token)
    user_to_delete = user_services.get_user(user_id)
    if not user_to_delete:
        raise errors["Delete error"]
    user_roles = dict(user_to_delete)["roles"]
    required_role = "super_admin" if any(
        role in user_roles for role in ["super_admin"]) else "admin"
    required_roles(token["roles"], [required_role])
    # Delete user
    result = user_services.delete_user(user_id)
    result = user_entity(result)
    # Websocket
    user = user_services.get_by_email(token["email"])
    message = WebsocketResponse(
        event="user_deleted",
        data=result, userName=result["userName"],
        company=user["company"])
    await manager.broadcast(message)
    # Log
    company = companies_services.get_company(user["company"])
    company_db = db_client[company["db"]]
    _ = logs_services(company_db).create_log({
        "company": user["company"],
        "user": user["email"],
        "userName": user["userName"],
        "type": "Usuarios",
        "message": f"El usuario {user['userName']} ha eliminado el usuario {result['userName']}"
    })
    # Return
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)
