"""Tags services module."""

from pymongo.database import Database
from pymongo.errors import PyMongoError
from bson import ObjectId
from models.company import Tag, Company
from .companies import CompaniesServices

class Error(Exception):
    """Base class for exceptions in this module."""

class TagsServices():
    """Tags services class."""
    def __init__(self, database: Database) -> None:
        self.database = database

    def add_tag(self, company_id: str, tag: Tag) -> Company:
        """
        Add a tag.
        Args:
            company_id (str): Company id.
            tag (Tag): Tag to add.
        Returns:
            Company: Company.
        Raises:
            Exception: If there's an error updating the company.
        """
        try:
            tag["id"] = str(ObjectId())
            if self.database.companies.find_one(
                {"_id": ObjectId(company_id),
                 "tags.name": tag["name"],
                 "tags.scope": tag["scope"]}):
                raise Error("Tag already exists")
            self.database.companies.update_one({"_id": ObjectId(company_id)},
                                               {"$push": {"tags": tag}})
            company = CompaniesServices(self.database).get_company(company_id)
            return company
        except PyMongoError as exception:
            raise Error(f"Error adding tag: {exception}") from exception

    def update_tag(self, company_id: str, tag_id: str, tag: Tag) -> Company:
        """
        Update a tag.
        Args:
            company_id (str): Company id.
            tag_id (str): Tag id.
            tag (Tag): Tag to update.
        Returns:
            Company: Company.
        Raises:
            Exception: If there's an error updating the company.
        """
        try:
            tag["id"] = tag_id
            self.database.companies.update_one(
                {"_id": ObjectId(company_id), "tags.id": tag_id},
                {"$set": {"tags.$": tag}})
            company = CompaniesServices(self.database).get_company(company_id)
            return company
        except PyMongoError as exception:
            raise Error(f"Error updating tag: {exception}") from exception

    def delete_tag(self, company_id: str, tag_id: str) -> Company:
        """
        Delete a tag.
        Args:
            company_id (str): Company id.
            tag_id (str): Tag id.
        Returns:
            Company: Company.
        Raises:
            Exception: If there's an error updating the company.
        """
        try:
            self.database.companies.update_one(
                {"_id": ObjectId(company_id)}, {"$pull": {"tags": {"id": tag_id}}})
            company = CompaniesServices(self.database).get_company(company_id)
            return company
        except PyMongoError as exception:
            raise Error(f"Error deleting tag: {exception}") from exception
