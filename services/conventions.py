"""Conventions services module."""

from pymongo.database import Database
from pymongo.errors import PyMongoError
from bson import ObjectId
from models.company import Convention, Company
from .companies import CompaniesServices

class Error(Exception):
    """Base class for exceptions in this module."""

class ConventionsServices():
    """Conventions services class."""
    def __init__(self, database: Database) -> None:
        self.database = database

    def add_convention(self, company_id: str, convention: Convention) -> Company:
        """
        Add a convention.
        Args:
            company_id (str): Company id.
            convention (Convention): Convention to add.
        Returns:
            Company: Company.
        Raises:
            Exception: If there's an error updating the company.
        """
        try:
            convention["id"] = str(ObjectId())
            if self.database.companies.find_one(
                {"_id": ObjectId(company_id), "conventions.name": convention["name"]}):
                raise Error("Convention already exists")
            self.database.companies.update_one(
                {"_id": ObjectId(company_id)}, {"$push": {"conventions": convention}})
            company = CompaniesServices(self.database).get_company(company_id)
            return company
        except PyMongoError as exception:
            raise Error(f"Error adding convention: {exception}") from exception

    def update_convention(
        self,
        company_id: str,
        convention_id: str,
        convention: Convention) -> Company:
        """
        Update a convention.
        Args:
            company_id (str): Company id.
            convention_id (str): Convention id.
            convention (Convention): Convention to update.
        Returns:
            Company: Company.
        Raises:
            Exception: If there's an error updating the company.
        """
        try:
            convention["id"] = convention_id
            self.database.companies.update_one(
                {"_id": ObjectId(company_id), "conventions.id": convention_id},
                {"$set": {"conventions.$": convention}})
            company = CompaniesServices(self.database).get_company(company_id)
            return company
        except PyMongoError as exception:
            raise Error(f"Error updating convention: {exception}") from exception

    def delete_convention(self, company_id: str, convention_id: str) -> Company:
        """
        Delete a convention.
        Args:
            company_id (str): Company id.
            convention_id (str): Convention id.
        Returns:
            Company: Company.
        Raises:
            Exception: If there's an error updating the company.
        """
        try:
            self.database.companies.update_one(
                {"_id": ObjectId(company_id)}, {"$pull": {"conventions": {"id": convention_id}}})
            company = CompaniesServices(self.database).get_company(id)
            return company
        except PyMongoError as exception:
            raise Error(f"Error deleting convention: {exception}") from exception
