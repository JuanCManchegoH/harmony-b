"""Shifts services module."""

from typing import List
import datetime
import pytz
from pymongo.database import Database
from pymongo.errors import PyMongoError
from pymongo import UpdateOne
from bson import ObjectId
from models.shift import Shift
from schemas.user import user_entity

class Error(Exception):
    """Base class for exceptions in this module."""

class ShiftsServices():
    """Shifts services class."""
    def __init__(self, database: Database) -> None:
        self.database = database

    def create_shifts(self, company: str, shifts: list, user: user_entity) -> List[Shift]:
        """
        Create shifts.
        Args:
            company (str): Company id.
            shifts (list): Shifts to create.
            user (user_entity): User.
        Returns:
            List[Shift]: Shifts.
        Raises:
            Exception: If there's an error creating the shifts.
        """
        try:
            for shift in shifts:
                shift["company"] = company
                shift["createdBy"] = user["userName"]
                shift["updatedBy"] = user["userName"]
                shift["createdAt"] = datetime.datetime.now(
                    pytz.timezone("America/Bogota")).strftime("%d/%m/%Y %H:%M")
                shift["updatedAt"] = datetime.datetime.now(
                    pytz.timezone("America/Bogota")).strftime("%d/%m/%Y %H:%M")
            shifts = self.database.shifts.insert_many(shifts)
            shifts = self.database.shifts.find({"_id": {"$in": shifts.inserted_ids}})
            return shifts
        except PyMongoError as exception:
            raise Error(f"Error creating shifts: {exception}") from exception

    def get_shifts_by_workers(
        self,
        company: str,
        workers_ids: List[str],
        types: List[str]) -> List[Shift]:
        """
        Get shifts by workers.
        Args:
            company (str): Company id.
            workers_ids (List[str]): Workers ids.
            types (List[str]): Shift types.
        Returns:
            List[Shift]: Shifts.
        Raises:
            Exception: If there's an error finding the shifts.
        """
        try:
            shifts = self.database.shifts.find(
                {"company": company, "worker": {"$in": workers_ids}, "type": {"$in": types}})
            return shifts
        except PyMongoError as exception:
            raise Error(f"Error finding shifts by customer: {exception}") from exception
        
    def get_by_customer_and_month_and_year(
        self,
        company: str,
        customer: str,
        months: List[str],
        years: List[str],
        types: List[str]) -> List[Shift]:
        """
        Get shifts by customer and month and year.
        Args:
            company (str): Company id.
            customer (str): Customer id.
            months (List[str]): Months.
            years (List[str]): Years.
            types (List[str]): Shift types.
        Returns:
            List[Shift]: Shifts.
        Raises:
            Exception: If there's an error finding the shifts.
        """
        try:
            shifts = self.database.shifts.find(
                {"company": company, "customer": customer, "month": {"$in": months},
                 "year": {"$in": years}, "type": {"$in": types}})
            return shifts
        except PyMongoError as exception:
            raise Error(
                f"Error finding shifts by customer and month and year: {exception}") from exception

    def get_shifts_by_month_and_year(
        self,
        company: str,
        months: List[str],
        years: List[str],
        types: List[str]) -> List[Shift]:
        """
        Get shifts by month and year.
        Args:
            company (str): Company id.
            months (List[str]): Months.
            years (List[str]): Years.
            types (List[str]): Shift types.
        Returns:
            List[Shift]: Shifts.
        Raises:
            Exception: If there's an error finding the shifts.
        """
        try:
            shifts = self.database.shifts.find(
                {"company": company, "month": {"$in": months}, "year": {"$in": years},
                 "type": {"$in": types}})
            return shifts
        except PyMongoError as exception:
            raise Error(f"Error finding shifts by month and year: {exception}") from exception

    def update_shifts(self, company_id: str, shifts: list, user: user_entity) -> List[Shift]:
        """
        Update shifts.
        Args:
            company_id (str): Company id.
            shifts (list): Shifts to update.
            user (user_entity): User.
        Returns:
            List[Shift]: Shifts.
        Raises:
            Exception: If there's an error updating the shifts.
        """
        try:
            ids = [ObjectId(shift["id"]) for shift in shifts]
            update_operations = []
            for shift in shifts:
                updated_shift = dict(shift)
                updated_shift["updatedBy"] = user["userName"]
                updated_shift["updatedAt"] = datetime.datetime.now(
                    pytz.timezone("America/Bogota")).strftime("%d/%m/%Y %H:%M")
                del updated_shift["id"]
                update_operations.append(
                    UpdateOne({"_id": ObjectId(shift["id"])}, {"$set": updated_shift}))
            self.database.shifts.bulk_write(update_operations)
            shifts = self.database.shifts.find({"company": company_id, "_id": {"$in": ids}})
            return shifts
        except PyMongoError as exception:
            raise Error(f"Error updating shifts: {exception}") from exception

    def delete_shifts(self, company: str, stall_id: str, shifts_ids: List[str]) -> List[Shift]:
        """
        Delete shifts.
        Args:
            company (str): Company id.
            stall_id (str): Stall id.
            shifts_ids (List[str]): Shifts ids.
        Returns:
            List[Shift]: Shifts.
        Raises:
            Exception: If there's an error deleting the shifts.
        """
        try:
            shifts = self.database.shifts.find(
                {"company": company, "stall": stall_id, "_id": {"$in":
                    [ObjectId(id) for id in shifts_ids]}})
            if not shifts:
                raise Error("Shifts not found")
            self.database.shifts.delete_many(
                {"company": company, "stall": stall_id, "_id": {"$in":
                    [ObjectId(id) for id in shifts_ids]}})
            return shifts or []
        except PyMongoError as exception:
            raise Error(f"Error deleting shifts: {exception}") from exception
