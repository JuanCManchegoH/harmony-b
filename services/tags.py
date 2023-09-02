from .companies import CompaniesServices
from models.company import Tag, Company
from pymongo.database import Database
from bson import ObjectId
from utils.errorsResponses import errors

class TagsServices():
    def __init__(self, db: Database) -> None:
        self.db = db
    
    def addTag(self, id: str, tag: Tag) -> Company:
        try:
            tag = dict(tag)
            tag["id"] = str(ObjectId())
            if self.db.companies.find_one({"_id": ObjectId(id), "tags.name": tag["name"], "tags.scope": tag["scope"]}):
                raise errors["Creation error"]
            self.db.companies.update_one({"_id": ObjectId(id)}, {"$push": {"tags": tag}})
            company = CompaniesServices(self.db).getCompany(id)
            return company
        except Exception as e:
            raise errors["Creation error"] from e
    
    def updateTag(self, id: str, tagId: str, tag: Tag) -> Company:
        try:
            tag = dict(tag)
            tag["id"] = tagId
            self.db.companies.update_one({"_id": ObjectId(id), "tags.id": tagId}, {"$set": {"tags.$": tag}})
            company = CompaniesServices(self.db).getCompany(id)
            return company
        except Exception as e:
            raise errors["Update error"] from e
    
    def deleteTag(self, id: str, tagId: str) -> Company:
        try:
            self.db.companies.update_one({"_id": ObjectId(id)}, {"$pull": {"tags": {"id": tagId}}})
            company = CompaniesServices(self.db).getCompany(id)
            return company
        except Exception as e:
            raise errors["Update error"] from e
        