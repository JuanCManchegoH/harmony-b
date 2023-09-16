"""CFields services module."""

from pymongo.database import Database
from pymongo.errors import PyMongoError
from bson import ObjectId
from models.company import Company, Field
from .companies import CompaniesServices

class Error(Exception):
    """Base class for exceptions in this module."""

class CFieldsServices():
    """CFields services class."""
    def __init__(self, database: Database) -> None:
        self.database = database

    def add_cfield(self, company_id: str, field: Field) -> Company:
        """
        Add a customer field.
        Args:
            cfield_id (str): Customer field id.
            field (Field): Field to add.
        Returns:
            Company: Company.
        Raises:
            Exception: If there's an error updating the company.
        """
        try:
            field["id"] = str(ObjectId())
            if self.database.companies.find_one(
                {"_id": ObjectId(company_id), "customerFields.name": field["name"]}):
                raise Error("Field already exists")
            self.database.companies.update_one(
                {"_id": ObjectId(company_id)}, {"$push": {"customerFields": field}})
            company = CompaniesServices(self.database).get_company(company_id)
            return company
        except PyMongoError as exception:
            raise Error(f"Error adding customer field: {exception}") from exception

    def update_cfield(self, company_id: str, field_id: str, field: Field) -> Company:
        """
        Update a customer field.
        Args:
            cfield_id (str): Customer field id.
            field (Field): Field to update.
        Returns:
            Company: Company.
        Raises:
            Exception: If there's an error updating the company.
        """
        try:
            field["id"] = field_id
            self.database.companies.update_one(
                {"_id": ObjectId(company_id), "customerFields.id": field_id},
                {"$set": {"customerFields.$": field}})
            company = CompaniesServices(self.database).get_company(company_id)
            return company
        except PyMongoError as exception:
            raise Error(f"Error updating customer field: {exception}") from exception

    def delete_cfield(self, company_id: str, field_id: str) -> Company:
        """
        Delete a customer field.
        Args:
            cfield_id (str): Customer field id.
        Returns:
            Company: Company.
        Raises:
            Exception: If there's an error updating the company.
        """
        try:
            self.database.companies.update_one(
                {"_id": ObjectId(company_id)}, {"$pull": {"customerFields": {"id": field_id}}})
            company = CompaniesServices(self.database).get_company(company_id)
            return company
        except PyMongoError as exception:
            raise Error(f"Error deleting customer field: {exception}") from exception
        