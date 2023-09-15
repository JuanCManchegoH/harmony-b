import pytz
import datetime
from models.worker import Worker, UpdateWorker
from schemas.user import UserEntity
from bson.objectid import ObjectId
from pymongo.database import Database
from bson import ObjectId
from utils.errorsResponses import errors
from typing import List

class WorkersServices():
    def __init__(self, db: Database) -> None:
        self.db = db
        
    def createWorker(self, company: str, worker: Worker, user: UserEntity) -> Worker:
        try:
            worker = dict(worker)
            del worker["id"]
            worker["company"] = company
            if self.db.workers.find_one({"identification": worker["identification"]}):
                raise errors["Creation error"]
            worker["userName"] = user["userName"]
            worker["updatedBy"] = user["userName"]
            worker["createdAt"] = datetime.datetime.now(pytz.timezone("America/Bogota")).strftime("%d/%m/%Y %H:%M")
            worker["updatedAt"] = datetime.datetime.now(pytz.timezone("America/Bogota")).strftime("%d/%m/%Y %H:%M")
            fields = []
            for field in worker["fields"]:
                fields.append(dict(field))
            worker["fields"] = fields
            worker = self.db.workers.insert_one(worker)
            worker = self.db.workers.find_one({"_id": worker.inserted_id})
            return worker
        except Exception as e:
            raise errors["Creation error"] from e
        
    def findWorkerById(self, company: str, id: str) -> Worker:
        try:
            worker = self.db.workers.find_one({"_id": ObjectId(id)})
            if not worker:
                return errors["Read error"]
            if worker["company"] != company:
                raise errors["Unauthorized"]
            return worker
        except Exception as e:
            raise errors["Read error"] from e
        
    def findWorkersByNameOrIdentification(self, company: str, search: str, limit: int, skip: int, userTags: list) -> List[Worker]:
        try:
            if "all" in userTags:
                workers = self.db.workers.find({"company": company, "$or": [{"name": {"$regex": search, "$options": "i"}}, {"identification": {"$regex": search, "$options": "i"}}]}).limit(limit).skip(skip)
                return workers or []
            workers = self.db.workers.find({"company": company, "tags": {"$in": userTags}, "$or": [{"name": {"$regex": search, "$options": "i"}}, {"identification": {"$regex": search, "$options": "i"}}]}).limit(limit).skip(skip)
            return workers or []
        except Exception as e:
            raise errors["Read error"] from e
        
    def findWorkersByAnArray(self, company: str, ids: List[str]) -> List[Worker]:
        try:
            workers = self.db.workers.find({"company": company, "_id": {"$in": [ObjectId(id) for id in ids]}})
            return workers or []
        except Exception as e:
            raise errors["Read error"] from e
    
    def updateWorker(self, company: str, id: str, data: UpdateWorker, user: UserEntity) -> Worker:
        try:
            worker = self.db.workers.find_one({"_id": ObjectId(id)})
            if not worker:
                return errors["Update error"]
            if worker["company"] != company:
                raise errors["Unauthorized"]
            worker = dict(worker)
            userTags = user["workers"]
            if not set(worker["tags"]).intersection(userTags) and "all" not in userTags:
                raise errors["Update error"]
            data = dict(data)
            fields = []
            for field in data["fields"]:
                fields.append(dict(field))
            data["fields"] = fields
            data["updatedAt"] = datetime.datetime.now(pytz.timezone("America/Bogota")).strftime("%d/%m/%Y %H:%M")
            data["updatedBy"] = user["userName"]
            self.db.workers.update_one({"_id": ObjectId(id)}, {"$set": data})
            worker = self.db.workers.find_one({"_id": ObjectId(id)})
            return worker
        except Exception as e:
            raise errors["Update error"] from e
    
    def deleteWorker(self, company: str, id: str, userTags: list) -> Worker:
        try:
            worker = self.db.workers.find_one({"_id": ObjectId(id)})
            if not worker:
                raise errors["Deletion error"]
            worker = dict(worker)
            if not set(worker["tags"]).intersection(userTags) and "all" not in userTags:
                raise errors["Unauthorized"]
            if worker["company"] != company:
                raise errors["Unauthorized"]
            self.db.workers.delete_one({"_id": ObjectId(id)})
            return worker
        except Exception as e:
            raise errors["Deletion error"] from e
    