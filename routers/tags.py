from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from db.client import db_client
from services.users import UsersServices
from services.tags import TagsServices
from services.websocket import manager
from models.company import Tag
from models.websocket import WebsocketResponse
from schemas.company import CompanyEntity
from utils.auth import decodeAccessToken
from utils.roles import required_roles

tags = APIRouter(prefix="/tags", tags=["Tags"], responses={404: {"description": "Not found"}})
db = db_client["harmony"]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# add a tag
@tags.post(path="/", summary="Add a tag", description="Add a tag to a company", status_code=status.HTTP_201_CREATED)
async def addTag(tag: Tag, token: str = Depends(oauth2_scheme)) -> JSONResponse:
    # Validations
    token = decodeAccessToken(token)
    required_roles(token["roles"], ["admin"])
    # Add tag
    user = UsersServices(db).getByEmail(token["email"])
    result = TagsServices(db).addTag(user["company"], tag)
    result = CompanyEntity(result)
    # Websocket
    message = WebsocketResponse(event="company_updated", data=result, userName=user["userName"], company=user["company"])
    await manager.broadcast(message)
    # Return
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=result)

# update a tag
@tags.put(path="/{tagId}", summary="Update a tag", description="Update a tag from a company", status_code=status.HTTP_200_OK)
async def updateTag(tagId: str, tag: Tag, token: str = Depends(oauth2_scheme)) -> JSONResponse:
    # Validations
    token = decodeAccessToken(token)
    required_roles(token["roles"], ["admin"])
    # Update tag
    user = UsersServices(db).getByEmail(token["email"])
    result = TagsServices(db).updateTag(user["company"], tagId, tag)
    result = CompanyEntity(result)
    # Websocket
    message = WebsocketResponse(event="company_updated", data=result, userName=user["userName"], company=user["company"])
    await manager.broadcast(message)
    # Return
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)

# delete a tag
@tags.delete(path="/{tagId}", summary="Delete a tag", description="Delete a tag from a company", status_code=status.HTTP_200_OK)
async def deleteTag(tagId: str, token: str = Depends(oauth2_scheme)) -> JSONResponse:
    # Validations
    token = decodeAccessToken(token)
    required_roles(token["roles"], ["admin"])
    # Delete tag
    user = UsersServices(db).getByEmail(token["email"])
    result = TagsServices(db).deleteTag(user["company"], tagId)
    result = CompanyEntity(result)
    # Websocket
    message = WebsocketResponse(event="company_updated", data=result, userName=user["userName"], company=user["company"])
    await manager.broadcast(message)
    # Return
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)