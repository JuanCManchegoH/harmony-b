import datetime
import pytz
from fastapi import HTTPException, status
from pymongo.database import Database
from models.stall import Stall, UpdateStall, StallWorker, UpdateStallWorker, StallsAndShifts
from models.shift import Shift
from schemas.stall import StallEntity
from schemas.shift import ShiftEntity
from schemas.user import UserEntity
from bson.objectid import ObjectId
from .shifts import ShiftsServices

class StallsServices():
    def __init__(self, db: Database) -> None:
        self.db = db
        
    def createStall(self, company: str, stall: Stall, user: UserEntity) -> StallEntity:
        stall = dict(stall)
        del stall["id"]
        stall["company"] = company
        stall["userName"] = user["userName"]
        stall["updatedBy"] = user["userName"]
        stall["createdAt"] = datetime.datetime.now(pytz.timezone("America/Bogota")).strftime("%Y-%m-%d")
        stall["updatedAt"] = datetime.datetime.now(pytz.timezone("America/Bogota")).strftime("%Y-%m-%d")
        try:
            stall = self.db.stalls.insert_one(stall)
            stall = self.db.stalls.find_one({"_id": stall.inserted_id})
            return StallEntity(stall)
        except:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error creating stall.")
        
    def findStallsByMonthAndYear(self, company: str, monthAndYear: str) -> StallsAndShifts:
        stalls = self.db.stalls.find({"company": company, "monthAndYear": monthAndYear})
        shifts = []
        for stall in stalls:
            stallShifts = ShiftsServices(self.db).findShiftsByStall(company, str(stall["_id"]))
            if stallShifts:
                shifts += stallShifts
        if stalls:
            return StallsAndShifts(stalls=[StallEntity(stall) for stall in stalls], shifts=[ShiftEntity(shift) for shift in shifts])
        return None
    
    def finsStallsByCustomer(self, company: str, monthAndYear: str, customer: str) -> StallsAndShifts:
        stalls = self.db.stalls.find({"company": company, "monthAndYear": monthAndYear, "customer": customer})
        shifts = []
        for stall in stalls:
            stallShifts = ShiftsServices(self.db).findShiftsByStall(company, str(stall["_id"]))
            if stallShifts:
                shifts += stallShifts
        if stalls:
            return [StallEntity(stall) for stall in stalls]
        return None
    
    def updateStall(self, company: str, id: str, data: UpdateStall, user: UserEntity) -> StallEntity:
        stall = self.db.stalls.find_one({"_id": ObjectId(id)})
        if not stall:
            return None
        if stall["company"] != company:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized.")
        stall = dict(stall)
        data = dict(data)
        data["updatedAt"] = datetime.datetime.now(pytz.timezone("America/Bogota")).strftime("%Y-%m-%d")
        data["updatedBy"] = user["userName"]
        self.db.stalls.update_one({"_id": ObjectId(id)}, {"$set": data})
        stall = self.db.stalls.find_one({"_id": ObjectId(id)})
        return StallEntity(stall)
    
    async def deleteStall(self, company: str, id: str) -> StallsAndShifts:
        stall = self.db.stalls.find_one({"_id": ObjectId(id)})
        if not stall:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error deleting stall.")
        stall = dict(stall)
        if stall["company"] != company:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized.")
        try:
            await ShiftsServices(self.db).deleteShifts(company, id)
            self.db.stalls.delete_one({"_id": ObjectId(id)})
        except:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error deleting stall.")
        return StallEntity(stall)
    
    # Stall workers
    def addStallWorker(self, company: str, id: str, worker: StallWorker, user: UserEntity) -> StallEntity:
        worker = dict(worker)
        del worker["id"]
        stall = self.db.stalls.find_one({"_id": ObjectId(id)})
        if not stall:
            return None
        if stall["company"] != company:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized.")
        try:
            self.db.stalls.update_one({"_id": ObjectId(id)}, {"$push": {"workers": worker}})
            stall = self.db.stalls.find_one({"_id": ObjectId(id)})
        except:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error adding worker.")
        return StallEntity(stall)
    
    async def deleteStallWorker(self, company: str, id: str, workerId: str) -> StallEntity:
        stall = self.db.stalls.find_one({"_id": ObjectId(id)})
        if not stall:
            return None
        if stall["company"] != company:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized.")
        try:
            await ShiftsServices(self.db).deleteShiftsByWorkerAndStall(company, workerId, id)
            self.db.stalls.update_one({"_id": ObjectId(id)}, {"$pull": {"workers": {"id": workerId}}})
            stall = self.db.stalls.find_one({"_id": ObjectId(id)})
        except:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error deleting worker.")
        return StallEntity(stall)
    