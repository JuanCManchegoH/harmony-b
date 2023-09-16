"""Conventions router module."""

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pymongo.database import Database
from db.client import db_client
from services.companies import CompaniesServices
from services.users import UsersServices
from services.conventions import ConventionsServices
from services.websocket import manager
from services.logs import LogsServices
from models.company import Convention
from models.websocket import WebsocketResponse
from schemas.company import company_entity
from utils.auth import decode_access_token
from utils.roles import required_roles

conventions = APIRouter(
    prefix="/conventions",
    tags=["Conventions"],
    responses={404: {"description": "Not found"}})
database = db_client["harmony"]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
companies_services = CompaniesServices(database)
conventions_services = ConventionsServices(database)
users_services = UsersServices(database)
def logs_services(company_db: Database):
    """Logs services."""
    return LogsServices(company_db)

@conventions.post(
    path="", summary="Add a convention",
    description="Add a convention to a company",
    status_code=status.HTTP_201_CREATED)
async def add_convention(
    convention: Convention,
    token: str = Depends(oauth2_scheme)) -> JSONResponse:
    """Add a convention."""
    # Validations
    token = decode_access_token(token)
    required_roles(token["roles"], ["admin"])
    # encode convention
    convention = jsonable_encoder(convention)
    # Add convention
    user = users_services.get_by_email(token["email"])
    result = conventions_services.add_convention(user["company"], convention)
    result = company_entity(result)
    # Websocket
    message = WebsocketResponse(
        event="company_updated",
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
        "type": "Convenciones",
        "message": f"El usuario {user['userName']} ha creado una convención"
    })
    # Return
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=result)

# update a convention
@conventions.put(
    path="/{convention_id}",
    summary="Update a convention",
    description="Update a convention from a company",
    status_code=status.HTTP_200_OK)
async def update_convention(
    convention_id: str,
    convention: Convention,
    token: str = Depends(oauth2_scheme)) -> JSONResponse:
    """Update a convention."""
    # Validations
    token = decode_access_token(token)
    required_roles(token["roles"], ["admin"])
    # encode convention
    convention = jsonable_encoder(convention)
    # Update convention
    user = users_services.get_by_email(token["email"])
    result = conventions_services.update_convention(user["company"], convention_id, convention)
    result = company_entity(result)
    # Websocket
    message = WebsocketResponse(
        event="company_updated",
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
        "type": "Convenciones",
        "message": f"El usuario {user['userName']} ha actualizado una convención"
    })
    # Return
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)

# delete a convention
@conventions.delete(
    path="/{convention_id}",
    summary="Delete a convention",
    description="Delete a convention from a company",
    status_code=status.HTTP_200_OK)
async def delete_convention(
    convention_id: str,
    token: str = Depends(oauth2_scheme)) -> JSONResponse:
    """Delete a convention."""
    # Validations
    token = decode_access_token(token) 
    required_roles(token["roles"], ["admin"])
    # Delete convention
    user = users_services.get_by_email(token["email"])
    result = conventions_services.delete_convention(user["company"], convention_id)
    result = company_entity(result)
    # Websocket
    message = WebsocketResponse(
        event="company_updated",
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
        "type": "Convenciones",
        "message": f"El usuario {user['userName']} ha eliminado una convención"
    })
    # Return
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)
