from .companies import CompaniesServices
from models.company import Company, Field
from pymongo.database import Database
from bson import ObjectId
from utils.errorsResponses import errors

class CFieldsServices():
    def __init__(self, db: Database) -> None:
        self.db = db
        
    def addCField(self, id: str, field: Field) -> Company:
        try:
            field = dict(field)
            field["id"] = str(ObjectId())
            if self.db.companies.find_one({"_id": ObjectId(id), "customerFields.name": field["name"]}):
                raise errors["Creation error"]
            self.db.companies.update_one({"_id": ObjectId(id)}, {"$push": {"customerFields": field}})
            company = CompaniesServices(self.db).getCompany(id)
            return company
        except Exception as e:
            raise errors["Creation error"] from e
    
    def updateCField(self, id: str, fieldId: str, field: Field) -> Company:
        try:
            field = dict(field)
            field["id"] = fieldId
            self.db.companies.update_one({"_id": ObjectId(id), "customerFields.id": fieldId}, {"$set": {"customerFields.$": field}})
            company = CompaniesServices(self.db).getCompany(id)
            return company
        except Exception as e:
            raise errors["Update error"] from e
    
    def deleteCField(self, id: str, fieldId: str) -> Company:
        try:
            self.db.companies.update_one({"_id": ObjectId(id)}, {"$pull": {"customerFields": {"id": fieldId}}})
            company = CompaniesServices(self.db).getCompany(id)
            return company
        except Exception as e:
            raise errors["Deletion error"] from e
        