from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from db.client import db_client
from services.users import UsersServices
from services.companies import CompaniesServices
from services.customers import CustomersServices
from services.websocket import manager
from models.customer import Customer, UpdateCustomer
from models.websocket import WebsocketResponse
from schemas.customer import CustomerEntity, CustomerEntityList
from schemas.user import UserEntity
from utils.auth import decodeAccessToken
from utils.roles import allowed_roles

customers = APIRouter(prefix='/customers', tags=['Customers'], responses={404: {"description": "Not found"}})
harmony = db_client["harmony"]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# create a customer
@customers.post(path="/", summary="Create a customer", description="This endpoint creates a customer in the database and returns the customer object.", status_code=201)
async def createCustomer(customer: Customer, token: str = Depends(oauth2_scheme)) -> JSONResponse:
    # Validations
    token = decodeAccessToken(token)
    allowed_roles(token["roles"], ["handle_customers", "admin"])
    # Create customer
    user = UsersServices(harmony).getByEmail(token["email"])
    company = CompaniesServices(harmony).getCompany(user["company"])
    companyDb = db_client[company["db"]]
    result = CustomersServices(companyDb).createCustomer(user["company"], customer, UserEntity(user))
    result = CustomerEntity(result)
    # Websocket
    message = WebsocketResponse(event="customer_created", data=result, userName=user["userName"], company=user["company"])
    await manager.broadcast(message)
    # Return
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=result)

@customers.get(path="/", summary="Find all customers", description="This endpoint returns all customers", status_code=200)
async def findAllCustomers(token: str = Depends(oauth2_scheme)) -> JSONResponse:
    # Validations
    token = decodeAccessToken(token)
    allowed_roles(token["roles"], ["read_customers", "admin"])
    # Find all customers
    user = UsersServices(harmony).getByEmail(token["email"])
    company = CompaniesServices(harmony).getCompany(user["company"])
    companyDb = db_client[company["db"]]
    result = CustomersServices(companyDb).findAllCustomers(user["company"], user["customers"])
    result = CustomerEntityList(result)
    # Return
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)

@customers.put(path="/{id}", summary="Update a customer", description="This endpoint updates a customer in the database and returns the customer object.", status_code=200)
async def updateCustomer(id: str, data: UpdateCustomer, token: str = Depends(oauth2_scheme)) -> JSONResponse:
    # Validations
    token = decodeAccessToken(token)
    allowed_roles(token["roles"], ["handle_customers", "admin"])
    # Update customer
    user = UsersServices(harmony).getByEmail(token["email"])
    company = CompaniesServices(harmony).getCompany(user["company"])
    companyDb = db_client[company["db"]]
    result = CustomersServices(companyDb).updateCustomer(user["company"], id, data, UserEntity(user))
    result = CustomerEntity(result)
    # Websocket
    message = WebsocketResponse(event="customer_updated", data=result, userName=user["userName"], company=user["company"])
    await manager.broadcast(message)
    # Return
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)

@customers.delete(path="/{id}", summary="Delete a customer", description="This endpoint deletes a customer in the database and returns the customer object.", status_code=200)
async def deleteCustomer(id: str, token: str = Depends(oauth2_scheme)) -> JSONResponse:
    # Validations
    token = decodeAccessToken(token)
    allowed_roles(token["roles"], ["handle_customers", "admin"])
    # Delete customer
    user = UsersServices(harmony).getByEmail(token["email"])
    company = CompaniesServices(harmony).getCompany(user["company"])
    companyDb = db_client[company["db"]]
    result = CustomersServices(companyDb).deleteCustomer(user["company"], id, user["customers"])
    result = CustomerEntity(result)
    # Websocket
    message = WebsocketResponse(event="customer_deleted", data=result, userName=user["userName"], company=user["company"])
    await manager.broadcast(message)
    # Return
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)
