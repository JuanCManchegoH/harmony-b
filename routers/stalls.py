"""Stalls router module."""

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi.encoders import jsonable_encoder
from pymongo.database import Database
from db.client import db_client
from services.companies import CompaniesServices
from services.users import UsersServices
from services.stalls import StallsServices
from services.websocket import manager
from services.workers import WorkersServices
from services.logs import LogsServices
from models.shift import DeleteShifts
from models.stall import GetStalls, Stall, StallWorker, UpdateStall
from models.websocket import WebsocketResponse
from schemas.stall import stall_entity, stalls_and_shifts
from utils.auth import decode_access_token
from utils.roles import allowed_roles

stalls = APIRouter(prefix='/stalls', tags=['Stalls'], responses={404: {"description": "Not found"}})
database = db_client["harmony"]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
companies_services = CompaniesServices(database)
users_services = UsersServices(database)
def stalls_services(company_db: Database):
    """Stalls services."""
    return StallsServices(company_db)
def workers_services(company_db: Database):
    """Workers services."""
    return WorkersServices(company_db)
def logs_services(company_db: Database):
    """Logs services."""
    return LogsServices(company_db)


@stalls.post(
    path="",
    summary="Create a stall",
    description="This endpoint creates a stall in the database and returns the stall object.",
    status_code=201)
async def create_stall(stall: Stall, token: str = Depends(oauth2_scheme)) -> JSONResponse:
    """Create a stall."""
    # Validations
    token = decode_access_token(token)
    allowed_roles(token["roles"], ["handle_stalls", "admin"])
    # Encode stall
    stall = jsonable_encoder(stall)
    # Create stall
    user = users_services.get_by_email(token["email"])
    company = companies_services.get_company(user["company"])
    company_db = db_client[company["db"]]
    result = stalls_services(company_db).create_stall(stall, user)
    result = stall_entity(result)
    # Websocket
    message = WebsocketResponse(
        event="stall_created",
        data=result,
        userName=user["userName"],
        company=user["company"])
    await manager.broadcast(message)
    # Log
    message = (
        f"El usuario {user['userName']} ha creado el puesto {result['name']}. "
        f"Cliente: {result['customerName']}")
    _ = logs_services(company_db).create_log({
        "company": user["company"],
        "user": user["email"],
        "userName": user["userName"],
        "type": "Puestos",
        "message": message
    })
    # Return
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=result)

@stalls.post(
    path="/getByCustomer",
    summary="Find all stalls",
    description="This endpoint returns all stalls",
    status_code=200)
async def get_customer_stalls(data: GetStalls, token: str = Depends(oauth2_scheme)) -> JSONResponse:
    """Find all stalls."""
    # Validations
    token = decode_access_token(token)
    allowed_roles(token["roles"], ["read_stalls", "admin"])
    # Find all stalls
    user = users_services.get_by_email(token["email"])
    company = companies_services.get_company(user["company"])
    company_db = db_client[company["db"]]
    result = stalls_services(company_db).get_customer_stalls(
        user["company"], data.customerId, data.months, data.years, data.types)
    result = stalls_and_shifts(result["stalls"], result["shifts"])
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)

@stalls.post(
    path="/getByCustomers",
    summary="Find all stalls",
    description="This endpoint returns all stalls",
    status_code=200)
async def get_customers_stalls(
    data: GetStalls, token: str = Depends(oauth2_scheme)) -> JSONResponse:
    """Find all stalls."""
    # Validations
    token = decode_access_token(token)
    allowed_roles(token["roles"], ["read_stalls", "admin"])
    # Find all stalls
    user = users_services.get_by_email(token["email"])
    company = companies_services.get_company(user["company"])
    company_db = db_client[company["db"]]
    result = stalls_services(company_db).get_stalls(
        user["company"], data.months, data.years, data.types)
    result = stalls_and_shifts(result["stalls"], result["shifts"])
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)

@stalls.put(
    path="/{stall_id}",
    summary="Update a stall",
    description="This endpoint updates a stall in the database and returns the stall object.",
    status_code=200)
async def update_stall(
    stall_id: str, data: UpdateStall, token: str = Depends(oauth2_scheme)) -> JSONResponse:
    """Update a stall."""
    # Validations
    token = decode_access_token(token)
    allowed_roles(token["roles"], ["handle_stalls", "admin"])
    # Encode stall
    data = jsonable_encoder(data)
    # Update stall
    user = users_services.get_by_email(token["email"])
    company = companies_services.get_company(user["company"])
    company_db = db_client[company["db"]]
    result = stalls_services(company_db).update_stall(stall_id, data, user)
    result = stall_entity(result)
    # Websocket
    message = WebsocketResponse(
        event="stall_updated",
        data=result,
        userName=user["userName"],
        company=user["company"])
    await manager.broadcast(message)
    # Log
    message = (
        f"El usuario {user['userName']} ha actualizado el puesto {result['name']}. "
        f"Cliente: {result['customerName']}")
    _ = logs_services(company_db).create_log({
        "company": user["company"],
        "user": user["email"],
        "userName": user["userName"],
        "type": "Puestos",
        "message": message
    })
    # Return
    return result

