from .companies import CompaniesServices
from models.company import Position, Company
from pymongo.database import Database
from bson import ObjectId
from utils.errorsResponses import errors

class PositionsServices():
    def __init__(self, db: Database) -> None:
        self.db = db
        
    def addPosition(self, id: str, position: Position) -> Company:
        try:
            position = dict(position)
            position["id"] = str(ObjectId())
            if self.db.companies.find_one({"_id": ObjectId(id), "positions.name": position["name"]}):
                raise errors["Creation error"]
            self.db.companies.update_one({"_id": ObjectId(id)}, {"$push": {"positions": position}})
            company = CompaniesServices(self.db).getCompany(id)
            return company
        except Exception as e:
            raise errors["Creation error"] from e
    
    def updatePosition(self, id: str, positionId: str, position: Position) -> Company:
        try: 
            position = dict(position)
            position["id"] = positionId
            self.db.companies.update_one({"_id": ObjectId(id), "positions.id": positionId}, {"$set": {"positions.$": position}})
            company = CompaniesServices(self.db).getCompany(id)
            return company
        except Exception as e:
            raise errors["Update error"] from e
    
    def deletePosition(self, id: str, positionId: str) -> Company:
        try: 
            self.db.companies.update_one({"_id": ObjectId(id)}, {"$pull": {"positions": {"id": positionId}}})
            company = CompaniesServices(self.db).getCompany(id)
            return company
        except Exception as e:
            raise errors["Deletion error"] from e
        