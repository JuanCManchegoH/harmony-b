import datetime
import pytz
from pymongo.database import Database
from pymongo import UpdateOne
from models.shift import Shift
from schemas.user import UserEntity
from bson.objectid import ObjectId
from utils.errorsResponses import errors
from typing import List

class ShiftsServices():
    def __init__(self, db: Database) -> None:
        self.db = db
        
    def createShifts(self, company: str, shifts: list, user: UserEntity) -> List[Shift]:
        try:
            shifts = [dict(shift) for shift in shifts]
            for shift in shifts:
                shift["company"] = company
                shift["createdBy"] = user["userName"]
                shift["updatedBy"] = user["userName"]
                shift["createdAt"] = datetime.datetime.now(pytz.timezone("America/Bogota")).strftime("%d/%m/%Y %H:%M")
                shift["updatedAt"] = datetime.datetime.now(pytz.timezone("America/Bogota")).strftime("%d/%m/%Y %H:%M")
            shifts = self.db.shifts.insert_many(shifts)
            shifts = self.db.shifts.find({"_id": {"$in": shifts.inserted_ids}})
            return shifts or []
        except Exception as e:
            raise errors["Creation error"] from e
        
    def findShiftsByCustomer(self, company: str, stallsIds: List[str], customer: str) -> List[Shift]:
        try:
            stallShifts = self.db.shifts.find({"company": company, "stall": {"$in": stallsIds}})
            customerShifts = self.db.shifts.find({"company": company, "stall": customer})
            shifts = list(stallShifts) + list(customerShifts)
            return shifts or []
        except Exception as e:
            raise errors["Read error"] from e
    
    def findShiftsByCustomers(self, company: str, stallsIds: List[str], customers: List[str]) -> List[Shift]:
        try:
            stallShifts = self.db.shifts.find({"company": company, "stall": {"$in": stallsIds}})
            customersShifts = self.db.shifts.find({"company": company, "stall": {"$in": customers}})
            shifts = list(stallShifts) + list(customersShifts)
            return shifts or []
        except Exception as e:
            raise errors["Read error"] from e
        
    def updateShifts(self, company: str, shifts: list, user: UserEntity) -> List[Shift]:
        try:
            shifts = [dict(shift) for shift in shifts]  # Convert shifts to dict
            ids = [ObjectId(shift["id"]) for shift in shifts]  # Get ids from shifts
            update_operations = []
            for shift in shifts:
                updated_shift = dict(shift)
                updated_shift["updatedBy"] = user["userName"]
                updated_shift["updatedAt"] = datetime.datetime.now(pytz.timezone("America/Bogota")).strftime("%d/%m/%Y %H:%M")
                del updated_shift["id"]  # Remove id from the updated_shift
                update_operations.append(UpdateOne({"_id": ObjectId(shift["id"])}, {"$set": updated_shift}))
            self.db.shifts.bulk_write(update_operations)
                
            shifts = self.db.shifts.find({"company": company, "_id": {"$in": ids}})
            return shifts
        except Exception as e:
            print(e)
            raise errors["Update error"] from e
        
    
    def deleteShifts(self, company: str, stallId: str, ids: List[str]) -> List[Shift]:
        try:
            shifts = self.db.shifts.find({"company": company, "stall": stallId, "_id": {"$in": [ObjectId(id) for id in ids]}})
            if not shifts:
                return errors["Deletion error"]
            self.db.shifts.delete_many({"company": company, "stall": stallId, "_id": {"$in": [ObjectId(id) for id in ids]}})
            return shifts or []
        except Exception as e:
            raise errors["Deletion error"] from e
