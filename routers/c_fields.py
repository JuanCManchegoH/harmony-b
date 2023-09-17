"""WFields router module."""

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pymongo.database import Database
from db.client import db_client
from services.companies import CompaniesServices
from services.users import UsersServices
from services.c_fields import CFieldsServices
from services.websocket import manager
from services.logs import LogsServices
from models.company import Field
from models.websocket import WebsocketResponse
from schemas.company import company_entity
from utils.auth import decode_access_token
from utils.roles import required_roles

cfields = APIRouter(
    prefix="/cfields",
    tags=["CFields"],
    responses={404: {"description": "Not found"}})
database = db_client["harmony"]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
companies_services = CompaniesServices(database)
cf_services = CFieldsServices(database)
users_services = UsersServices(database)
def logs_services(company_db: Database):
    """Logs services."""
    return LogsServices(company_db)

@cfields.post(
    path="",
    summary="Add a customer field",
    description="Add a customer field to a company",
    status_code=status.HTTP_201_CREATED)
async def add_cfield(field: Field, token: str = Depends(oauth2_scheme)) -> JSONResponse:
    """Add a customer field."""
    # Validations
    token = decode_access_token(token)
    required_roles(token["roles"], ["admin"])
    # encode customer field
    field = jsonable_encoder(field)
    # Add customer field
    user = users_services.get_by_email(token["email"])
    result = cf_services.add_cfield(user["company"], field)
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
        "type": "Campos de clientes",
        "message": f"El usuario {user['userName']} ha creado un campo de clientes"
    })
    # Return
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=result)

@cfields.put(
    path="/{field_id}",
    summary="Update a customer field",
    description="Update a customer field from a company",
    status_code=status.HTTP_200_OK)
async def update_cfield(
    field_id: str,
    field: Field,
    token: str = Depends(oauth2_scheme)) -> JSONResponse:
    """Update a customer field."""
    # Validations
    token = decode_access_token(token)
    required_roles(token["roles"], ["admin"])
    # encode customer field
    field = jsonable_encoder(field)
    # Update customer field
    user = users_services.get_by_email(token["email"])
    result = cf_services.update_cfield(user["company"], field_id, field)
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
        "type": "Campos de clientes",
        "message": f"El usuario {user['userName']} ha actualizado un campo de clientes"
    })
    # Return
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)

@cfields.delete(
    path="/{field_id}",
    summary="Delete a customer field",
    description="Delete a customer field from a company",
    status_code=status.HTTP_200_OK)
async def delete_cfield(field_id: str, token: str = Depends(oauth2_scheme)) -> JSONResponse:
    """Delete a customer field."""
    # Validations
    token = decode_access_token(token)
    required_roles(token["roles"], ["admin"])
    # Delete customer field
    user = users_services.get_by_email(token["email"])
    result = cf_services.delete_cfield(user["company"], field_id)
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
        "type": "Campos de clientes",
        "message": f"El usuario {user['userName']} ha eliminado un campo de clientes"
    })
    # Return
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)
