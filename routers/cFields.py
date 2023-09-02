from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from db.client import db_client
from services.users import UsersServices
from services.cFields import CFieldsServices
from services.websocket import manager
from models.company import Field
from models.websocket import WebsocketResponse
from schemas.company import CompanyEntity
from utils.auth import decodeAccessToken
from utils.roles import required_roles

cfields = APIRouter(prefix="/cfields", tags=["CFields"], responses={404: {"description": "Not found"}})
db = db_client["harmony"]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# add a customer field
@cfields.post(path="/", summary="Add a customer field", description="Add a customer field to a company", status_code=status.HTTP_201_CREATED)
async def addCField(field: Field, token: str = Depends(oauth2_scheme)) -> JSONResponse:
    # Validations
    token = decodeAccessToken(token)
    required_roles(token["roles"], ["admin"])
    # Add customer field
    user = UsersServices(db).getByEmail(token["email"])
    result = CFieldsServices(db).addCField(user["company"], field)
    result = CompanyEntity(result)
    # Websocket
    message = WebsocketResponse(event="company_updated", data=result, userName=user["userName"], company=user["company"])
    await manager.broadcast(message)
    # Return
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=result)

# update a customer field
@cfields.put(path="/{fieldId}", summary="Update a customer field", description="Update a customer field from a company", status_code=status.HTTP_200_OK)
async def updateCField(fieldId: str, field: Field, token: str = Depends(oauth2_scheme)) -> JSONResponse:
    # Validations
    token = decodeAccessToken(token)
    required_roles(token["roles"], ["admin"])
    # Update customer field
    user = UsersServices(db).getByEmail(token["email"])
    result = CFieldsServices(db).updateCField(user["company"], fieldId, field)
    result = CompanyEntity(result)
    # Websocket
    message = WebsocketResponse(event="company_updated", data=result, userName=user["userName"], company=user["company"])
    await manager.broadcast(message)
    # Return
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)

# delete a customer field
@cfields.delete(path="/{fieldId}", summary="Delete a customer field", description="Delete a customer field from a company", status_code=status.HTTP_200_OK)
async def deleteCField(fieldId: str, token: str = Depends(oauth2_scheme)) -> JSONResponse:
    # Validations
    token = decodeAccessToken(token)
    required_roles(token["roles"], ["admin"])
    # Delete customer field
    user = UsersServices(db).getByEmail(token["email"])
    result = CFieldsServices(db).deleteCField(user["company"], fieldId)
    result = CompanyEntity(result)
    # Websocket
    message = WebsocketResponse(event="company_updated", data=result, userName=user["userName"], company=user["company"])
    await manager.broadcast(message)
    # Return
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)