from models.company import Field
from schemas.company import CompanyEntity
from bson import ObjectId

class CFieldsServices():
    def __init__(self, db) -> None:
        self.db = db
        
    def addCField(self, id: str, field: Field) -> CompanyEntity:
        field = dict(field)
        field["id"] = str(ObjectId())
        self.db.companies.update_one({"_id": ObjectId(id)}, {"$push": {"customerFields": field}})
        company = self.db.companies.find_one({"_id": ObjectId(id)})
        return CompanyEntity(company)
    
    def updateCField(self, id: str, fieldId: str, field: Field) -> CompanyEntity:
        field = dict(field)
        field["id"] = fieldId
        if not self.db.companies.find_one({"_id": ObjectId(id), "customerFields.id": fieldId}):
            return None
        self.db.companies.update_one({"_id": ObjectId(id), "customerFields.id": fieldId}, {"$set": {"customerFields.$": field}})
        company = self.db.companies.find_one({"_id": ObjectId(id)})
        return CompanyEntity(company)
    
    def deleteCField(self, id: str, fieldId: str) -> CompanyEntity:
        if not self.db.companies.find_one({"_id": ObjectId(id), "customerFields.id": fieldId}):
            return None
        self.db.companies.update_one({"_id": ObjectId(id)}, {"$pull": {"customerFields": {"id": fieldId}}})
        company = self.db.companies.find_one({"_id": ObjectId(id)})
        return CompanyEntity(company)