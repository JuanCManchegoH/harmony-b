from models.company import Convention
from schemas.company import CompanyEntity
from bson import ObjectId

class ConventionsServices():
    def __init__(self, db) -> None:
        self.db = db
    
    def addConvention(self, id: str, convention: Convention) -> CompanyEntity:
        convention = dict(convention)
        convention["id"] = str(ObjectId())
        self.db.companies.update_one({"_id": ObjectId(id)}, {"$push": {"conventions": convention}})
        company = self.db.companies.find_one({"_id": ObjectId(id)})
        return CompanyEntity(company)
    
    def updateConvention(self, id: str, conventionId: str, convention: Convention) -> CompanyEntity:
        convention = dict(convention)
        convention["id"] = conventionId
        if not self.db.companies.find_one({"_id": ObjectId(id), "conventions.id": conventionId}):
            return None
        self.db.companies.update_one({"_id": ObjectId(id), "conventions.id": conventionId}, {"$set": {"conventions.$": convention}})
        company = self.db.companies.find_one({"_id": ObjectId(id)})
        return CompanyEntity(company)
    
    def deleteConvention(self, id: str, conventionId: str) -> CompanyEntity:
        if not self.db.companies.find_one({"_id": ObjectId(id), "conventions.id": conventionId}):
            return None
        self.db.companies.update_one({"_id": ObjectId(id)}, {"$pull": {"conventions": {"id": conventionId}}})
        company = self.db.companies.find_one({"_id": ObjectId(id)})
        return CompanyEntity(company)