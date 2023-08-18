from models.company import Position
from schemas.company import CompanyEntity
from bson.objectid import ObjectId
from utils.errorsResponses import errors

class PositionsServices():
    def __init__(self, db) -> None:
        self.db = db
        
    def addPosition(self, id: str, position: Position) -> CompanyEntity:
        position = dict(position)
        position["id"] = str(ObjectId())
        if self.db.companies.find_one({"_id": ObjectId(id), "positions.name": position["name"]}):
            raise errors["Creation error"]
        if not self.db.companies.find_one({"_id": ObjectId(id)}):
            raise errors["Creation error"]
        try:
            self.db.companies.update_one({"_id": ObjectId(id)}, {"$push": {"positions": position}})
            company = self.db.companies.find_one({"_id": ObjectId(id)})
            return CompanyEntity(company)
        except:
            raise errors["Creation error"]
    
    def updatePosition(self, id: str, positionId: str, position: Position) -> CompanyEntity:
        position = dict(position)
        position["id"] = positionId
        if not self.db.companies.find_one({"_id": ObjectId(id), "positions.id": positionId}):
            raise errors["Update error"]
        try: 
            self.db.companies.update_one({"_id": ObjectId(id), "positions.id": positionId}, {"$set": {"positions.$": position}})
            company = self.db.companies.find_one({"_id": ObjectId(id)})
            return CompanyEntity(company)
        except:
            raise errors["Update error"]
    
    def deletePosition(self, id: str, positionId: str) -> CompanyEntity:
        if not self.db.companies.find_one({"_id": ObjectId(id), "positions.id": positionId}):
            raise errors["Deletion error"]
        try: 
            self.db.companies.update_one({"_id": ObjectId(id)}, {"$pull": {"positions": {"id": positionId}}})
            company = self.db.companies.find_one({"_id": ObjectId(id)})
            return CompanyEntity(company)
        except:
            raise errors["Deletion error"]