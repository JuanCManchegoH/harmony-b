import datetime
import pytz
from pymongo.database import Database
from models.stall import Stall, UpdateStall, StallWorker, StallsAndShifts, UpdateStallWorker
from schemas.user import UserEntity
from bson.objectid import ObjectId
from .shifts import ShiftsServices
from utils.errorsResponses import errors
from typing import List

class StallsServices():
    def __init__(self, db: Database) -> None:
        self.db = db
        
    def createStall(self, stall: Stall, user: UserEntity) -> Stall:
        try:
            stall = dict(stall)
            del stall["id"]
            stall["createdBy"] = user["userName"]
            stall["updatedBy"] = user["userName"]
            stall["createdAt"] = datetime.datetime.now(pytz.timezone("America/Bogota")).strftime("%d/%m/%Y %H:%M")
            stall["updatedAt"] = datetime.datetime.now(pytz.timezone("America/Bogota")).strftime("%d/%m/%Y %H:%M")
            stall = self.db.stalls.insert_one(stall)
            stall = self.db.stalls.find_one({"_id": stall.inserted_id})
            return stall or {}
        except Exception as e:
            raise errors["Creation error"] from e
        
    def findStalls(self, company: str, months: List[str], years: List[str], customers: List[str]) -> StallsAndShifts:
        try:
            stalls = self.db.stalls.find({"month": {"$in": months}, "year": {"$in": years}})
            shifts = ShiftsServices(self.db).findShiftsByStall(company, [str(stall["_id"]) for stall in stalls], "", customers)
            stalls = [dict(stall) for stall in stalls]
            shifts = [dict(shift) for shift in shifts]
            result = {"stalls": stalls, "shifts": shifts}
            return result or {}
        except Exception as e:
            raise errors["Read error"] from e
    
    def finsCustomerStalls(self, company: str, customer: str, months: List[str], years: List[str]) -> StallsAndShifts:
        try:
            stalls = self.db.stalls.find({"customer": customer, "month": {"$in": months}, "year": {"$in": years}})
            stalls = [dict(stall) for stall in stalls]
            shifts = ShiftsServices(self.db).findShiftsByStall(company, [str(stall["_id"]) for stall in stalls], customer, [])
            shifts = [dict(shift) for shift in shifts]
            result = {"stalls": stalls, "shifts": shifts}
            return result or {}
        except Exception as e:
            raise errors["Read error"] from e
    
    def updateStall(self, id: str, data: UpdateStall, user: UserEntity) -> Stall:
        try:
            stall = self.db.stalls.find_one({"_id": ObjectId(id)})
            if not stall:
                return errors["Update error"]
            stall = dict(stall)
            data = dict(data)
            data["updatedAt"] = datetime.datetime.now(pytz.timezone("America/Bogota")).strftime("%d/%m/%Y %H:%M")
            data["updatedBy"] = user["userName"]
            self.db.stalls.update_one({"_id": ObjectId(id)}, {"$set": data})
            stall = self.db.stalls.find_one({"_id": ObjectId(id)})
            return stall or {}
        except Exception as e:
            raise errors["Update error"] from e
    
    def deleteStall(self, company: str, id: str, shifts: List[str]) -> StallsAndShifts:
        try:
            stall = self.db.stalls.find_one({"_id": ObjectId(id)})
            if not stall:
                raise errors["Deletion error"]
            stall = dict(stall)
            self.db.stalls.delete_one({"_id": ObjectId(id)})
            shifts = ShiftsServices.deleteShifts(self, company, id, shifts)
            return stall or {}
        except Exception as e:
            raise errors["Deletion error"] from e
    
    # Stall workers
    def addStallWorker(self, id: str, worker: StallWorker, user: UserEntity) -> Stall:
        try:
            worker = dict(worker)
            worker["createdBy"] = user["userName"]
            worker["updatedBy"] = user["userName"]
            worker["createdAt"] = datetime.datetime.now(pytz.timezone("America/Bogota")).strftime("%d/%m/%Y %H:%M")
            worker["updatedAt"] = datetime.datetime.now(pytz.timezone("America/Bogota")).strftime("%d/%m/%Y %H:%M")
            stall = self.db.stalls.find_one({"_id": ObjectId(id)})
            if not stall:
                return errors["Update error"]
            self.db.stalls.update_one({"_id": ObjectId(id)}, {"$push": {"workers": worker}})
            stall = self.db.stalls.find_one({"_id": ObjectId(id)})
            return stall or {}
        except Exception as e:
            raise errors["Update error"] from e
        
    def updateStallWorker(self, id: str, workerId: str, data: UpdateStallWorker, user: UserEntity) -> Stall:
        try:
            update_data = {
                "workers.$.sequence": data["sequence"],
                "workers.$.index": data["index"],
                "workers.$.jump": data["jump"],
                "workers.$.updatedAt": datetime.datetime.now(pytz.timezone("America/Bogota")).strftime("%d/%m/%Y %H:%M"),
                "workers.$.updatedBy": user["userName"]
            }

            result = self.db.stalls.update_one(
                {"_id": ObjectId(id), "workers.id": workerId},
                {"$set": update_data}
            )

            if result.modified_count == 0:
                return errors["Update error"]

            stall = self.db.stalls.find_one({"_id": ObjectId(id)})
            return stall or {}
        except Exception as e:
            raise errors["Update error"] from e
    
    def removeWorker(self, company: str, stallId: str, workerId: str, shifts: List[str]) -> Stall:
        try:
            stall = self.db.stalls.find_one({"_id": ObjectId(stallId)})
            if not stall:
                raise errors["Deletion error"]
            stall = dict(stall)
            self.db.stalls.update_one({"_id": ObjectId(stallId)}, {"$pull": {"workers": {"id": workerId}}})
            stall = self.db.stalls.find_one({"_id": ObjectId(stallId)})
            shifts = ShiftsServices.deleteShifts(self, company, stallId, shifts)
            return stall or {}
        except Exception as e:
            raise errors["Deletion error"] from e