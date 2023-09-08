from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from db.client import db_client
from services.companies import CompaniesServices
from services.users import UsersServices
from services.sequences import SequencesServices
from services.websocket import manager
from services.logs import LogsServices
from models.company import Sequence
from models.websocket import WebsocketResponse
from schemas.company import CompanyEntity
from utils.auth import decodeAccessToken
from utils.roles import required_roles

sequences = APIRouter(prefix="/sequences", tags=["Sequences"], responses={404: {"description": "Not found"}})
db = db_client["harmony"]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# add a sequence
@sequences.post(path="", summary="Add a sequence", description="Add a sequence to a company", status_code=status.HTTP_201_CREATED)
async def addSequence(sequence: Sequence, token: str = Depends(oauth2_scheme)) -> JSONResponse:
    # Validations
    token = decodeAccessToken(token)
    required_roles(token["roles"], ["admin"])
    # Add sequence
    user = UsersServices(db).getByEmail(token["email"])
    result = SequencesServices(db).addSequence(user["company"], sequence)
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
        "type": "Secuencias",
        "message": f"El usuario {user['userName']} ha creado una secuencia"
    })
    # Return
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=result)

# update a sequence
@sequences.put(path="/{sequenceId}", summary="Update a sequence", description="Update a sequence from a company", status_code=status.HTTP_200_OK)
async def updateSequence(sequenceId: str, sequence: Sequence, token: str = Depends(oauth2_scheme)) -> JSONResponse:
    # Validations
    token = decodeAccessToken(token)
    required_roles(token["roles"], ["admin"])
    # Update sequence
    user = UsersServices(db).getByEmail(token["email"])
    result = SequencesServices(db).updateSequence(user["company"], sequenceId, sequence)
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
        "type": "Secuencias",
        "message": f"El usuario {user['userName']} ha actualizado una secuencia"
    })
    # Return
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)

# delete a sequence
@sequences.delete(path="/{sequenceId}", summary="Delete a sequence", description="Delete a sequence from a company", status_code=status.HTTP_200_OK)
async def deleteSequence(sequenceId: str, token: str = Depends(oauth2_scheme)) -> JSONResponse:
    # Validations
    token = decodeAccessToken(token)
    required_roles(token["roles"], ["admin"])
    # Delete sequence
    user = UsersServices(db).getByEmail(token["email"])
    result = SequencesServices(db).deleteSequence(user["company"], sequenceId)
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
        "type": "Secuencias",
        "message": f"El usuario {user['userName']} ha eliminado una secuencia"
    })
    # Return
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)