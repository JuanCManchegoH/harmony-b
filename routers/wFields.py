from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from db.client import db_client
from services.companies import CompaniesServices
from services.users import UsersServices
from services.wFields import WFieldsServices
from services.websocket import manager
from services.logs import LogsServices
from models.company import Field
from models.websocket import WebsocketResponse
from schemas.company import CompanyEntity
from utils.auth import decodeAccessToken
from utils.roles import required_roles

wfields = APIRouter(prefix="/wfields", tags=["WFields"], responses={404: {"description": "Not found"}})
db = db_client["harmony"]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# add a worker field
@wfields.post(path="", summary="Add a worker field", description="Add a worker field to a company", status_code=status.HTTP_201_CREATED)
async def addWField(field: Field, token: str = Depends(oauth2_scheme)) -> JSONResponse:
    # Validations
    token = decodeAccessToken(token)
    required_roles(token["roles"], ["admin"])
    # Add worker field
    user = UsersServices(db).getByEmail(token["email"])
    result = WFieldsServices(db).addWField(user["company"], field)
    result = CompanyEntity(result)
    # Websocket
    message = WebsocketResponse(event="company_updated", data=result, userName=user["userName"], company=user["company"])
    await manager.broadcast(message)
    # Log
    company = CompaniesServices(db).getCompany(user["company"])
    companyDb = db_client[company["db"]]
    _ = LogsServices(companyDb).createLog({
        "company": user["company"],
        "user": user["email"],
        "userName": user["userName"],
        "type": "Campos de personal",
        "message": f"El usuario {user['userName']} ha creado un campo de personal"
    })
    # Return
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=result)

# update a worker field
@wfields.put(path="/{fieldId}", summary="Update a worker field", description="Update a worker field from a company", status_code=status.HTTP_200_OK)
async def updateWField(fieldId: str, field: Field, token: str = Depends(oauth2_scheme)) -> JSONResponse:
    # Validations
    token = decodeAccessToken(token)
    required_roles(token["roles"], ["admin"])
    # Update worker field
    user = UsersServices(db).getByEmail(token["email"])
    result = WFieldsServices(db).updateWField(user["company"], fieldId, field)
    result = CompanyEntity(result)
    # Websocket
    message = WebsocketResponse(event="company_updated", data=result, userName=user["userName"], company=user["company"])
    await manager.broadcast(message)
    # Log
    company = CompaniesServices(db).getCompany(user["company"])
    companyDb = db_client[company["db"]]
    _ = LogsServices(companyDb).createLog({
        "company": user["company"],
        "user": user["email"],
        "userName": user["userName"],
        "type": "Campos de personal",
        "message": f"El usuario {user['userName']} ha actualizado un campo de personal"
    })
    # Return
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)

# delete a worker field
@wfields.delete(path="/{fieldId}", summary="Delete a worker field", description="Delete a worker field from a company", status_code=status.HTTP_200_OK)
async def deleteWField(fieldId: str, token: str = Depends(oauth2_scheme)) -> JSONResponse:
    # Validations
    token = decodeAccessToken(token)
    required_roles(token["roles"], ["admin"])
    # Delete worker field
    user = UsersServices(db).getByEmail(token["email"])
    result = WFieldsServices(db).deleteWField(user["company"], fieldId)
    result = CompanyEntity(result)
    # Websocket
    message = WebsocketResponse(event="company_updated", data=result, userName=user["userName"], company=user["company"])
    await manager.broadcast(message)
    # Log
    company = CompaniesServices(db).getCompany(user["company"])
    companyDb = db_client[company["db"]]
    _ = LogsServices(companyDb).createLog({
        "company": user["company"],
        "user": user["email"],
        "userName": user["userName"],
        "type": "Campos de personal",
        "message": f"El usuario {user['userName']} ha eliminado un campo de personal"
    })
    # Return
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)