from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from db.client import db_client
from services.users import UsersServices
from services.companies import CompaniesServices
from services.workers import WorkersServices
from services.websocket import manager
from models.worker import Worker, UpdateWorker
from models.websocket import WebsocketResponse
from schemas.worker import WorkerEntity, WorkerEntityList
from schemas.user import UserEntity
from utils.auth import decodeAccessToken
from utils.roles import allowed_roles

workers = APIRouter(prefix='/workers', tags=['Workers'], responses={404: {"description": "Not found"}})
harmony = db_client["harmony"]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# create a worker
@workers.post(path="", summary="Create a worker", description="This endpoint creates a worker in the database and returns the worker object.", status_code=201)
async def createWorker(worker: Worker, token: str = Depends(oauth2_scheme)) -> JSONResponse:
    # Validations
    token = decodeAccessToken(token)
    allowed_roles(token["roles"], ["handle_workers", "admin"])
    # Create worker
    user = UsersServices(harmony).getByEmail(token["email"])
    company = CompaniesServices(harmony).getCompany(user["company"])
    companyDb = db_client[company["db"]]
    result = WorkersServices(companyDb).createWorker(user["company"], worker, UserEntity(user))
    result = WorkerEntity(result)
    # Websocket
    message = WebsocketResponse(event="worker_created", data=result, userName=user["userName"], company=user["company"])
    await manager.broadcast(message)
    # Return
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=result)

# find workers by name or identification, limit and offset
@workers.get(path="/{search}/{limit}/{skip}", summary="Find workers by name or identification", description="This endpoint finds workers by name or identification in the database and returns the workers object.", status_code=200)
async def findWorkers(search: str, limit: int, skip: int, token: str = Depends(oauth2_scheme)) -> JSONResponse:
    # Validations
    token = decodeAccessToken(token)
    allowed_roles(token["roles"], ["read_workers", "admin"])
    # Find workers
    user = UsersServices(harmony).getByEmail(token["email"])
    company = CompaniesServices(harmony).getCompany(user["company"])
    companyDb = db_client[company["db"]]
    result = WorkersServices(companyDb).findWorkersByNameOrIdentification(user["company"], search, limit, skip, user["workers"])
    result = WorkerEntityList(result)
    # Return
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)

# Update a worker
@workers.put(path="/{id}", summary="Update a worker", description="This endpoint updates a worker in the database and returns the worker object.", status_code=200)
async def updateWorker(id: str, worker: UpdateWorker, token: str = Depends(oauth2_scheme)) -> JSONResponse:
    # Validations
    token = decodeAccessToken(token)
    allowed_roles(token["roles"], ["handle_workers", "admin"])
    # Update worker
    user = UsersServices(harmony).getByEmail(token["email"])
    company = CompaniesServices(harmony).getCompany(user["company"])
    companyDb = db_client[company["db"]]
    result = WorkersServices(companyDb).updateWorker(user["company"], id, worker, UserEntity(user))
    result = WorkerEntity(result)
    # Websocket
    message = WebsocketResponse(event="worker_updated", data=result, userName=user["userName"], company=user["company"])
    await manager.broadcast(message)
    # Return
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)

# Delete a worker
@workers.delete(path="/{id}", summary="Delete a worker", description="This endpoint deletes a worker in the database and returns the worker object.", status_code=200)
async def deleteWorker(id: str, token: str = Depends(oauth2_scheme)) -> JSONResponse:
    # Validations
    token = decodeAccessToken(token)
    allowed_roles(token["roles"], ["handle_workers", "admin"])
    # Delete worker
    user = UsersServices(harmony).getByEmail(token["email"])
    company = CompaniesServices(harmony).getCompany(user["company"])
    companyDb = db_client[company["db"]]
    result = WorkersServices(companyDb).deleteWorker(user["company"], id, user["workers"])
    result = WorkerEntity(result)
    # Websocket
    message = WebsocketResponse(event="worker_deleted", data=result, userName=user["userName"], company=user["company"])
    await manager.broadcast(message)
    # Return
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)