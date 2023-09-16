"""Log services module."""

from typing import List
import datetime
import pytz
from pymongo.database import Database
from pymongo.errors import PyMongoError
from bson import ObjectId
from models.log import Log, CreateLog
from utils.errorsResponses import errors

class Error(Exception):
    """Base class for exceptions in this module."""
class LogsServices():
    """Logs services class."""
    def __init__(self, database: Database) -> None:
        self.database = database

    def create_log(self, data: CreateLog) -> Log:
        """
        Create a log.
        Args:
            data (CreateLog): Log data.
        Returns:
            Log: Log.
        Raises:
            Exception: If there's an error creating the log.
        """
        try:
            log = dict(data)
            log["createdAt"] = datetime.datetime.now(
                pytz.timezone("America/Bogota")).strftime("%d/%m/%Y %H:%M")
            log["month"] = datetime.datetime.now(pytz.timezone("America/Bogota")).strftime("%m")
            log["year"] = datetime.datetime.now(pytz.timezone("America/Bogota")).strftime("%Y")
            log = self.database.logs.insert_one(log)
            log = self.database.logs.find_one({"_id": log.inserted_id})
            return log
        except PyMongoError as exception:
            raise Error(f"Error creating log: {exception}") from exception

    def find_logs_by_month_and_year(self, company: str, month: str, year: str) -> List[Log]:
        """
        Find logs by month and year.
        Args:
            company (str): Company.
            month (str): Month.
            year (str): Year.
        Returns:
            List[Log]: List of logs.
        Raises:
            Exception: If there's an error reading logs.
        """
        try:
            logs = self.database.logs.find({"company": company, "month": month, "year": year})
            return logs
        except PyMongoError as exception:
            raise Error(f"Error reading logs: {exception}") from exception

    def delete_log(self, company: str, log_id: str) -> Log:
        """
        Delete a log.
        Args:
            company (str): Company.
            log_id (str): Log id.
        Returns:
            Log: Log.
        Raises:
            Exception: If there's an error deleting the log.
        """
        try:
            log = self.database.logs.find_one({"company": company, "_id": ObjectId(log_id)})
            if not log:
                raise errors["Deletion error"]
            _ = self.database.logs.find_one_and_delete(
                {"company": company, "_id": ObjectId(log_id)})
            return log
        except PyMongoError as exception:
            raise Error(f"Error deleting log: {exception}") from exception
