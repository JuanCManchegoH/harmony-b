from models.company import Convention
from schemas.company import CompanyEntity
from bson import ObjectId
from utils.errorsResponses import errors

class ConventionsServices():
    def __init__(self, db) -> None:
        self.db = db
    
    def addConvention(self, id: str, convention: Convention) -> CompanyEntity:
        convention = dict(convention)
        convention["id"] = str(ObjectId())
        if self.db.companies.find_one({"_id": ObjectId(id), "conventions.name": convention["name"]}):
            raise errors["Creation error"]
        if not self.db.companies.find_one({"_id": ObjectId(id)}):
            raise errors["Creation error"]
        try:
            self.db.companies.update_one({"_id": ObjectId(id)}, {"$push": {"conventions": convention}})
            company = self.db.companies.find_one({"_id": ObjectId(id)})
            return CompanyEntity(company)
        except:
            raise errors["Creation error"]
    
    def updateConvention(self, id: str, conventionId: str, convention: Convention) -> CompanyEntity:
        convention = dict(convention)
        convention["id"] = conventionId
        if not self.db.companies.find_one({"_id": ObjectId(id), "conventions.id": conventionId}):
            raise errors["Update error"]
        try:
            self.db.companies.update_one({"_id": ObjectId(id), "conventions.id": conventionId}, {"$set": {"conventions.$": convention}})
            company = self.db.companies.find_one({"_id": ObjectId(id)})
            return CompanyEntity(company)
        except:
            raise errors["Update error"]
    
    def deleteConvention(self, id: str, conventionId: str) -> CompanyEntity:
        if not self.db.companies.find_one({"_id": ObjectId(id), "conventions.id": conventionId}):
            raise errors["Deletion error"]
        try: 
            self.db.companies.update_one({"_id": ObjectId(id)}, {"$pull": {"conventions": {"id": conventionId}}})
            company = self.db.companies.find_one({"_id": ObjectId(id)})
            return CompanyEntity(company)
        except:
            raise errors["Deletion error"]