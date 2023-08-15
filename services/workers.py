import datetime
import pytz
from fastapi import HTTPException, status
from pymongo.database import Database
from models.worker import Worker, UpdateWorker
from schemas.worker import WorkerEntity
from schemas.user import UserEntity
from bson.objectid import ObjectId

class WorkersServices():
    def __init__(self, db: Database) -> None:
        self.db = db
        
    def createWorker(self, company: str, worker: Worker, user: UserEntity) -> WorkerEntity:
        worker = dict(worker)
        del worker["id"]
        worker["company"] = company
        if self.db.workers.find_one({"identification": worker["identification"]}):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Worker already exists.")
        worker["userName"] = user["userName"]
        worker["updatedBy"] = user["userName"]
        worker["createdAt"] = datetime.datetime.now(pytz.timezone("America/Bogota")).strftime("%Y-%m-%d")
        worker["updatedAt"] = datetime.datetime.now(pytz.timezone("America/Bogota")).strftime("%Y-%m-%d")
        try:
            worker = self.db.workers.insert_one(worker)
            worker = self.db.workers.find_one({"_id": worker.inserted_id})
            return WorkerEntity(worker)
        except:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error creating worker.")
        
    def findWorkersByNameOrIdentification(self, company: str, search: str, limit: int, skip: int) -> list:
        workers = self.db.workers.find({"company": company, "$or": [{"name": {"$regex": search, "$options": "i"}}, {"identification": {"$regex": search, "$options": "i"}}]}).limit(limit).skip(skip)
        if workers:
            return [WorkerEntity(worker) for worker in workers]
        return None
    
    def updateWorker(self, company: str, id: str, data: UpdateWorker, user: UserEntity) -> WorkerEntity:
        worker = self.db.workers.find_one({"_id": ObjectId(id)})
        if not worker:
            return None
        if worker["company"] != company:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized.")
        worker = dict(worker)
        data = dict(data)
        data["updatedAt"] = datetime.datetime.now(pytz.timezone("America/Bogota")).strftime("%Y-%m-%d")
        data["updatedBy"] = user["userName"]
        self.db.workers.update_one({"_id": ObjectId(id)}, {"$set": data})
        worker = self.db.workers.find_one({"_id": ObjectId(id)})
        return WorkerEntity(worker)
    
    def deleteWorker(self, company: str, id: str) -> WorkerEntity:
        worker = self.db.workers.find_one({"_id": ObjectId(id)})
        if not worker:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error deleting worker.")
        worker = dict(worker)
        if worker["company"] != company:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized.")
        try:
            self.db.workers.delete_one({"_id": ObjectId(id)})
        except:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error deleting worker.")
        return WorkerEntity(worker)
    