@stalls.post(
    path="/{stall_id}",
    summary="Delete a stall",
    description="This endpoint deletes a stall in the database and returns the stall object.",
    status_code=200)
async def delete_stall(stall_id: str, data: DeleteShifts, token: str = Depends(oauth2_scheme)):
    """Delete a stall."""
    # Validations
    token = decode_access_token(token)
    allowed_roles(token["roles"], ["handle_stalls", "admin"])
    # Delete stall
    user = users_services.get_by_email(token["email"])
    company = companies_services.get_company(user["company"])
    company_db = db_client[company["db"]]
    result = stalls_services(company_db).delete_stall(user["company"], stall_id, data.shifts)
    result = stall_entity(result)
    # Websocket
    message = WebsocketResponse(
        event="stall_deleted",
        data=result, userName=user["userName"],
        company=user["company"])
    await manager.broadcast(message)
    # Log
    message = (
        f"El usuario {user['userName']} ha eliminado el puesto {result['name']}. "
        f"Cliente: {result['customerName']}")
    _ = logs_services(company_db).create_log({
        "company": user["company"],
        "user": user["email"],
        "userName": user["userName"],
        "type": "Puestos",
        "message": message
    })
    # Return
    return result

@stalls.post(
    path="/addWorker/{stall_id}",
    summary="Add a worker to a stall",
    description=
    "This endpoint adds a worker to a stall in the database and returns the stall object.",
    status_code=200)
async def add_stall_worker(
    stall_id: str, worker: StallWorker, token: str = Depends(oauth2_scheme)):
    """Add a worker to a stall."""
    # Validations
    token = decode_access_token(token)
    allowed_roles(token["roles"], ["handle_stalls", "admin"])
    # Encode stall worker
    worker = jsonable_encoder(worker)
    # Create stall worker
    user = users_services.get_by_email(token["email"])
    company = companies_services.get_company(user["company"])
    company_db = db_client[company["db"]]
    result = stalls_services(company_db).add_stall_worker(stall_id, worker, user)
    result = stall_entity(result)
    # Websocket
    message = WebsocketResponse(
        event="stall_updated",
        data=result,
        userName=user["userName"],
        company=user["company"])
    await manager.broadcast(message)
    # Log
    worker =  dict(worker)
    worker = workers_services(company_db).get_worker_by_id(user["company"], worker["id"])
    message = (
        f"El usuario {user['userName']} ha asignado a {worker['name']} al puesto {result['name']}. "
        f"Cliente: {result['customerName']}")
    _ = logs_services(company_db).create_log({
        "company": user["company"],
        "user": user["email"],
        "userName": user["userName"],
        "type": "Puestos",
        "message": message
    })
    # Return
    return result

@stalls.post(
    path="/removeWorker/{stall_id}/{worker_id}",
    summary="Remove a worker from a stall",
    description=
    "This endpoint removes a worker from a stall",
    status_code=200)
async def remove_worker(
    stall_id: str, worker_id: str, data: DeleteShifts, token: str = Depends(oauth2_scheme)):
    """Remove a worker from a stall."""
    # Validations
    token = decode_access_token(token)
    allowed_roles(token["roles"], ["handle_stalls", "admin"])
    # Delete stall worker
    user = users_services.get_by_email(token["email"])
    company = companies_services.get_company(user["company"])
    company_db = db_client[company["db"]]
    result = stalls_services(company_db).remove_worker(
        user["company"], stall_id, worker_id, data.shifts)
    result = stall_entity(result)
    # Websocket
    message = WebsocketResponse(
        event="stall_updated",
        data=result,
        userName=user["userName"],
        company=user["company"])
    await manager.broadcast(message)
    # Log
    worker = workers_services(company_db).get_worker_by_id(user["company"], worker_id)
    message = (
        f"El usuario {user['userName']} ha eliminado a {worker['name']}, puesto {result['name']}. "
        f"Cliente: {result['customerName']}")
    _ = logs_services(company_db).create_log({
        "company": user["company"],
        "user": user["email"],
        "userName": user["userName"],
        "type": "Puestos",
        "message": message
    })
    # Return
    return result
