import datetime
import pytz
from pymongo.database import Database
from models.log import Log, CreateLog
from bson import ObjectId
from utils.errorsResponses import errors
from typing import List

class LogsServices():
    def __init__(self, db: Database) -> None:
        self.db = db
        
    def createLog(self, data: CreateLog) -> Log:
        try:
            log = dict(data)
            log["createdAt"] = datetime.datetime.now(pytz.timezone("America/Bogota")).strftime("%d/%m/%Y %H:%M")
            log["month"] = datetime.datetime.now(pytz.timezone("America/Bogota")).strftime("%m")
            log["year"] = datetime.datetime.now(pytz.timezone("America/Bogota")).strftime("%Y")
            log = self.db.logs.insert_one(log)
            log = self.db.logs.find_one({"_id": log.inserted_id})
            return log or {}
        except Exception as e:
            raise errors["Creation error"] from e
        
    def findLogsByMonthAndYear(self, company: str, month: str, year: str) -> List[Log]:
        try:
            logs = self.db.logs.find({"company": company, "month": month, "year": year})
            return logs or []
        except Exception as e:
            raise errors["Read error"] from e
    
    def deleteLog(self, company: str, logId: str) -> Log:
        try:
            log = self.db.logs.find_one({"company": company, "_id": ObjectId(logId)})
            if not log:
                raise errors["Deletion error"]
            _ = self.db.logs.find_one_and_delete({"company": company, "_id": ObjectId(logId)})
            return log or {}
        except Exception as e:
            raise errors["Deletion error"] from e