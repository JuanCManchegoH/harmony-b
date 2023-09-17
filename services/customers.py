"""Cussomers services module."""

import datetime
from typing import List
import pytz
from bson import ObjectId
from pymongo.database import Database
from pymongo.errors import PyMongoError
from models.customer import Customer, UpdateCustomer
from schemas.user import user_entity

class Error(Exception):
    """Base class for exceptions in this module."""

class CustomersServices():
    """Customers services class."""
    def __init__(self, database: Database) -> None:
        self.database = database

    def create_customer(self , company: str, customer: Customer, user: user_entity) -> Customer:
        """
        Create a customer.
        Args:
            company (str): Company name.
            customer (Customer): Customer data.
            user (user_entity): User data.
        Returns:
            Customer: Customer created.
        Raises:
            Error: Customer already exists.
            Error: Error creating customer.
        """
        try:
            del customer["id"]
            customer["company"] = company
            if self.database.customers.find_one({"identification": customer["identification"]}):
                raise Error("Customer already exists")
            customer["userName"] = user["userName"]
            customer["updatedatabasey"] = user["userName"]
            customer["createdAt"] = datetime.datetime.now(
                pytz.timezone("America/Bogota")).strftime("%d/%m/%Y %H:%M")
            customer["updatedAt"] = datetime.datetime.now(
                pytz.timezone("America/Bogota")).strftime("%d/%m/%Y %H:%M")
            fields = []
            for field in customer["fields"]:
                fields.append(dict(field))
            customer["fields"] = fields
            customer = self.database.customers.insert_one(customer)
            customer = self.database.customers.find_one({"_id": customer.inserted_id})
            return customer
        except PyMongoError as exception:
            raise Error(f"Error creating customer: {exception}") from exception

    def get_all_customers(self, company: str, user_tags: list) -> List[Customer]:
        """
        Find all customers.
        Args:
            company (str): Company name.
            user_tags (list): User tags.
        Returns:
            List[Customer]: Customers found.
        Raises:
            Error: Error finding customers.
        """
        try:
            if "all" in user_tags:
                customers = self.database.customers.find({"company": company})
                return customers
            customers = self.database.customers.find(
                {"company": company, "tags": {"$in": user_tags}})
            return customers
        except PyMongoError as exception:
            raise Error(f"Error finding customers: {exception}") from exception

    def update_customer(
        self,
        company: str,
        customer_id: str,
        data: UpdateCustomer,
        user: user_entity) -> Customer:
        """
        Update a customer.
        Args:
            company (str): Company name.
            customer_id (str): Customer id.
            data (UpdateCustomer): Customer data.
            user (user_entity): User data.
        Returns:
            Customer: Customer updated.
        Raises:
            Error: Customer not found.
            Error: Error updating customer.
        """
        try:
            customer = self.database.customers.find_one({"_id": ObjectId(customer_id)})
            if customer["company"] != company:
                raise Error("Customer not found")
            user_tags = user["customers"]
            if not set(customer["tags"]).intersection(user_tags) and "all" not in user_tags:
                raise Error("Customer not found")
            fields = []
            for field in data["fields"]:
                fields.append(dict(field))
            data["fields"] = fields
            data["updatedAt"] = datetime.datetime.now(
                pytz.timezone("America/Bogota")).strftime("%d/%m/%Y %H:%M")
            data["updatedatabasey"] = user["userName"]
            self.database.customers.update_one({"_id": ObjectId(customer_id)}, {"$set": data})
            customer = self.database.customers.find_one({"_id": ObjectId(customer_id)})
            return customer
        except PyMongoError as exception:
            raise Error(f"Error updating customer: {exception}") from exception

    def delete_customer(self, company: str, customer_id: str, user_tags: list) -> Customer:
        """
        Delete a customer.
        Args:
            company (str): Company name.
            customer_id (str): Customer id.
            user_tags (list): User tags.
        Returns:
            Customer: Customer deleted.
        Raises:
            Error: Customer not found.
            Error: Error deleting customer.
        """
        try:
            customer = self.database.customers.find_one({"_id": ObjectId(customer_id)})
            if customer["company"] != company:
                raise Error("Customer not found")
            customer = dict(customer)
            if not set(customer["tags"]).intersection(user_tags) and "all" not in user_tags:
                raise Error("Customer not found")
            self.database.customers.delete_one({"_id": ObjectId(customer_id)})
            return customer
        except PyMongoError as exception:
            raise Error(f"Error deleting customer: {exception}") from exception
