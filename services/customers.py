import datetime
import pytz
from fastapi import HTTPException, status
from pymongo.database import Database
from models.customer import Customer, UpdateCustomer
from schemas.customer import CustomerEntity
from schemas.user import UserEntity
from bson.objectid import ObjectId

class CustomersServices():
    def __init__(self, db: Database) -> None:
        self.db = db
    
    def createCustomer(self , company: str, customer: Customer, user: UserEntity) -> CustomerEntity:
        customer = dict(customer)
        del customer["id"]
        customer["company"] = company
        if self.db.customers.find_one({"identification": customer["identification"]}):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Customer already exists.")
        customer["userName"] = user["userName"]
        customer["updatedBy"] = user["userName"]
        customer["createdAt"] = datetime.datetime.now(pytz.timezone("America/Bogota")).strftime("%Y-%m-%d")
        customer["updatedAt"] = datetime.datetime.now(pytz.timezone("America/Bogota")).strftime("%Y-%m-%d")
        try:
            customer = self.db.customers.insert_one(customer)
            customer = self.db.customers.find_one({"_id": customer.inserted_id})
            return CustomerEntity(customer)
        except:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error creating customer.")
    
    def findAllCustomers(self, company: str, userTags: list) -> list:
        customers = self.db.customers.find({"company": company, "tags": {"$in": userTags}})
        if customers:
            return [CustomerEntity(customer) for customer in customers]
        return None
    
    def updateCustomer(self, company: str, id: str, data: UpdateCustomer, user: UserEntity) -> CustomerEntity:
        customer = self.db.customers.find_one({"_id": ObjectId(id)})
        if not customer:
            return None
        if customer["company"] != company:
            return None
        customer = dict(customer)
        userTags = user["customers"]
        if not set(customer["tags"]).intersection(userTags):
            return None
        data = dict(data)
        data["updatedAt"] = datetime.datetime.now(pytz.timezone("America/Bogota")).strftime("%Y-%m-%d")
        data["updatedBy"] = user["userName"]
        self.db.customers.update_one({"_id": ObjectId(id)}, {"$set": data})
        customer = self.db.customers.find_one({"_id": ObjectId(id)})
        return CustomerEntity(customer)
    
    def deleteCustomer(self, company: str, id: str, userTags: list) -> CustomerEntity:
        customer = self.db.customers.find_one({"_id": ObjectId(id)})
        if not customer:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error deleting customer.")
        if customer["company"] != company:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error deleting customer.")
        customer = dict(customer)
        if not set(customer["tags"]).intersection(userTags):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error deleting customer.")
        try:
            self.db.customers.delete_one({"_id": ObjectId(id)})
            return CustomerEntity(customer)
        except:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error deleting customer.")