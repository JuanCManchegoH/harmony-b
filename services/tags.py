from models.company import Tag
from schemas.company import CompanyEntity
from bson import ObjectId

class TagsServices():
    def __init__(self, db) -> None:
        self.db = db
    
    def addTag(self, id: str, tag: Tag) -> CompanyEntity:
        tag = dict(tag)
        tag["id"] = str(ObjectId())
        self.db.companies.update_one({"_id": ObjectId(id)}, {"$push": {"tags": tag}})
        company = self.db.companies.find_one({"_id": ObjectId(id)})
        return CompanyEntity(company)
    
    def updateTag(self, id: str, tagId: str, tag: Tag) -> CompanyEntity:
        tag = dict(tag)
        tag["id"] = tagId
        if not self.db.companies.find_one({"_id": ObjectId(id), "tags.id": tagId}):
            return None
        self.db.companies.update_one({"_id": ObjectId(id), "tags.id": tagId}, {"$set": {"tags.$": tag}})
        company = self.db.companies.find_one({"_id": ObjectId(id)})
        return CompanyEntity(company)
    
    def deleteTag(self, id: str, tagId: str) -> CompanyEntity:
        if not self.db.companies.find_one({"_id": ObjectId(id), "tags.id": tagId}):
            return None
        self.db.companies.update_one({"_id": ObjectId(id)}, {"$pull": {"tags": {"id": tagId}}})
        company = self.db.companies.find_one({"_id": ObjectId(id)})
        return CompanyEntity(company)