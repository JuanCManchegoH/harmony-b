from .companies import CompaniesServices
from models.company import Sequence, Company
from pymongo.database import Database
from bson import ObjectId
from utils.errorsResponses import errors

class SequencesServices():
    def __init__(self, db: Database) -> None:
        self.db = db
    
    def addSequence(self, id: str, sequence: Sequence) -> Company:
        try:
            sequence = dict(sequence)
            steps = []
            for step in sequence["steps"]:
                steps.append(dict(step))
            sequence["steps"] = steps
            sequence["id"] = str(ObjectId())
            if self.db.companies.find_one({"_id": ObjectId(id), "sequences.name": sequence["name"]}):
                raise errors["Creation error"]
            self.db.companies.update_one({"_id": ObjectId(id)}, {"$push": {"sequences": sequence}})
            company = CompaniesServices(self.db).getCompany(id)
            return company
        except Exception as e:
            raise errors["Creation error"] from e
    
    def updateSequence(self, id: str, sequenceId: str, sequence: Sequence) -> Company:
        try:
            sequence = dict(sequence)
            steps = []
            for step in sequence["steps"]:
                steps.append(dict(step))
            sequence["steps"] = steps
            sequence["id"] = sequenceId
            self.db.companies.update_one({"_id": ObjectId(id), "sequences.id": sequenceId}, {"$set": {"sequences.$": sequence}})
            company = CompaniesServices(self.db).getCompany(id)
            return company
        except Exception as e:
            raise errors["Update error"] from e
    
    def deleteSequence(self, id: str, sequenceId: str) -> Company:
        try:
            self.db.companies.update_one({"_id": ObjectId(id)}, {"$pull": {"sequences": {"id": sequenceId}}})
            company = CompaniesServices(self.db).getCompany(id)
            return company
        except Exception as e:
            raise errors["Deletion error"] from e