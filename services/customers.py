import pytz
import datetime
from models.customer import Customer, UpdateCustomer
from schemas.user import UserEntity
from pymongo.database import Database
from bson import ObjectId
from utils.errorsResponses import errors
from typing import List

class CustomersServices():
    def __init__(self, db: Database) -> None:
        self.db = db
    
    def createCustomer(self , company: str, customer: Customer, user: UserEntity) -> Customer:
        try:
            customer = dict(customer)
            del customer["id"]
            customer["company"] = company
            if self.db.customers.find_one({"identification": customer["identification"]}):
                raise errors["Creation error"]
            customer["userName"] = user["userName"]
            customer["updatedBy"] = user["userName"]
            customer["createdAt"] = datetime.datetime.now(pytz.timezone("America/Bogota")).strftime("%d/%m/%Y %H:%M")
            customer["updatedAt"] = datetime.datetime.now(pytz.timezone("America/Bogota")).strftime("%d/%m/%Y %H:%M")
            fields = []
            for field in customer["fields"]:
                fields.append(dict(field))
            customer["fields"] = fields
            customer = self.db.customers.insert_one(customer)
            customer = self.db.customers.find_one({"_id": customer.inserted_id})
            return customer
        except Exception as e:
            raise errors["Creation error"] from e
    
    def findAllCustomers(self, company: str, userTags: list) -> List[Customer]:
        try:
            if "all" in userTags:
                customers = self.db.customers.find({"company": company})
                return customers or []
            customers = self.db.customers.find({"company": company, "tags": {"$in": userTags}})
            return customers or []
        except Exception as e:
            raise errors["Read error"] from e
    
    def updateCustomer(self, company: str, id: str, data: UpdateCustomer, user: UserEntity) -> Customer:
        try:
            customer = self.db.customers.find_one({"_id": ObjectId(id)})
            if customer["company"] != company:
                return errors["Unauthorized"]
            customer = dict(data)
            userTags = user["customers"]
            if not set(customer["tags"]).intersection(userTags) and "all" not in userTags:
                return errors["Update error"]
            data = dict(data)
            fields = []
            for field in data["fields"]:
                fields.append(dict(field))
            data["fields"] = fields
            data["updatedAt"] = datetime.datetime.now(pytz.timezone("America/Bogota")).strftime("%d/%m/%Y %H:%M")
            data["updatedBy"] = user["userName"]
            self.db.customers.update_one({"_id": ObjectId(id)}, {"$set": data})
            customer = self.db.customers.find_one({"_id": ObjectId(id)})
            return customer
        except Exception as e:
            raise errors["Update error"] from e
    
    def deleteCustomer(self, company: str, id: str, userTags: list) -> Customer:
        try:
            customer = self.db.customers.find_one({"_id": ObjectId(id)})
            if customer["company"] != company:
                raise errors["Unauthorized"]
            customer = dict(customer)
            if not set(customer["tags"]).intersection(userTags) and "all" not in userTags:
                raise errors["Deletion error"]
            self.db.customers.delete_one({"_id": ObjectId(id)})
            return customer
        except Exception as e:
            raise errors["Deletion error"] from e