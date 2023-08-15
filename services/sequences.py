from models.company import Sequence, Step
from schemas.company import CompanyEntity
from bson import ObjectId

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
        self.db.companies.update_one({"_id": ObjectId(id)}, {"$push": {"sequences": sequence}})
        company = self.db.companies.find_one({"_id": ObjectId(id)})
        return CompanyEntity(company)
    
    def updateSequence(self, id: str, sequenceId: str, sequence: Sequence) -> CompanyEntity:
        sequence = dict(sequence)
        steps = []
        for step in sequence["steps"]:
            steps.append(dict(step))
        sequence["steps"] = steps
        sequence["id"] = sequenceId
        if not self.db.companies.find_one({"_id": ObjectId(id), "sequences.id": sequenceId}):
            return None
        self.db.companies.update_one({"_id": ObjectId(id), "sequences.id": sequenceId}, {"$set": {"sequences.$": sequence}})
        company = self.db.companies.find_one({"_id": ObjectId(id)})
        return CompanyEntity(company)
    
    def deleteSequence(self, id: str, sequenceId: str) -> CompanyEntity:
        if not self.db.companies.find_one({"_id": ObjectId(id), "sequences.id": sequenceId}):
            return None
        self.db.companies.update_one({"_id": ObjectId(id)}, {"$pull": {"sequences": {"id": sequenceId}}})
        company = self.db.companies.find_one({"_id": ObjectId(id)})
        return CompanyEntity(company)