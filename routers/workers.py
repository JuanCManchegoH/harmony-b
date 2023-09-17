"""Workers router module."""

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi.encoders import jsonable_encoder
from pymongo.database import Database
from db.client import db_client
from services.users import UsersServices
from services.companies import CompaniesServices
from services.workers import WorkersServices
from services.websocket import manager
from services.logs import LogsServices
from models.worker import GetByIds, Worker, UpdateWorker
from models.websocket import WebsocketResponse
from schemas.worker import worker_entity, worker_entity_list
from schemas.user import user_entity
from utils.auth import decode_access_token
from utils.roles import allowed_roles

workers = APIRouter(
    prefix='/workers',
    tags=['Workers'],
    responses={404: {"description": "Not found"}})
database = db_client["harmony"]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
user_services = UsersServices(database)
companies_services = CompaniesServices(database)
def workers_services(company_db: Database):
    """Workers services."""
    return WorkersServices(company_db)
def logs_services(company_db: Database):
    """Logs services."""
    return LogsServices(company_db)

@workers.post(
    path="",
    summary="Create a worker",
    description="This endpoint creates a worker in the database and returns the worker object.",
    status_code=201)
async def create_worker(worker: Worker, token: str = Depends(oauth2_scheme)) -> JSONResponse:
    """Create a worker."""
    # Validations
    token = decode_access_token(token)
    allowed_roles(token["roles"], ["handle_workers", "admin"])
    # Encode worker
    worker = jsonable_encoder(worker)
    # Create worker
    user = user_services.get_by_email(token["email"])
    company = companies_services.get_company(user["company"])
    company_db = db_client[company["db"]]
    result = workers_services(company_db).create_worker(user["company"], worker, user_entity(user))
    result = worker_entity(result)
    # Websocket
    message = WebsocketResponse(
        event="worker_created",
        data=result, userName=user["userName"],
        company=user["company"])
    await manager.broadcast(message)
    # Log
    _ = logs_services(company_db).create_log({
        "company": user["company"],
        "user": user["email"],
        "userName": user["userName"],
        "type": "Personal",
        "message": f"El usuario {user['userName']} ha creado a la persona {result['name']}"
    })
    # Return
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=result)

@workers.get(
    path="/{search}/{limit}/{skip}",
    summary="Find workers by name or identification",
    description="This endpoint finds workers by name or identification",
    status_code=200)
async def get_workers(
    search: str,
    limit: int,
    skip: int,
    token: str = Depends(oauth2_scheme)) -> JSONResponse:
    """Find workers by name or identification."""
    # Validations
    token = decode_access_token(token)
    allowed_roles(token["roles"], ["read_workers", "admin"])
    # Find workers
    user = user_services.get_by_email(token["email"])
    company = companies_services.get_company(user["company"])
    company_db = db_client[company["db"]]
    result = workers_services(company_db).get_workers_by_name_or_identification(
        user["company"], search, limit, skip, user["workers"])
    result = worker_entity_list(result)
    # Return
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)

@workers.post(
    path="/array",
    summary="Find workers by an array of ids",
    description="This endpoint finds workers by an array of ids",
    status_code=200)
async def get_workers_by_an_array(
    data: GetByIds,
    token: str = Depends(oauth2_scheme)) -> JSONResponse:
    """Find workers by an array of ids."""
    # Validations
    token = decode_access_token(token)
    allowed_roles(token["roles"], ["read_workers", "admin"])
    # Find workers
    user = user_services.get_by_email(token["email"])
    company = companies_services.get_company(user["company"])
    company_db = db_client[company["db"]]
    result = workers_services(company_db).get_workers_by_an_array(user["company"], data.ids)
    result = worker_entity_list(result)
    # Return
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)

@workers.put(
    path="/{worker_id}",
    summary="Update a worker",
    description="This endpoint updates a worker", status_code=200)
async def update_worker(
    worker_id: str,
    worker: UpdateWorker,
    token: str = Depends(oauth2_scheme)) -> JSONResponse:
    """Update a worker."""
    # Validations
    token = decode_access_token(token)
    allowed_roles(token["roles"], ["handle_workers", "admin"])
    # Encode worker
    worker = jsonable_encoder(worker)
    # Update worker
    user = user_services.get_by_email(token["email"])
    company = companies_services.get_company(user["company"])
    company_db = db_client[company["db"]]
    result = workers_services(company_db).update_worker(
        user["company"], worker_id, worker, user_entity(user))
    result = worker_entity(result)
    # Websocket
    message = WebsocketResponse(
        event="worker_updated",
        data=result,
        userName=user["userName"],
        company=user["company"])
    await manager.broadcast(message)
    # Log
    _ = logs_services(company_db).create_log({
        "company": user["company"],
        "user": user["email"],
        "userName": user["userName"],
        "type": "Personal",
        "message": f"El usuario {user['userName']} ha actualizado a la persona {result['name']}"
    })
    # Return
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)

@workers.delete(
    path="/{worker_id}",
    summary="Delete a worker",
    description="This endpoint deletes a worker",
    status_code=200)
async def delete_worker(worker_id: str, token: str = Depends(oauth2_scheme)) -> JSONResponse:
    """Delete a worker."""
    # Validations
    token = decode_access_token(token)
    allowed_roles(token["roles"], ["handle_workers", "admin"])
    # Delete worker
    user = user_services.get_by_email(token["email"])
    company = companies_services.get_company(user["company"])
    company_db = db_client[company["db"]]
    result = workers_services(company_db).delete_worker(user["company"], worker_id, user["workers"])
    result = worker_entity(result)
    # Websocket
    message = WebsocketResponse(
        event="worker_deleted",
        data=result,
        userName=user["userName"],
        company=user["company"])
    await manager.broadcast(message)
    # Log
    _ = logs_services(company_db).create_log({
        "company": user["company"],
        "user": user["email"],
        "userName": user["userName"],
        "type": "Personal",
        "message": f"El usuario {user['userName']} ha eliminado a la persona {result['name']}"
    })
    # Return
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)
