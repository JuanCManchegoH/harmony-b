from .companies import CompaniesServices
from models.company import Field, Company
from pymongo.database import Database
from bson import ObjectId
from utils.errorsResponses import errors

class WFieldsServices():
    def __init__(self, db: Database) -> None:
        self.db = db
    
    def addWField(self, id: str, field: Field) -> Company:
        try:
            field = dict(field)
            field["id"] = str(ObjectId())
            if self.db.companies.find_one({"_id": ObjectId(id), "workerFields.name": field["name"]}):
                raise errors["Creation error"]
            self.db.companies.update_one({"_id": ObjectId(id)}, {"$push": {"workerFields": field}})
            company = CompaniesServices(self.db).getCompany(id)
            return company
        except Exception as e:
            raise errors["Creation error"] from e
    
    def updateWField(self, id: str, fieldId: str, field: Field) -> Company:
        try:  
            field = dict(field)
            field["id"] = fieldId
            self.db.companies.update_one({"_id": ObjectId(id), "workerFields.id": fieldId}, {"$set": {"workerFields.$": field}})
            company = CompaniesServices(self.db).getCompany(id)
            return company
        except Exception as e:
            raise errors["Update error"] from e
    
    def deleteWField(self, id: str, fieldId: str) -> Company:
        try: 
            self.db.companies.update_one({"_id": ObjectId(id)}, {"$pull": {"workerFields": {"id": fieldId}}})
            company = CompaniesServices(self.db).getCompany(id)
            return company
        except Exception as e:
            raise errors["Deletion error"] from e
        