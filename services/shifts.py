import datetime
import pytz
from fastapi import HTTPException, status
from pymongo.database import Database
from models.shift import Shift
from schemas.shift import ShiftEntity
from schemas.user import UserEntity
from bson.objectid import ObjectId
from typing import List

class ShiftsServices():
    def __init__(self, db: Database) -> None:
        self.db = db
        
    def createShifts(self, company: str, shifts: List[Shift], user: UserEntity) -> list:
        shifts = [dict(shift) for shift in shifts]
        for shift in shifts:
            del shift["id"]
            shift["company"] = company
            shift["userName"] = user["userName"]
            shift["updatedBy"] = user["userName"]
            shift["createdAt"] = datetime.datetime.now(pytz.timezone("America/Bogota")).strftime("%Y-%m-%d")
            shift["updatedAt"] = datetime.datetime.now(pytz.timezone("America/Bogota")).strftime("%Y-%m-%d")
        try:
            shifts = self.db.shifts.insert_many(shifts)
            shifts = self.db.shifts.find({"_id": {"$in": shifts.inserted_ids}})
            return [ShiftEntity(shift) for shift in shifts]
        except:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error creating shifts.")
        
    def findShiftsByStall(self, company: str, stall: str) -> list:
        shifts = self.db.shifts.find({"company": company, "stall": stall})
        if shifts:
            return [ShiftEntity(shift) for shift in shifts]
        return None

    def replaceShifts(self, company: str, stall: str, shifts: List[Shift], user: UserEntity) -> list:
        shifts = [dict(shift) for shift in shifts]
        for shift in shifts:
            del shift["id"]
            shift["company"] = company
            shift["userName"] = user["userName"]
            shift["updatedBy"] = user["userName"]
            shift["createdAt"] = datetime.datetime.now(pytz.timezone("America/Bogota")).strftime("%Y-%m-%d")
            shift["updatedAt"] = datetime.datetime.now(pytz.timezone("America/Bogota")).strftime("%Y-%m-%d")
        try:
            for shift in shifts:
                self.db.shifts.delete_one({"company": company, "stall": stall, "day": shift["day"], "worker": shift["worker"], "customer": shift["customer"]})
            shifts = self.db.shifts.insert_many(shifts)
            shifts = self.db.shifts.find({"_id": {"$in": shifts.inserted_ids}})
            return [ShiftEntity(shift) for shift in shifts]
        except:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error creating shifts.")
        
    def deactivateShift(self, company: str, id: str, user: UserEntity) -> ShiftEntity:
        shift = self.db.shifts.find_one({"_id": ObjectId(id)})
        if not shift:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error deleting shift.")
        shift = dict(shift)
        if shift["company"] != company:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized.")
        shift["active"] = False
        shift["updatedBy"] = user["userName"]
        shift["updatedAt"] = datetime.datetime.now(pytz.timezone("America/Bogota")).strftime("%Y-%m-%d")
        try:
            self.db.shifts.update_one({"_id": ObjectId(id)}, {"$set": shift})
        except:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error deleting shift.")
        return ShiftEntity(shift)
    
    def deactivateShifts(self, company: str, stall: str, user: UserEntity) -> list:
        shifts = self.db.shifts.find({"company": company, "stall": stall})
        if not shifts:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error deleting shifts.")
        shifts = [dict(shift) for shift in shifts]
        shiftsDeactivated = []
        try:
            for shift in shifts:
                self.deactivateShift(company, str(shift["_id"]), user)
                shiftsDeactivated.append(shift)
        except:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error deleting shifts.")
        return [ShiftEntity(shift) for shift in shiftsDeactivated]
        
    
    def deleteShift(self, company: str, id: str) -> ShiftEntity:
        shift = self.db.shifts.find_one({"_id": ObjectId(id)})
        if not shift:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error deleting shift.")
        shift = dict(shift)
        if shift["company"] != company:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized.")
        try:
            self.db.shifts.delete_one({"_id": ObjectId(id)})
        except:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error deleting shift.")
        return ShiftEntity(shift)
    
    def deleteShifts(self, company: str, stall: str) -> list:
        shifts = self.db.shifts.find({"company": company, "stall": stall})
        if not shifts:
            return None
        shifts = [dict(shift) for shift in shifts]
        try:
            for shift in shifts:
                self.deleteShift(company, str(shift["_id"]))
        except:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error deleting shifts.")
        return [ShiftEntity(shift) for shift in shifts]

    def deleteShiftsByWorkerAndStall(self, company: str, worker: str, stall: str) -> list:
        shifts = self.db.shifts.find({"company": company, "worker": worker, "stall": stall})
        if not shifts:
            return None
        shifts = [dict(shift) for shift in shifts]
        try:
            for shift in shifts:
                self.deleteShift(company, str(shift["_id"]))
        except:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error deleting shifts.")
        return [ShiftEntity(shift) for shift in shifts]