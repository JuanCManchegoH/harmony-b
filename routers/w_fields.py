"""WFields router module."""

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from pymongo.database import Database
from db.client import db_client
from services.companies import CompaniesServices
from services.users import UsersServices
from services.w_fields import WFieldsServices
from services.websocket import manager
from services.logs import LogsServices
from models.company import Field
from models.websocket import WebsocketResponse
from schemas.company import company_entity
from utils.auth import decode_access_token
from utils.roles import required_roles

wfields = APIRouter(
    prefix="/wfields",
    tags=["WFields"],
    responses={404: {"description": "Not found"}})
database = db_client["harmony"]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
companies_services = CompaniesServices(database)
wf_services = WFieldsServices(database)
users_services = UsersServices(database)
def logs_services(company_db: Database):
    """Logs services."""
    return LogsServices(company_db)

# add a worker field
@wfields.post(
    path="",
    summary="Add a worker field",
    description="Add a worker field to a company",
    status_code=status.HTTP_201_CREATED)
async def add_wfield(field: Field, token: str = Depends(oauth2_scheme)) -> JSONResponse:
    """Add a worker field."""
    # Validations
    token = decode_access_token(token)
    required_roles(token["roles"], ["admin"])
    # Add worker field
    user = users_services.get_by_email(token["email"])
    result = wf_services.add_wfield(user["company"], field)
    result = company_entity(result)
    # Websocket
    message = WebsocketResponse(
        event="company_updated",
        data=result,
        userName=user["userName"],
        company=user["company"])
    await manager.broadcast(message)
    # Log
    company = companies_services.get_company(user["company"])
    company_db = db_client[company["db"]]
    _ = logs_services(company_db).create_log({
        "company": user["company"],
        "user": user["email"],
        "userName": user["userName"],
        "type": "Campos de personal",
        "message": f"El usuario {user['userName']} ha creado un campo de personal"
    })
    # Return
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=result)

# update a worker field
@wfields.put(
    path="/{field_id}",
    summary="Update a worker field",
    description="Update a worker field from a company",
    status_code=status.HTTP_200_OK)
async def update_wfield(
    field_id: str,
    field: Field,
    token: str = Depends(oauth2_scheme)) -> JSONResponse:
    """Update a worker field."""
    # Validations
    token = decode_access_token(token)
    required_roles(token["roles"], ["admin"])
    # Update worker field
    user = users_services.get_by_email(token["email"])
    result = wf_services.update_wfield(user["company"], field_id, field)
    result = company_entity(result)
    # Websocket
    message = WebsocketResponse(
        event="company_updated",
        data=result,
        userName=user["userName"],
        company=user["company"])
    await manager.broadcast(message)
    # Log
    company = companies_services.get_company(user["company"])
    companyDb = db_client[company["db"]]
    _ = logs_services(companyDb).create_log({
        "company": user["company"],
        "user": user["email"],
        "userName": user["userName"],
        "type": "Campos de personal",
        "message": f"El usuario {user['userName']} ha actualizado un campo de personal"
    })
    # Return
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)

# delete a worker field
@wfields.delete(
    path="/{field_id}",
    summary="Delete a worker field",
    description="Delete a worker field from a company",
    status_code=status.HTTP_200_OK)
async def delete_wfield(field_id: str, token: str = Depends(oauth2_scheme)) -> JSONResponse:
    """Delete a worker field."""
    # Validations
    token = decode_access_token(token)
    required_roles(token["roles"], ["admin"])
    # Delete worker field
    user = users_services.get_by_email(token["email"])
    result = wf_services.delete_wfield(user["company"], field_id)
    result = company_entity(result)
    # Websocket
    message = WebsocketResponse(
        event="company_updated",
        data=result,
        userName=user["userName"],
        company=user["company"])
    await manager.broadcast(message)
    # Log
    company = companies_services.get_company(user["company"])
    company_db = db_client[company["db"]]
    _ = logs_services(company_db).create_log({
        "company": user["company"],
        "user": user["email"],
        "userName": user["userName"],
        "type": "Campos de personal",
        "message": f"El usuario {user['userName']} ha eliminado un campo de personal"
    })
    # Return
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)
