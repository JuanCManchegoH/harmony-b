from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from db.client import db_client
from models.company import Field
from utils.auth import decodeAccessToken
from utils.errorsResponses import errors
from utils.roles import validateRoles
from services.users import UsersServices
from services.wFields import WFieldsServices
from services.websocket import manager
from models.websocket import WebsocketResponse


wfields = APIRouter(prefix="/wfields", tags=["WFields"], responses={404: {"description": "Not found"}})
db = db_client["harmony"]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# add a worker field
@wfields.post(path="/", summary="Add a worker field", description="Add a worker field to a company", status_code=status.HTTP_201_CREATED)
async def addWField(field: Field, token: str = Depends(oauth2_scheme)):
    token = decodeAccessToken(token)
    if token == False:
        raise errors["Token expired"]
    if not validateRoles(token["roles"], ["admin"], []):
        raise errors["Unauthorized"]
    user = UsersServices(db).getByEmail(token["email"])
    result = WFieldsServices(db).addWField(user["company"], field)
    message = WebsocketResponse(event="company_updated", data=result, userName=user["userName"], company=user["company"])
    await manager.broadcast(message)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=result)

# update a worker field
@wfields.put(path="/{fieldId}", summary="Update a worker field", description="Update a worker field from a company", status_code=status.HTTP_200_OK)
async def updateWField(fieldId: str, field: Field, token: str = Depends(oauth2_scheme)):
    token = decodeAccessToken(token)
    if token == False:
        raise errors["Token expired"]
    if not validateRoles(token["roles"], ["admin"], []):
        raise errors["Unauthorized"]
    user = UsersServices(db).getByEmail(token["email"])
    result = WFieldsServices(db).updateWField(user["company"], fieldId, field)
    message = WebsocketResponse(event="company_updated", data=result, userName=user["userName"], company=user["company"])
    await manager.broadcast(message)
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)

# delete a worker field
@wfields.delete(path="/{fieldId}", summary="Delete a worker field", description="Delete a worker field from a company", status_code=status.HTTP_200_OK)
async def deleteWField(fieldId: str, token: str = Depends(oauth2_scheme)):
    token = decodeAccessToken(token)
    if token == False:
        raise errors["Token expired"]
    if not validateRoles(token["roles"], ["admin"], []):
        raise errors["Unauthorized"]
    user = UsersServices(db).getByEmail(token["email"])
    result = WFieldsServices(db).deleteWField(user["company"], fieldId)
    message = WebsocketResponse(event="company_updated", data=result, userName=user["userName"], company=user["company"])
    await manager.broadcast(message)
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)