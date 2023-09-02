from .companies import CompaniesServices
from models.company import Convention, Company
from pymongo.database import Database
from bson import ObjectId
from utils.errorsResponses import errors

class ConventionsServices():
    def __init__(self, db: Database) -> None:
        self.db = db
    
    def addConvention(self, id: str, convention: Convention) -> Company:
        try:
            convention = dict(convention)
            convention["id"] = str(ObjectId())
            if self.db.companies.find_one({"_id": ObjectId(id), "conventions.name": convention["name"]}):
                raise errors["Creation error"]
            self.db.companies.update_one({"_id": ObjectId(id)}, {"$push": {"conventions": convention}})
            company = CompaniesServices(self.db).getCompany(id)
            return company
        except Exception as e:
            raise errors["Creation error"] from e
    
    def updateConvention(self, id: str, conventionId: str, convention: Convention) -> Company:
        try:
            convention = dict(convention)
            convention["id"] = conventionId
            self.db.companies.update_one({"_id": ObjectId(id), "conventions.id": conventionId}, {"$set": {"conventions.$": convention}})
            company = CompaniesServices(self.db).getCompany(id)
            return company
        except Exception as e:
            raise errors["Update error"] from e
    
    def deleteConvention(self, id: str, conventionId: str) -> Company:
        try: 
            self.db.companies.update_one({"_id": ObjectId(id)}, {"$pull": {"conventions": {"id": conventionId}}})
            company = CompaniesServices(self.db).getCompany(id)
            return company
        except Exception as e:
            raise errors["Deletion error"] from e