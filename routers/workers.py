from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from db.client import db_client
from models.worker import Worker, UpdateWorker
from utils.auth import decodeAccessToken, validateRoles
from services.users import UsersServices
from services.companies import CompaniesServices
from services.workers import WorkersServices
from services.websocket import manager
from models.websocket import WebsocketResponse

workers = APIRouter(prefix='/workers', tags=['Workers'], responses={404: {"description": "Not found"}})
harmony = db_client["harmony"]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# create a worker
@workers.post(path="/", summary="Create a worker", description="This endpoint creates a worker in the database and returns the worker object.", status_code=201)
async def createWorker(worker: Worker, token: str = Depends(oauth2_scheme)):
    token = decodeAccessToken(token)
    if token == False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired.")
    if not validateRoles(token["roles"], ["handle_worker"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    user = UsersServices(harmony).getByEmail(token["email"])
    company = CompaniesServices(harmony).findCompany(user["company"])
    companyDb = db_client[company["db"]]
    result = WorkersServices(companyDb).createWorker(user["company"], worker, user)
    if result:
        message = WebsocketResponse(event="worker_created", data=result, userName=user["userName"], company=user["company"])
        await manager.broadcast(message)
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=result)
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error creating worker.")

# find workers by name or identification, limit and offset
@workers.get(path="/{search}/{limit}/{skip}", summary="Find workers by name or identification", description="This endpoint finds workers by name or identification in the database and returns the workers object.", status_code=200)
async def findWorkers(search: str, limit: int, skip: int, token: str = Depends(oauth2_scheme)):
    token = decodeAccessToken(token)
    if token == False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired.")
    user = UsersServices(harmony).getByEmail(token["email"])
    company = CompaniesServices(harmony).findCompany(user["company"])
    companyDb = db_client[company["db"]]
    result = WorkersServices(companyDb).findWorkersByNameOrIdentification(user["company"], search, limit, skip)
    if result:
        return result
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workers not found.")

# Update a worker
@workers.put(path="/{id}", summary="Update a worker", description="This endpoint updates a worker in the database and returns the worker object.", status_code=200)
async def updateWorker(id: str, worker: UpdateWorker, token: str = Depends(oauth2_scheme)):
    token = decodeAccessToken(token)
    if token == False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired.")
    if not validateRoles(token["roles"], ["handle_worker"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    user = UsersServices(harmony).getByEmail(token["email"])
    company = CompaniesServices(harmony).findCompany(user["company"])
    companyDb = db_client[company["db"]]
    result = WorkersServices(companyDb).updateWorker(user["company"], id, worker, user)
    if result:
        message = WebsocketResponse(event="worker_updated", data=result, userName=user["userName"], company=user["company"])
        await manager.broadcast(message)
        return result
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Worker not found.")

# Delete a worker
@workers.delete(path="/{id}", summary="Delete a worker", description="This endpoint deletes a worker in the database and returns the worker object.", status_code=200)
async def deleteWorker(id: str, token: str = Depends(oauth2_scheme)):
    token = decodeAccessToken(token)
    if token == False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired.")
    if not validateRoles(token["roles"], ["handle_worker"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    user = UsersServices(harmony).getByEmail(token["email"])
    company = CompaniesServices(harmony).findCompany(user["company"])
    companyDb = db_client[company["db"]]
    result = WorkersServices(companyDb).deleteWorker(user["company"], id)
    if result:
        message = WebsocketResponse(event="worker_deleted", data=result, userName=user["userName"], company=user["company"])
        await manager.broadcast(message)
        return result
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Worker not found.")