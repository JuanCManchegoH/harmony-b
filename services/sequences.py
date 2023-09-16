"""Sequence services module."""

from pymongo.errors import PyMongoError
from pymongo.database import Database
from bson import ObjectId
from models.company import Sequence, Company
from .companies import CompaniesServices\

class Error(Exception):
    """Base class for exceptions in this module."""

class SequencesServices():
    """Sequences services class."""
    def __init__(self, database: Database) -> None:
        self.database = database

    def add_sequence(self, company_id: str, sequence: Sequence) -> Company:
        """
        Add a sequence.
        Args:
            sequence (Sequence): Sequence to add.
        Returns:
            Company: Company.
        Raises:
            Exception: If there's an error updating the company.
        """
        try:
            steps = []
            for step in sequence["steps"]:
                steps.append(dict(step))
            sequence["steps"] = steps
            sequence["id"] = str(ObjectId())
            if self.database.companies.find_one(
                {"_id": ObjectId(company_id), "sequences.name": sequence["name"]}):
                raise Error("Sequence already exists")
            self.database.companies.update_one(
                {"_id": ObjectId(company_id)}, {"$push": {"sequences": sequence}})
            company = CompaniesServices(self.database).get_company(company_id)
            return company
        except PyMongoError as exception:
            raise Error(f"Error adding sequence: {exception}") from exception

    def update_sequence(self, company_id: str, sequence_id: str, sequence: Sequence) -> Company:
        """
        Update a sequence.
        Args:
            sequence_id (str): Sequence id.
            sequence (Sequence): Sequence to update.
        Returns:
            Company: Company.
        Raises:
            Exception: If there's an error updating the company.
        """
        try:
            steps = []
            for step in sequence["steps"]:
                steps.append(dict(step))
            sequence["steps"] = steps
            sequence["id"] = sequence_id
            self.database.companies.update_one(
                {"_id": ObjectId(company_id), "sequences.id": sequence_id},
                {"$set": {"sequences.$": sequence}})
            company = CompaniesServices(self.database).get_company(company_id)
            return company
        except PyMongoError as exception:
            raise Error(f"Error updating sequence: {exception}") from exception

    def delete_sequence(self, company_id: str, sequence_id: str) -> Company:
        """
        Delete a sequence.
        Args:
            sequence_id (str): Sequence id.
        Returns:
            Company: Company.
        Raises:
            Exception: If there's an error updating the company.
        """
        try:
            self.database.companies.update_one(
                {"_id": ObjectId(company_id)}, {"$pull": {"sequences": {"id": sequence_id}}})
            company = CompaniesServices(self.database).get_company(company_id)
            return company
        except PyMongoError as exception:
            raise Error(f"Error deleting sequence: {exception}") from exception
    