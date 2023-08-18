from models.company import Field
from schemas.company import CompanyEntity
from bson import ObjectId
from utils.errorsResponses import errors

class WFieldsServices():
    def __init__(self, db) -> None:
        self.db = db
    
    def addWField(self, id: str, field: Field) -> CompanyEntity:
        field = dict(field)
        field["id"] = str(ObjectId())
        if self.db.companies.find_one({"_id": ObjectId(id), "workerFields.name": field["name"]}):
            raise errors["Creation error"]
        if not self.db.companies.find_one({"_id": ObjectId(id)}):
            raise errors["Creation error"]
        try:
            self.db.companies.update_one({"_id": ObjectId(id)}, {"$push": {"workerFields": field}})
            company = self.db.companies.find_one({"_id": ObjectId(id)})
            return CompanyEntity(company)
        except:
            raise errors["Creation error"]
    
    def updateWField(self, id: str, fieldId: str, field: Field) -> CompanyEntity:
        field = dict(field)
        field["id"] = fieldId
        if not self.db.companies.find_one({"_id": ObjectId(id), "workerFields.id": fieldId}):
            raise errors["Update error"]
        try:  
            self.db.companies.update_one({"_id": ObjectId(id), "workerFields.id": fieldId}, {"$set": {"workerFields.$": field}})
            company = self.db.companies.find_one({"_id": ObjectId(id)})
            return CompanyEntity(company)
        except:
            raise errors["Update error"]
    
    def deleteWField(self, id: str, fieldId: str) -> CompanyEntity:
        if not self.db.companies.find_one({"_id": ObjectId(id), "workerFields.id": fieldId}):
            raise errors["Deletion error"]
        try: 
            self.db.companies.update_one({"_id": ObjectId(id)}, {"$pull": {"workerFields": {"id": fieldId}}})
            company = self.db.companies.find_one({"_id": ObjectId(id)})
            return CompanyEntity(company)
        except:
            raise errors["Deletion error"]