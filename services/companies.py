from fastapi import HTTPException, status
from pymongo.database import Database
from models.company import Company, UpdateCompany
from schemas.company import CompanyEntity
from bson.objectid import ObjectId

class CompaniesServices(): 
    def __init__(self, db: Database) -> None:
        self.db = db
    
    def createCompany(self, company: Company) -> CompanyEntity:
        company = dict(company)
        del company["id"]
        if self.db.companies.find_one({"db": company["db"]}):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Company already exists.")
        try:
            company = self.db.companies.insert_one(company)
            company = self.db.companies.find_one({"_id": company.inserted_id})
            return CompanyEntity(company)
        except:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error creating company.")
        
    def findCompany(self, id: str) -> CompanyEntity:
        company = self.db.companies.find_one({"_id": ObjectId(id)})
        if company:
            return CompanyEntity(company)
        return None
    
    def findAllCompanies(self) -> list:
        companies = self.db.companies.find()
        if companies:
            return [CompanyEntity(company) for company in companies]
        return None
    
    def updateCompany(self, id: str, company: UpdateCompany) -> CompanyEntity:
        company = dict(company)
        self.db.companies.update_one({"_id": ObjectId(id)}, {"$set": company})
        company = self.db.companies.find_one({"_id": ObjectId(id)})
        return CompanyEntity(company)
    
    def deleteCompany(self, id: str) -> bool:
        try:
            self.db.companies.delete_one({"_id": ObjectId(id)})
            return True
        except:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error deleting company.")