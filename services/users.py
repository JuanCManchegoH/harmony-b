from services.companies import CompaniesServices
from models.user import UpdateUser, User
from models.user import Profile
from schemas.company import CompanyEntity
from pymongo.database import Database
from bson import ObjectId
from utils.errorsResponses import errors
from utils.auth import createAccessToken, getHashedPassword, verifyPassword
from typing import Optional, List

class UsersServices():
    def __init__(self, db: Database) -> None:
        self.db = db

    def getUser(self, id: str) -> Optional[User]:
        try:
            user = self.db.users.find_one({"_id": ObjectId(id)})
            return user or None
        except Exception as e:
            raise errors["Read error"] from e
        
    def getByEmail(self, email: str) -> Optional[User]:
        try:
            user = self.db.users.find_one({"email": email})
            return user or None
        except Exception as e:
            raise errors["Read error"] from e
    
    def authenticateUser(self, email: str, password: str) -> Optional[User]:
        try:
            user = self.getByEmail(email)
            if user is None or not verifyPassword(password, user["password"]):
                raise errors["Authentication error"]
            return user or None
        except Exception as e:
            raise errors["Authentication error"] from e

    def createUser(self, user: User) -> User:
        try:
            user_data = dict(user)
            del user_data["id"]
            # print("here")
            if self.getByEmail(user_data["email"]):
                raise errors["Creation error"]
            user_data["password"] = getHashedPassword(user_data["password"])
            insertion_result = self.db.users.insert_one(user_data)
            created_user = self.getUser(str(insertion_result.inserted_id))
            return created_user
        except Exception as e:
            raise errors["Creation error"] from e
      
    def login(self, email: str, password: str) -> dict:
        try:
            user = self.authenticateUser(email, password)
            user = dict(user)
            token = createAccessToken(data={"sub": user["email"], "roles": user["roles"]})
            return {"access_token": token, "token_type": "bearer"}
        except Exception as e:
            raise errors["Authentication error"] from e
    
    def getProfile(self, email: str) -> Profile:
        try: 
            user = self.getByEmail(email)
            company = CompaniesServices(self.db).getCompany(user["company"])
            user["company"] = CompanyEntity(company)
            return user
        except Exception as e:
            raise errors["Read error"] from e
        
    def getByCompany(self, company: str) -> List[User]:
        try:
            users = self.db.users.find({"company": company})
            return users or []
        except Exception as e:
            raise errors["Read error"] from e
    
    def update(self, user: UpdateUser, id: str) -> User:
        try:
            user = dict(user)
            self.db.users.update_one({"_id": ObjectId(id)}, {"$set": user})
            updated_user = self.getUser(id)
            return updated_user
        except:
            raise errors["Update error"]
        
    def delete(self, id: str) -> User:
        try:
            user = self.db.users.find_one({"_id": ObjectId(id)})
            self.db.users.delete_one({"_id": ObjectId(id)})
            return user
        except:
            raise errors["Deletion error"]