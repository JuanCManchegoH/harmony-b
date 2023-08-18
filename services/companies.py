from pymongo.database import Database
from models.company import Company, UpdateCompany
from schemas.company import CompanyEntity
from bson.objectid import ObjectId
from utils.errorsResponses import errors
from typing import List

class CompaniesServices(): 
    def __init__(self, db: Database) -> None:
        self.db = db
    
    def createCompany(self, company: Company) -> CompanyEntity:
        company = dict(company)
        del company["id"]
        if self.db.companies.find_one({"db": company["db"]}):
            raise errors["Creation error"]
        try:
            company = self.db.companies.insert_one(company)
            company = self.db.companies.find_one({"_id": company.inserted_id})
            return CompanyEntity(company)
        except:
            raise errors["Creation error"]
        
    def findCompany(self, id: str) -> CompanyEntity:
        company = self.db.companies.find_one({"_id": ObjectId(id)})
        if company:
            return CompanyEntity(company)
        return CompanyEntity({})
    
    def findAllCompanies(self) -> List[CompanyEntity]:
        companies = self.db.companies.find()
        if companies:
            return [CompanyEntity(company) for company in companies]
        return []
    
    def updateCompany(self, id: str, company: UpdateCompany) -> CompanyEntity:
        company = dict(company)
        if company["db"]:
            if self.db.companies.find_one({"db": company["db"]}):
                raise errors["Update error"]
        del company["id"]
        try:
            self.db.companies.update_one({"_id": ObjectId(id)}, {"$set": company})
            company = self.db.companies.find_one({"_id": ObjectId(id)})
            return CompanyEntity(company)
        except:
            raise errors["Update error"]
    
    def deleteCompany(self, id: str) -> CompanyEntity:
        try:
            company = self.db.companies.find_one({"_id": ObjectId(id)})
            if not company:
                raise errors["Deletion error"]
            self.db.companies.delete_one({"_id": ObjectId(id)})
            return CompanyEntity(company)
        except :
            raise errors["Deletion error"]