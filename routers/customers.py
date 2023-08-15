from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from db.client import db_client
from models.customer import Customer, UpdateCustomer
from utils.auth import decodeAccessToken, validateRoles
from services.users import UsersServices
from services.companies import CompaniesServices
from services.customers import CustomersServices
from services.websocket import manager
from models.websocket import WebsocketResponse

customers = APIRouter(prefix='/customers', tags=['Customers'], responses={404: {"description": "Not found"}})
harmony = db_client["harmony"]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# create a customer
@customers.post(path="/", summary="Create a customer", description="This endpoint creates a customer in the database and returns the customer object.", status_code=201)
async def createCustomer(customer: Customer, token: str = Depends(oauth2_scheme)):
    token = decodeAccessToken(token)
    if token == False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired.")
    if not validateRoles(token["roles"], ["handle_customer"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    user = UsersServices(harmony).getByEmail(token["email"])
    company = CompaniesServices(harmony).findCompany(user["company"])
    companyDb = db_client[company["db"]]
    result = CustomersServices(companyDb).createCustomer(user["company"], customer, user)
    if result:
        message = WebsocketResponse(event="customer_created", data=result, userName=user["userName"], company=user["company"])
        await manager.broadcast(message)
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=result)
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error creating customer.")

@customers.get(path="/", summary="Find all customers", description="This endpoint returns all customers in the database.", status_code=200)
async def findAllCustomers(token: str = Depends(oauth2_scheme)):
    token = decodeAccessToken(token)
    if token == False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired.")
    if not validateRoles(token["roles"], ["read_customer"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    user = UsersServices(harmony).getByEmail(token["email"])
    company = CompaniesServices(harmony).findCompany(user["company"])
    companyDb = db_client[company["db"]]
    customers = CustomersServices(companyDb).findAllCustomers(user["company"], user["customers"])
    if customers:
        return customers
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No customers found.")

@customers.put(path="/{id}", summary="Update a customer", description="This endpoint updates a customer in the database and returns the customer object.", status_code=200)
async def updateCustomer(id: str, data: UpdateCustomer, token: str = Depends(oauth2_scheme)):
    token = decodeAccessToken(token)
    if token == False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired.")
    if not validateRoles(token["roles"], ["handle_customer"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    user = UsersServices(harmony).getByEmail(token["email"])
    company = CompaniesServices(harmony).findCompany(user["company"])
    companyDb = db_client[company["db"]]
    result = CustomersServices(companyDb).updateCustomer(user["company"], id, data, user)
    if result:
        message = WebsocketResponse(event="customer_updated", data=result, userName=user["userName"], company=user["company"])
        await manager.broadcast(message)
        return result
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found.")

@customers.delete(path="/{id}", summary="Delete a customer", description="This endpoint deletes a customer in the database and returns the customer object.", status_code=200)
async def deleteCustomer(id: str, token: str = Depends(oauth2_scheme)):
    token = decodeAccessToken(token)
    if token == False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired.")
    if not validateRoles(token["roles"], ["handle_customer"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    user = UsersServices(harmony).getByEmail(token["email"])
    company = CompaniesServices(harmony).findCompany(user["company"])
    companyDb = db_client[company["db"]]
    result = CustomersServices(companyDb).deleteCustomer(user["company"], id, user["customers"])
    if result:
        message = WebsocketResponse(event="customer_deleted", data=result, userName=user["userName"], company=user["company"])
        await manager.broadcast(message)
        return result
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found.")
