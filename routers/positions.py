"""Positions router module."""

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pymongo.database import Database
from db.client import db_client
from services.companies import CompaniesServices
from services.users import UsersServices
from services.positions import PositionsServices
from services.websocket import manager
from services.logs import LogsServices
from models.company import Position
from models.websocket import WebsocketResponse
from schemas.company import company_entity
from utils.auth import decode_access_token
from utils.roles import required_roles

positions = APIRouter(
    prefix="/positions",
    tags=["Positions"],
    responses={404: {"description": "Not found"}})
database = db_client["harmony"]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
companies_services = CompaniesServices(database)
positions_services = PositionsServices(database)
users_services = UsersServices(database)
def logs_services(company_db: Database):
    """Logs services."""
    return LogsServices(company_db)

@positions.post(
    path="", summary="Add a position",
    description="Add a position to a company",
    status_code=status.HTTP_201_CREATED)
async def add_position(position: Position, token: str = Depends(oauth2_scheme)) -> JSONResponse:
    """Add a position."""
    # Validations
    token = decode_access_token(token)
    required_roles(token["roles"], ["admin"])
    # encode position
    position = jsonable_encoder(position)
    # Add position
    user = users_services.get_by_email(token["email"])
    result = positions_services.add_position(user["company"], position)
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
        "type": "Cargos",
        "message": f"El usuario {user['userName']} ha creado un cargo"
    })
    # Return
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=result)

# update a position
@positions.put(
    path="/{position_id}",
    summary="Update a position",
    description="Update a position from a company",
    status_code=status.HTTP_200_OK)
async def update_position(
    position_id: str,
    position: Position,
    token: str = Depends(oauth2_scheme)) -> JSONResponse:
    """Update a position."""
    # Validations
    token = decode_access_token(token)
    required_roles(token["roles"], ["admin"])
    # encode position
    position = jsonable_encoder(position)
    # Update position
    user = users_services.get_by_email(token["email"])
    result = positions_services.update_position(user["company"], position_id, position)
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
        "type": "Cargos",
        "message": f"El usuario {user['userName']} ha actualizado un cargo"
    })
    # Return
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)

# delete a position
@positions.delete(
    path="/{position_id}",
    summary="Delete a position",
    description="Delete a position from a company",
    status_code=status.HTTP_200_OK)
async def delete_position(position_id: str, token: str = Depends(oauth2_scheme)) -> JSONResponse:
    """Delete a position."""
    # Validations
    token = decode_access_token(token)
    required_roles(token["roles"], ["admin"])
    # Delete position
    user = users_services.get_by_email(token["email"])
    result = positions_services.delete_position(user["company"], position_id)
    result = company_entity(result)
    # Websocket
    message = WebsocketResponse(
        event="company_updated",
        data=result, userName=user["userName"],
        company=user["company"])
    await manager.broadcast(message)
    # Log
    company = companies_services.get_company(user["company"])
    companyDb = db_client[company["db"]]
    _ = logs_services(companyDb).create_log({
        "company": user["company"],
        "user": user["email"],
        "userName": user["userName"],
        "type": "Cargos",
        "message": f"El usuario {user['userName']} ha eliminado un cargo"
    })
    # Return
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)
