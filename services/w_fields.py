"""WFields services module."""

from pymongo.database import Database
from pymongo.errors import PyMongoError
from bson import ObjectId
from models.company import Field, Company
from .companies import CompaniesServices

class Error(Exception):
    """Base class for exceptions in this module."""

class WFieldsServices():
    """WFields services class."""
    def __init__(self, database: Database) -> None:
        self.database = database

    def add_wfield(self, company_id: str, field: Field) -> Company:
        """
        Add a worker field.
        Args:
            wfield_id (str): Worker field id.
            field (Field): Field to add.
        Returns:
            Company: Company.
        Raises:
            Exception: If there's an error updating the company.
        """
        try:
            field = dict(field)
            field["id"] = str(ObjectId())
            if self.database.companies.find_one(
                {"_id": ObjectId(company_id), "workerFields.name": field["name"]}):
                raise Error("Field already exists")
            self.database.companies.update_one(
                {"_id": ObjectId(company_id)}, {"$push": {"workerFields": field}})
            company = CompaniesServices(self.database).get_company(company_id)
            return company
        except PyMongoError as exception:
            raise Error(f"Error adding worker field: {exception}") from exception

    def update_wfield(self, company_id: str, field_id: str, field: Field) -> Company:
        """
        Update a worker field.
        Args:
            wfield_id (str): Worker field id.
            field (Field): Field to update.
        Returns:
            Company: Company.
        Raises:
            Exception: If there's an error updating the company.
        """
        try:
            field = dict(field)
            field["id"] = field_id
            self.database.companies.update_one(
                {"_id": ObjectId(company_id), "workerFields.id": field_id},
                {"$set": {"workerFields.$": field}})
            company = CompaniesServices(self.database).get_company(company_id)
            return company
        except PyMongoError as exception:
            raise Error(f"Error updating worker field: {exception}") from exception

    def delete_wfield(self, company_id: str, field_id: str) -> Company:
        """
        Delete a worker field.
        Args:
            wfield_id (str): Worker field id.
        Returns:
            Company: Company.
        Raises:
            Exception: If there's an error updating the company.
        """
        try:
            self.database.companies.update_one(
                {"_id": ObjectId(company_id)},
                {"$pull": {"workerFields": {"id": field_id}}})
            company = CompaniesServices(self.database).get_company(company_id)
            return company
        except PyMongoError as exception:
            raise Error(f"Error deleting worker field: {exception}") from exception
