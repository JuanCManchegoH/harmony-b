from models.user import UpdateUser, User
from schemas.user import UserEntity
from utils.auth import createAccessToken, getHashedPassword
from bson.objectid import ObjectId
from services.companies import CompaniesServices
from utils.errorsResponses import errors

class UsersServices():
    def __init__(self, db) -> None:
        self.db = db

    def createUser(self, user: User) -> UserEntity:
        user = dict(user)
        del user["id"]
        user["password"] = getHashedPassword(user["password"])
        if self.db.users.find_one({"email": user["email"]}):
            raise errors["Creation error"]
        try:
            user = self.db.users.insert_one(user)
            user = self.db.users.find_one({"_id": user.inserted_id})
            return UserEntity(user)
        except:
            raise errors["Creation error"]
        
    def login(self, user: dict) -> dict:
        try:
            token = createAccessToken(data={"sub": user["email"], "roles": user["roles"]})
            return {"access_token": token, "token_type": "bearer"}
        except:
            raise errors["Creation error"]
    
    def getByEmail(self, email: str) -> UserEntity:
        try:
            user = self.db.users.find_one({"email": email})
            if user:
                return UserEntity(user)
        except:
            return UserEntity({})
    
    def getProfile(self, email: str) -> UserEntity:
        try:
            user = self.db.users.find_one({"email": email})
            company = CompaniesServices(self.db).findCompany(user["company"])
            if user:
                profile = UserEntity(user)
                profile["company"] = company
                return profile
        except:
            return UserEntity({})
        
    def getByCompany(self, company: str) -> list:
        try:
            users = self.db.users.find({"company": company})
            if users:
                return [UserEntity(user) for user in users]
        except:
            return []
    
    def update(self, user: UpdateUser, id: str) -> UserEntity:
        user = dict(user)
        try:
            self.db.users.update_one({"_id": ObjectId(id)}, {"$set": user})
            return UserEntity(self.db.users.find_one({"_id": ObjectId(id)}))
        except:
            raise errors["Update error"]
        
    def delete(self, id: str) -> UserEntity:
        user = self.db.users.find_one({"_id": ObjectId(id)})
        if not user:
            raise errors["Deletion error"]
        try:
            self.db.users.delete_one({"_id": ObjectId(id)})
            return UserEntity(user)
        except:
            raise errors["Deletion error"]