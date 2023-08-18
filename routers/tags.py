from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from db.client import db_client
from models.company import Tag
from utils.auth import decodeAccessToken
from utils.roles import validateRoles
from utils.errorsResponses import errors
from services.users import UsersServices
from services.tags import TagsServices
from services.websocket import manager
from models.websocket import WebsocketResponse

tags = APIRouter(prefix="/tags", tags=["Tags"], responses={404: {"description": "Not found"}})
db = db_client["harmony"]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# add a tag
@tags.post(path="/", summary="Add a tag", description="Add a tag to a company", status_code=status.HTTP_201_CREATED)
async def addTag(tag: Tag, token: str = Depends(oauth2_scheme)):
    token = decodeAccessToken(token)
    if token == False:
        raise errors["Token expired"]
    if not validateRoles(token["roles"], ["admin"], []):
        raise errors["Unauthorized"]
    user = UsersServices(db).getByEmail(token["email"])
    result = TagsServices(db).addTag(user["company"], tag)
    message = WebsocketResponse(event="company_updated", data=result, userName=user["userName"], company=user["company"])
    await manager.broadcast(message)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=result)

# update a tag
@tags.put(path="/{tagId}", summary="Update a tag", description="Update a tag from a company", status_code=status.HTTP_200_OK)
async def updateTag(tagId: str, tag: Tag, token: str = Depends(oauth2_scheme)):
    token = decodeAccessToken(token)
    if token == False:
        raise errors["Token expired"]
    if not validateRoles(token["roles"], ["admin"], []):
        raise errors["Unauthorized"]
    user = UsersServices(db).getByEmail(token["email"])
    result = TagsServices(db).updateTag(user["company"], tagId, tag)
    message = WebsocketResponse(event="company_updated", data=result, userName=user["userName"], company=user["company"])
    await manager.broadcast(message)
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)

# delete a tag
@tags.delete(path="/{tagId}", summary="Delete a tag", description="Delete a tag from a company", status_code=status.HTTP_200_OK)
async def deleteTag(tagId: str, token: str = Depends(oauth2_scheme)):
    token = decodeAccessToken(token)
    if token == False:
        raise errors["Token expired"]
    if not validateRoles(token["roles"], ["admin"], []):
        raise errors["Unauthorized"]
    user = UsersServices(db).getByEmail(token["email"])
    result = TagsServices(db).deleteTag(user["company"], tagId)
    message = WebsocketResponse(event="company_updated", data=result, userName=user["userName"], company=user["company"])
    await manager.broadcast(message)
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)