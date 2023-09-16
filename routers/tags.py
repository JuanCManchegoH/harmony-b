"""Tags routers module."""

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pymongo.database import Database
from db.client import db_client
from services.companies import CompaniesServices
from services.users import UsersServices
from services.tags import TagsServices
from services.websocket import manager
from services.logs import LogsServices
from models.company import Tag
from models.websocket import WebsocketResponse
from schemas.company import company_entity
from utils.auth import decode_access_token
from utils.roles import required_roles

tags = APIRouter(
    prefix="/tags",
    tags=["Tags"],
    responses={404: {"description": "Not found"}})
database = db_client["harmony"]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
companies_services = CompaniesServices(database)
tags_services = TagsServices(database)
users_services = UsersServices(database)
def logs_services(company_db: Database):
    """Logs services."""
    return LogsServices(company_db)

# add a tag
@tags.post(
    path="",
    summary="Add a tag",
    description="Add a tag to a company",
    status_code=status.HTTP_201_CREATED)
async def add_tag(tag: Tag, token: str = Depends(oauth2_scheme)) -> JSONResponse:
    """Add a tag."""
    # Validations
    token = decode_access_token(token)
    required_roles(token["roles"], ["admin"])
    # encode tag
    tag = jsonable_encoder(tag)
    # Add tag
    user = users_services.get_by_email(token["email"])
    result = tags_services.add_tag(user["company"], tag)
    result = company_entity(result)
    # Websocket
    message = WebsocketResponse(
        event="company_updated",
        data=result,
        userName=user["userName"],
        company=user["company"])
    await manager.broadcast(message)
    # Log
    company = companies_services.get_company(user["company"])
    company_db = db_client[company["db"]]
    _ = logs_services(company_db).create_log({
        "company": user["company"],
        "user": user["email"],
        "userName": user["userName"],
        "type": "Etiquetas",
        "message": f"El usuario {user['userName']} ha creado una etiqueta"
    })
    # Return
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=result)

# update a tag
@tags.put(
    path="/{tag_id}",
    summary="Update a tag",
    description="Update a tag from a company",
    status_code=status.HTTP_200_OK)
async def update_tag(tag_id: str, tag: Tag, token: str = Depends(oauth2_scheme)) -> JSONResponse:
    """Update a tag."""
    # Validations
    token = decode_access_token(token)
    required_roles(token["roles"], ["admin"])
    # encode tag
    tag = jsonable_encoder(tag)
    # Update tag
    user = users_services.get_by_email(token["email"])
    result = tags_services.update_tag(user["company"], tag_id, tag)
    result = company_entity(result)
    # Websocket
    message = WebsocketResponse(
        event="company_updated", data=result,
        userName=user["userName"],
        company=user["company"])
    await manager.broadcast(message)
    # Log
    company = companies_services.get_company(user["company"])
    company_db = db_client[company["db"]]
    _ = logs_services(company_db).create_log({
        "company": user["company"],
        "user": user["email"],
        "userName": user["userName"],
        "type": "Etiquetas",
        "message": f"El usuario {user['userName']} ha actualizado una etiqueta"
    })
    # Return
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)

# delete a tag
@tags.delete(
    path="/{tag_id}",
    summary="Delete a tag",
    description="Delete a tag from a company",
    status_code=status.HTTP_200_OK)
async def delete_tag(tag_id: str, token: str = Depends(oauth2_scheme)) -> JSONResponse:
    """Delete a tag."""
    # Validations
    token = decode_access_token(token)
    required_roles(token["roles"], ["admin"])
    # Delete tag
    user = users_services.get_by_email(token["email"])
    result = tags_services.delete_tag(user["company"], tag_id)
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
        "type": "Etiquetas",
        "message": f"El usuario {user['userName']} ha eliminado una etiqueta"
    })
    # Return
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)
