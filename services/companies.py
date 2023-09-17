"""Companies services module."""

from typing import List
from bson import ObjectId
from pymongo.database import Database
from pymongo.errors import PyMongoError
from models.company import Company, UpdateCompany

class Error(Exception):
    """Base class for exceptions in this module."""

class CompaniesServices():
    """Companies services class."""
    def __init__(self, database: Database) -> None:
        self.database = database

    # Create a company
    def create_company(self, company: Company) -> Company:
        """
        Create a company.
        Args:
            company (Company): Company to create.
        Returns:
            Company: Created company.
        Raises:
            Exception: If there's an error creating the company.
        """
        try:
            del company["id"]
            if self.database.companies.find_one({"db": company["db"]}):
                raise Error("Company already exists")
            insertion_result = self.database.companies.insert_one(company)
            created_company = self.database.companies.find_one(
                {"_id": insertion_result.inserted_id})
            return created_company
        except PyMongoError as exception:
            raise Error(f"Error creating company: {exception}") from exception

    def get_company(self, company_id: str) -> Company:
        """
        Get a company.
        Args:
            company_id (str): Company id.
        Returns:
            Company: Company.
        Raises:
            Exception: If there's an error reading the company.
        """
        try:
            company = self.database.companies.find_one({"_id": ObjectId(company_id)})
            return company
        except PyMongoError as exception:
            raise Error(f"Error reading company: {exception}") from exception

    def get_all_companies(self) -> List[Company]:
        """
        Get all companies.
        Args:
            company_id (str): Company id.
        Returns:
            List[Company]: List of companies.
        Raises:
            Exception: If there's an error reading the companies.
        """
        try:
            companies = self.database.companies.find()
            return list(companies)
        except PyMongoError as exception:
            raise Error(f"Error reading companies: {exception}") from exception

    def update_company(self, company_id: str, company: UpdateCompany) -> Company:
        """
        Update a company.
        Args:
            company_id (str): Company id.
        Returns:
            Company: Updated company.
        Raises:
            errors["Update error"]: If the company could not be updated.
        """
        try:
            self.database.companies.update_one({"_id": ObjectId(company_id)}, {"$set": company})
            company = self.get_company(company_id)
            return company
        except PyMongoError as exception:
            raise Error(f"Error updating company: {exception}") from exception

    def delete_company(self, company_id: str) -> Company:
        """Delete a company."""
        try:
            company = self.get_company(company_id)
            if not company:
                raise Error("Company not found")
            self.database.companies.delete_one({"_id": ObjectId(company_id)})
            return company
        except PyMongoError as exception:
            raise Error(f"Error deleting company: {exception}") from exception
