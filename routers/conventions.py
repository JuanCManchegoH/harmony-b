from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from db.client import db_client
from services.users import UsersServices
from services.conventions import ConventionsServices
from services.websocket import manager
from models.company import Convention
from models.websocket import WebsocketResponse
from schemas.company import CompanyEntity
from utils.auth import decodeAccessToken
from utils.roles import required_roles

conventions = APIRouter(prefix="/conventions", tags=["Conventions"], responses={404: {"description": "Not found"}})
db = db_client["harmony"]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# add a convention
@conventions.post(path="/", summary="Add a convention", description="Add a convention to a company", status_code=status.HTTP_201_CREATED)
async def addConvention(convention: Convention, token: str = Depends(oauth2_scheme)) -> JSONResponse:
    # Validations
    token = decodeAccessToken(token)
    required_roles(token["roles"], ["admin"])
    # Add convention
    user = UsersServices(db).getByEmail(token["email"])
    result = ConventionsServices(db).addConvention(user["company"], convention)
    result = CompanyEntity(result)
    # Websocket
    message = WebsocketResponse(event="company_updated", data=result, userName=user["userName"], company=user["company"])
    await manager.broadcast(message)
    # Return
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=result)

# update a convention
@conventions.put(path="/{conventionId}", summary="Update a convention", description="Update a convention from a company", status_code=status.HTTP_200_OK)
async def updateConvention(conventionId: str, convention: Convention, token: str = Depends(oauth2_scheme)) -> JSONResponse:
    # Validations
    token = decodeAccessToken(token)
    required_roles(token["roles"], ["admin"])
    # Update convention
    user = UsersServices(db).getByEmail(token["email"])
    result = ConventionsServices(db).updateConvention(user["company"], conventionId, convention)
    result = CompanyEntity(result)
    # Websocket
    message = WebsocketResponse(event="company_updated", data=result, userName=user["userName"], company=user["company"])
    await manager.broadcast(message)
    # Return
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)

# delete a convention
@conventions.delete(path="/{conventionId}", summary="Delete a convention", description="Delete a convention from a company", status_code=status.HTTP_200_OK)
async def deleteConvention(conventionId: str, token: str = Depends(oauth2_scheme)) -> JSONResponse:
    # Validations
    token = decodeAccessToken(token) 
    required_roles(token["roles"], ["admin"])
    # Delete convention
    user = UsersServices(db).getByEmail(token["email"])
    result = ConventionsServices(db).deleteConvention(user["company"], conventionId)
    result = CompanyEntity(result)
    # Websocket
    message = WebsocketResponse(event="company_updated", data=result, userName=user["userName"], company=user["company"])
    await manager.broadcast(message)
    # Return
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)