from models.company import Field
from schemas.company import CompanyEntity
from bson import ObjectId
from utils.errorsResponses import errors


class CFieldsServices():
    def __init__(self, db) -> None:
        self.db = db
        
    def addCField(self, id: str, field: Field) -> CompanyEntity:
        field = dict(field)
        field["id"] = str(ObjectId())
        if self.db.companies.find_one({"_id": ObjectId(id), "customerFields.name": field["name"]}):
            raise errors["Creation error"]
        if not self.db.companies.find_one({"_id": ObjectId(id)}):
            raise errors["Creation error"]
        try:
            self.db.companies.update_one({"_id": ObjectId(id)}, {"$push": {"customerFields": field}})
            company = self.db.companies.find_one({"_id": ObjectId(id)})
            return CompanyEntity(company)
        except:
            raise errors["Creation error"]
    
    def updateCField(self, id: str, fieldId: str, field: Field) -> CompanyEntity:
        field = dict(field)
        field["id"] = fieldId
        if not self.db.companies.find_one({"_id": ObjectId(id), "customerFields.id": fieldId}):
            raise errors["Update error"]
        try:
            self.db.companies.update_one({"_id": ObjectId(id), "customerFields.id": fieldId}, {"$set": {"customerFields.$": field}})
            company = self.db.companies.find_one({"_id": ObjectId(id)})
            return CompanyEntity(company)
        except:
            raise errors["Update error"]
    
    def deleteCField(self, id: str, fieldId: str) -> CompanyEntity:
        if not self.db.companies.find_one({"_id": ObjectId(id), "customerFields.id": fieldId}):
            raise errors["Deletion error"]
        try:
            self.db.companies.update_one({"_id": ObjectId(id)}, {"$pull": {"customerFields": {"id": fieldId}}})
            company = self.db.companies.find_one({"_id": ObjectId(id)})
            return CompanyEntity(company)
        except:
            raise errors["Deletion error"]