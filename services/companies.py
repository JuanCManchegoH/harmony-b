from pymongo.database import Database
from models.company import Company, UpdateCompany
from bson.objectid import ObjectId
from utils.errorsResponses import errors
from typing import Optional, List

class CompaniesServices(): 
    def __init__(self, db: Database) -> None:
        self.db = db
    
    def getCompany(self, id: str) -> Optional[Company]:
        try:
            company = self.db.companies.find_one({"_id": ObjectId(id)})
            return company or None
        except Exception as e:
            raise errors["Read error"] from e
    
    def createCompany(self, company: Company) -> Company:
        try:
            company = dict(company)
            del company["id"]
            if self.db.companies.find_one({"db": company["db"]}):
                raise errors["Creation error"]
            insertion_result = self.db.companies.insert_one(company)
            created_company = self.db.companies.find_one({"_id": insertion_result.inserted_id})
            return created_company
        except Exception as e:
            raise errors["Creation error"]
        
    def findAllCompanies(self) -> List[Company]:
        try:
            companies = self.db.companies.find()
            return companies or []
        except Exception as e:
            raise errors["Read error"] from e
        
    
    def updateCompany(self, id: str, company: UpdateCompany) -> Company:
        try:
            company = dict(company)
            if company["db"]:
                if self.db.companies.find_one({"db": company["db"]}):
                    raise errors["Update error"]
            del company["id"]
            self.db.companies.update_one({"_id": ObjectId(id)}, {"$set": company})
            company = self.getCompany(id)
            return company
        except:
            raise errors["Update error"]
    
    def deleteCompany(self, id: str) -> Company:
        try:
            company = self.getCompany(id)
            if not company:
                raise errors["Deletion error"]
            self.db.companies.delete_one({"_id": ObjectId(id)})
            return company
        except :
            raise errors["Deletion error"]