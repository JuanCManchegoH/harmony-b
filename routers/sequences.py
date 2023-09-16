"""Sequence router module."""

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pymongo.database import Database
from db.client import db_client
from services.companies import CompaniesServices
from services.users import UsersServices
from services.sequences import SequencesServices
from services.websocket import manager
from services.logs import LogsServices
from models.company import Sequence
from models.websocket import WebsocketResponse
from schemas.company import company_entity
from utils.auth import decode_access_token
from utils.roles import required_roles

sequences = APIRouter(
    prefix="/sequences",
    tags=["Sequences"],
    responses={404: {"description": "Not found"}})
database = db_client["harmony"]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
companies_services = CompaniesServices(database)
sequences_services = SequencesServices(database)
users_services = UsersServices(database)
def logs_services(company_db: Database):
    """Logs services."""
    return LogsServices(company_db)

# add a sequence
@sequences.post(
    path="", summary="Add a sequence",
    description="Add a sequence to a company",
    status_code=status.HTTP_201_CREATED)
async def add_sequence(sequence: Sequence, token: str = Depends(oauth2_scheme)) -> JSONResponse:
    """Add a sequence."""
    # Validations
    token = decode_access_token(token)
    required_roles(token["roles"], ["admin"])
    # encode sequence
    sequence = jsonable_encoder(sequence)
    # Add sequence
    user = users_services.get_by_email(token["email"])
    result = sequences_services.add_sequence(user["company"], sequence)
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
        "type": "Secuencias",
        "message": f"El usuario {user['userName']} ha creado una secuencia"
    })
    # Return
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=result)

# update a sequence
@sequences.put(
    path="/{sequence_id}",
    summary="Update a sequence",
    description="Update a sequence from a company",
    status_code=status.HTTP_200_OK)
async def update_sequence(
    sequence_id: str,
    sequence: Sequence,
    token: str = Depends(oauth2_scheme)) -> JSONResponse:
    """Update a sequence."""
    # Validations
    token = decode_access_token(token)
    required_roles(token["roles"], ["admin"])
    # encode sequence
    sequence = jsonable_encoder(sequence)
    # Update sequence
    user = users_services.get_by_email(token["email"])
    result = sequences_services.update_sequence(user["company"], sequence_id, sequence)
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
        "type": "Secuencias",
        "message": f"El usuario {user['userName']} ha actualizado una secuencia"
    })
    # Return
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)

# delete a sequence
@sequences.delete(
    path="/{sequence_id}",
    summary="Delete a sequence",
    description="Delete a sequence from a company",
    status_code=status.HTTP_200_OK)
async def delete_sequence(sequence_id: str, token: str = Depends(oauth2_scheme)) -> JSONResponse:
    """Delete a sequence."""
    # Validations
    token = decode_access_token(token)
    required_roles(token["roles"], ["admin"])
    # Delete sequence
    user = users_services.get_by_email(token["email"])
    result = sequences_services.delete_sequence(user["company"], sequence_id)
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
        "type": "Secuencias",
        "message": f"El usuario {user['userName']} ha eliminado una secuencia"
    })
    # Return
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)
