from models.company import Position
from schemas.company import CompanyEntity
from bson.objectid import ObjectId

class PositionsServices():
    def __init__(self, db) -> None:
        self.db = db
        
    def addPosition(self, id: str, position: Position) -> CompanyEntity:
        position = dict(position)
        position["id"] = str(ObjectId())
        self.db.companies.update_one({"_id": ObjectId(id)}, {"$push": {"positions": position}})
        company = self.db.companies.find_one({"_id": ObjectId(id)})
        return CompanyEntity(company)
    
    def updatePosition(self, id: str, positionId: str, position: Position) -> CompanyEntity:
        position = dict(position)
        position["id"] = positionId
        if not self.db.companies.find_one({"_id": ObjectId(id), "positions.id": positionId}):
            return None
        self.db.companies.update_one({"_id": ObjectId(id), "positions.id": positionId}, {"$set": {"positions.$": position}})
        company = self.db.companies.find_one({"_id": ObjectId(id)})
        return CompanyEntity(company)
    
    def deletePosition(self, id: str, positionId: str) -> CompanyEntity:
        if not self.db.companies.find_one({"_id": ObjectId(id), "positions.id": positionId}):
            return None
        self.db.companies.update_one({"_id": ObjectId(id)}, {"$pull": {"positions": {"id": positionId}}})
        company = self.db.companies.find_one({"_id": ObjectId(id)})
        return CompanyEntity(company)