"""Customers router module."""

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi.encoders import jsonable_encoder
from pymongo.database import Database
from db.client import db_client
from services.users import UsersServices
from services.companies import CompaniesServices
from services.customers import CustomersServices
from services.websocket import manager
from services.logs import LogsServices
from models.customer import Customer, UpdateCustomer
from models.websocket import WebsocketResponse
from schemas.customer import customer_entity, customer_entity_list
from schemas.user import user_entity
from utils.auth import decode_access_token
from utils.roles import allowed_roles

customers = APIRouter(
    prefix='/customers',
    tags=['Customers'],
    responses={404: {"description": "Not found"}})
database = db_client["harmony"]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
users_services = UsersServices(database)
companies_services = CompaniesServices(database)
def customers_services(company_db: Database):
    """Customers services."""
    return CustomersServices(company_db)
def logs_services(company_db: Database):
    """Logs services."""
    return LogsServices(company_db)

# create a customer
@customers.post(
    path="",
    summary="Create a customer",
    description="This endpoint creates a customer in the database and returns the customer object.",
    status_code=201)
async def create_customer(customer: Customer, token: str = Depends(oauth2_scheme)) -> JSONResponse:
    """Create a customer."""
    # Validations
    token = decode_access_token(token)
    allowed_roles(token["roles"], ["handle_customers", "admin"])
    # Encode customer
    customer = jsonable_encoder(customer)
    # Create customer
    user = users_services.get_by_email(token["email"])
    company = companies_services.get_company(user["company"])
    company_db = db_client[company["db"]]
    result = customers_services(company_db).create_customer(
        user["company"], customer, user_entity(user))
    result = customer_entity(result)
    # Websocket
    message = WebsocketResponse(
        event="customer_created",
        data=result,
        userName=user["userName"],
        company=user["company"])
    await manager.broadcast(message)
    # Log
    _ = logs_services(company_db).create_log({
        "company": user["company"],
        "user": user["email"],
        "userName": user["userName"],
        "type": "Clientes",
        "message": f"El usuario {user['userName']} ha creado al cliente {result['name']}"
    })
    # Return
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=result)

@customers.get(
    path="/",
    summary="Find all customers",
    description="This endpoint returns all customers",
    status_code=200)
async def get_all_customers(token: str = Depends(oauth2_scheme)) -> JSONResponse:
    """get all customers."""
    # Validations
    token = decode_access_token(token)
    allowed_roles(token["roles"], ["read_customers", "admin"])
    # Find all customers
    user = users_services.get_by_email(token["email"])
    company = companies_services.get_company(user["company"])
    company_db = db_client[company["db"]]
    result = customers_services(company_db).get_all_customers(user["company"], user["customers"])
    result = customer_entity_list(result)
    # Return
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)

@customers.put(
    path="/{customer_id}",
    summary="Update a customer",
    description="This endpoint updates a customer.",
    status_code=200)
async def update_customer(
    customer_id: str,
    data: UpdateCustomer,
    token: str = Depends(oauth2_scheme)) -> JSONResponse:
    """Update a customer."""
    # Validations
    token = decode_access_token(token)
    allowed_roles(token["roles"], ["handle_customers", "admin"])
    # Encode customer
    data = jsonable_encoder(data)
    # Update customer
    user = users_services.get_by_email(token["email"])
    company = companies_services.get_company(user["company"])
    company_db = db_client[company["db"]]
    result = customers_services(company_db).update_customer(
        user["company"],
        customer_id, data,
        user_entity(user))
    result = customer_entity(result)
    # Websocket
    message = WebsocketResponse(
        event="customer_updated",
        data=result,
        userName=user["userName"],
        company=user["company"])
    await manager.broadcast(message)
    # Log
    _ = logs_services(company_db).create_log({
        "company": user["company"],
        "user": user["email"],
        "userName": user["userName"],
        "type": "Clientes",
        "message": f"El usuario {user['userName']} ha actualizado al cliente {result['name']}"
    })
    # Return
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)

@customers.delete(
    path="/{customer_id}",
    summary="Delete a customer",
    description="This endpoint deletes a customer in the database and returns the customer object.",
    status_code=200)
async def delete_customer(customer_id: str, token: str = Depends(oauth2_scheme)) -> JSONResponse:
    """Delete a customer."""
    # Validations
    token = decode_access_token(token)
    allowed_roles(token["roles"], ["handle_customers", "admin"])
    # Delete customer
    user = users_services.get_by_email(token["email"])
    company = companies_services.get_company(user["company"])
    company_db = db_client[company["db"]]
    result = customers_services(company_db).delete_customer(
        user["company"],
        customer_id,
        user["customers"])
    result = customer_entity(result)
    # Websocket
    message = WebsocketResponse(
        event="customer_deleted",
        data=result,
        userName=user["userName"],
        company=user["company"])
    await manager.broadcast(message)
    # Log
    _ = LogsServices(company_db).create_log({
        "company": user["company"],
        "user": user["email"],
        "userName": user["userName"],
        "type": "Clientes",
        "message": f"El usuario {user['userName']} ha eliminado al cliente {result['name']}"
    })
    # Return
    return JSONResponse(status_code=status.HTTP_200_OK, content=result)
