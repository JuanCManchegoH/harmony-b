from models.company import Sequence
from schemas.company import CompanyEntity
from bson import ObjectId
from utils.errorsResponses import errors

class SequencesServices():
    def __init__(self, db) -> None:
        self.db = db
    
    def addSequence(self, id: str, sequence: Sequence) -> CompanyEntity:
        sequence = dict(sequence)
        steps = []
        for step in sequence["steps"]:
            steps.append(dict(step))
        sequence["steps"] = steps
        sequence["id"] = str(ObjectId())
        if self.db.companies.find_one({"_id": ObjectId(id), "sequences.name": sequence["name"]}):
            raise errors["Creation error"]
        if not self.db.companies.find_one({"_id": ObjectId(id)}):
            raise errors["Creation error"]
        try:
            self.db.companies.update_one({"_id": ObjectId(id)}, {"$push": {"sequences": sequence}})
            company = self.db.companies.find_one({"_id": ObjectId(id)})
            return CompanyEntity(company)
        except:
            raise errors["Creation error"]
    
    def updateSequence(self, id: str, sequenceId: str, sequence: Sequence) -> CompanyEntity:
        sequence = dict(sequence)
        steps = []
        for step in sequence["steps"]:
            steps.append(dict(step))
        sequence["steps"] = steps
        sequence["id"] = sequenceId
        if not self.db.companies.find_one({"_id": ObjectId(id), "sequences.id": sequenceId}):
            raise errors["Update error"]
        try:
            self.db.companies.update_one({"_id": ObjectId(id), "sequences.id": sequenceId}, {"$set": {"sequences.$": sequence}})
            company = self.db.companies.find_one({"_id": ObjectId(id)})
            return CompanyEntity(company)
        except:
            raise errors["Update error"]
    
    def deleteSequence(self, id: str, sequenceId: str) -> CompanyEntity:
        if not self.db.companies.find_one({"_id": ObjectId(id), "sequences.id": sequenceId}):
            raise errors["Deletion error"]
        try:
            self.db.companies.update_one({"_id": ObjectId(id)}, {"$pull": {"sequences": {"id": sequenceId}}})
            company = self.db.companies.find_one({"_id": ObjectId(id)})
            return CompanyEntity(company)
        except:
            raise errors["Deletion error"]