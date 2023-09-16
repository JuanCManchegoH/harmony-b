"""Positions services module."""

from pymongo.database import Database
from pymongo.errors import PyMongoError
from bson import ObjectId
from models.company import Position, Company
from .companies import CompaniesServices

class Error(Exception):
    """Base class for exceptions in this module."""

class PositionsServices():
    """Positions services class."""
    def __init__(self, database: Database) -> None:
        """Positions services class."""
        self.database = database

    def add_position(self, company_id: str, position: Position) -> Company:
        """
        Add a position.
        Args:
            company_id (str): Company id.
            position (Position): Position to add.
        Returns:
            Company: Company.
        Raises:
            Exception: If there's an error updating the company.
        """
        try:
            position["id"] = str(ObjectId())
            if self.database.companies.find_one(
                {"_id": ObjectId(company_id), "positions.name": position["name"]}):
                raise Error("Position already exists")
            self.database.companies.update_one(
                {"_id": ObjectId(company_id)}, {"$push": {"positions": position}})
            company = CompaniesServices(self.database).get_company(company_id)
            return company
        except PyMongoError as exception:
            raise Error(f"Error adding position: {exception}") from exception

    def update_position(self, company_id: str, position_id: str, position: Position) -> Company:
        """
        Update a position.
        Args:
            company_id (str): Company id.
            position_id (str): Position id.
            position (Position): Position to update.
        Returns:
            Company: Company.
        Raises:
            Exception: If there's an error updating the company.
        """
        try:
            position["id"] = position_id
            self.database.companies.update_one(
                {"_id": ObjectId(company_id), "positions.id": position_id},
                {"$set": {"positions.$": position}})
            company = CompaniesServices(self.database).get_company(company_id)
            return company
        except PyMongoError as exception:
            raise Error(f"Error updating position: {exception}") from exception

    def delete_position(self, company_id: str, position_id: str) -> Company:
        """
        Delete a position.
        Args:
            company_id (str): Company id.
            position_id (str): Position id.
        Returns:
            Company: Company.
        Raises:
            Exception: If there's an error updating the company.
        """
        try:
            self.database.companies.update_one(
                {"_id": ObjectId(company_id)}, {"$pull": {"positions": {"id": position_id}}})
            company = CompaniesServices(self.database).get_company(company_id)
            return company
        except PyMongoError as exception:
            raise Error(f"Error deleting position: {exception}") from exception
