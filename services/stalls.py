"""Stalls services module."""

import datetime
from typing import List
import pytz
from pymongo.database import Database
from pymongo.errors import PyMongoError
from bson.objectid import ObjectId
from models.stall import Stall, UpdateStall, StallWorker, StallsAndShifts, UpdateStallWorker
from schemas.user import user_entity
from .shifts import ShiftsServices

class Error(Exception):
    """Base class for exceptions in this module."""

class StallsServices():
    """Stalls services class."""
    def __init__(self, database: Database) -> None:
        self.database = database

    def create_stall(self, stall: Stall, user: user_entity) -> Stall:
        """
        Create a stall.
        Args:
            stall (Stall): Stall to create.
            user (user_entity): User.
        Returns:
            Stall: Created stall.
        Raises:
            Exception: If there's an error creating the stall.
        """
        try:
            del stall["id"]
            stall["createdBy"] = user["userName"]
            stall["updatedBy"] = user["userName"]
            stall["createdAt"] = datetime.datetime.now(
                pytz.timezone("America/Bogota")).strftime("%d/%m/%Y %H:%M")
            stall["updatedAt"] = datetime.datetime.now(
                pytz.timezone("America/Bogota")).strftime("%d/%m/%Y %H:%M")
            stall = self.database.stalls.insert_one(stall)
            stall = self.database.stalls.find_one({"_id": stall.inserted_id})
            return stall
        except PyMongoError as exception:
            raise Error(f"Error creating stall: {exception}") from exception

    def get_stall(self, stall_id: str) -> Stall:
        """
        Find a stall.
        Args:
            stall_id (str): Stall id.
        Returns:
            Stall: Stall.
        Raises:
            Exception: If there's an error reading the stall.
        """
        try:
            stall = self.database.stalls.find_one({"_id": ObjectId(stall_id)})
            return stall
        except PyMongoError as exception:
            raise Error(f"Error reading stall: {exception}") from exception

    def get_stalls(
        self,
        months: List[str],
        years: List[str]) -> List[Stall]:
        """
        Find stalls.
        Args:
            company (str): Company id.
            months (List[str]): Months.
            years (List[str]): Years.
            types (List[str]): Shift types.
        Returns:
            StallsAndShifts: Stalls and shifts.
        Raises:
            Exception: If there's an error reading the stalls.
        """
        try:
            result = self.database.stalls.find(
                { "month": {"$in": months}, "year": {"$in": years}})
            return result
        except PyMongoError as exception:
            raise Error(f"Error reading stalls: {exception}") from exception

    def get_customer_stalls(
        self,
        company: str,
        customer: str,
        months: List[str],
        years: List[str],
        types: List[str]) -> StallsAndShifts:
        """
        Find stalls.
        Args:
            company (str): Company id.
            customer (str): Customer id.
            months (List[str]): Months.
            years (List[str]): Years.
            types (List[str]): Shift types.
        Returns:
            StallsAndShifts: Stalls and shifts.
        Raises:
            Exception: If there's an error reading the stalls.
        """
        try:
            stalls = self.database.stalls.find(
                {"customer": customer, "month": {"$in": months}, "year": {"$in": years}})
            stalls = [dict(stall) for stall in stalls]
            shifts = ShiftsServices(self.database).get_by_customer_and_month_and_year(
                company, customer, months, years, types)
            shifts = [dict(shift) for shift in shifts]
            result = {"stalls": stalls, "shifts": shifts}
            return result
        except PyMongoError as exception:
            raise Error(f"Error reading stalls: {exception}") from exception

    def update_stall(self, stall_id: str, data: UpdateStall, user: user_entity) -> Stall:
        """
        Update a stall.
        Args:
            stall_id (str): Stall id.
            data (UpdateStall): Stall data to update.
            user (user_entity): User.
        Returns:
            Stall: Updated stall.
        Raises:
            Exception: If there's an error updating the stall.
        """
        try:
            stall = self.database.stalls.find_one({"_id": ObjectId(stall_id)})
            if not stall:
                raise Error("Stall not found")
            stall = dict(stall)
            data["updatedAt"] = datetime.datetime.now(
                pytz.timezone("America/Bogota")).strftime("%d/%m/%Y %H:%M")
            data["updatedBy"] = user["userName"]
            self.database.stalls.update_one({"_id": ObjectId(stall_id)}, {"$set": data})
            stall = self.database.stalls.find_one({"_id": ObjectId(stall_id)})
            return stall or {}
        except PyMongoError as exception:
            raise Error(f"Error updating stall: {exception}") from exception

    def delete_stall(self, company_id: str, stall_id: str, shifts: List[str]) -> StallsAndShifts:
        """
        Delete a stall.
        Args:
            company_id (str): Company id.
            stall_id (str): Stall id.
            shifts (List[str]): Shifts ids.
        Returns:
            StallsAndShifts: Stalls and shifts.
        Raises:
            Exception: If there's an error deleting the stall.
        """
        try:
            stall = self.database.stalls.find_one({"_id": ObjectId(stall_id)})
            if not stall:
                raise Error("Stall not found")
            stall = dict(stall)
            self.database.stalls.delete_one({"_id": ObjectId(stall_id)})
            shifts = ShiftsServices.delete_shifts(self, company_id, stall_id, shifts)
            return stall
        except PyMongoError as exception:
            raise Error(f"Error deleting stall: {exception}") from exception

    # Stall workers
    def add_stall_worker(self, stall_id: str, worker: StallWorker, user: user_entity) -> Stall:
        """
        Add a stall worker.
        Args:
            stall_id (str): Stall id.
            worker (StallWorker): Stall worker.
            user (user_entity): User.
        Returns:
            Stall: Stall.
        Raises:
            Exception: If there's an error adding the worker.
        """
        try:
            worker = dict(worker)
            worker["createdBy"] = user["userName"]
            worker["updatedBy"] = user["userName"]
            worker["createdAt"] = datetime.datetime.now(
                pytz.timezone("America/Bogota")).strftime("%d/%m/%Y %H:%M")
            worker["updatedAt"] = datetime.datetime.now(
                pytz.timezone("America/Bogota")).strftime("%d/%m/%Y %H:%M")
            stall = self.database.stalls.find_one({"_id": ObjectId(stall_id)})
            if not stall:
                raise Error("Stall not found")
            self.database.stalls.update_one(
                {"_id": ObjectId(stall_id)}, {"$push": {"workers": worker}})
            stall = self.database.stalls.find_one({"_id": ObjectId(stall_id)})
            return stall
        except PyMongoError as exception:
            raise Error(f"Error adding worker: {exception}") from exception

    def update_stall_worker(
        self,
        stall_id: str,
        worker_id: str,
        data: UpdateStallWorker,
        user: user_entity) -> Stall:
        """
        Update a stall worker.
        Args:
            stall_id (str): Stall id.
            worker_id (str): Worker id.
            data (UpdateStallWorker): Stall worker data to update.
            user (user_entity): User.
        Returns:
            Stall: Updated stall.
        Raises:
            Exception: If there's an error updating the worker.
        """
        try:
            update_data = {
                "workers.$.sequence": data["sequence"],
                "workers.$.index": data["index"],
                "workers.$.jump": data["jump"],
                "workers.$.updatedAt": datetime.datetime.now(
                    pytz.timezone("America/Bogota")).strftime("%d/%m/%Y %H:%M"),
                "workers.$.updatedatabasey": user["userName"]
            }
            result = self.database.stalls.update_one(
                {"_id": ObjectId(stall_id), "workers.id": worker_id},
                {"$set": update_data}
            )
            if result.modified_count == 0:
                raise Error("Worker not found")
            stall = self.database.stalls.find_one({"_id": ObjectId(stall_id)})
            return stall
        except PyMongoError as exception:
            raise Error(f"Error updating worker: {exception}") from exception

    def remove_worker(
        self,
        company: str,
        stall_id: str,
        worker_id: str,
        shifts: List[str]) -> Stall:
        """
        Remove a worker.
        Args:
            company (str): Company id.
            stall_id (str): Stall id.
            worker_id (str): Worker id.
            shifts (List[str]): Shifts ids. 
        Returns:
            Stall: Stall.
        Raises:
            Exception: If there's an error removing the worker.
        """
        try:
            stall = self.database.stalls.find_one({"_id": ObjectId(stall_id)})
            if not stall:
                raise Error("Stall not found")
            stall = dict(stall)
            self.database.stalls.update_one(
                {"_id": ObjectId(stall_id)}, {"$pull": {"workers": {"id": worker_id}}})
            stall = self.database.stalls.find_one({"_id": ObjectId(stall_id)})
            shifts = ShiftsServices.delete_shifts(self, company, stall_id, shifts)
            return stall
        except PyMongoError as exception:
            raise Error(f"Error removing worker: {exception}") from exception
