from fastapi import HTTPException, status
from models.user import UpdateUser, User
from schemas.user import UserEntity, ProfileEntity
from utils.auth import createAccessToken, getHashedPassword
from bson.objectid import ObjectId
from services.companies import CompaniesServices

class UsersServices():
    def __init__(self, db) -> None:
        self.db = db

    def createUser(self, user: User) -> UserEntity:
        user = dict(user)
        del user["id"]
        user["password"] = getHashedPassword(user["password"])
        try:
            user = self.db.users.insert_one(user)
            user = self.db.users.find_one({"_id": user.inserted_id})
            return UserEntity(user)
        except:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error creating user.")
        
    def login(self, user: dict) -> dict:
        token = createAccessToken(data={"sub": user["email"], "roles": user["roles"]})
        return {"access_token": token, "token_type": "bearer"}
    
    def getByEmail(self, email: str) -> UserEntity:
        user = self.db.users.find_one({"email": email})
        if user:
            return UserEntity(user)
        return None
    
    def getProfile(self, email: str) -> ProfileEntity:
        user = self.db.users.find_one({"email": email})
        company = CompaniesServices(self.db).findCompany(user["company"])
        if user:
            profile = ProfileEntity(user)
            profile["company"] = company
            return profile
        return None
        
    def getByCompany(self, company: str) -> list:
        users = self.db.users.find({"company": company})
        if users:
            return [UserEntity(user) for user in users]
        return None
    
    def update(self, user: UpdateUser, id: str) -> UserEntity:
        user = dict(user)
        try:
            self.db.users.update_one({"_id": ObjectId(id)}, {"$set": user})
            return UserEntity(self.db.users.find_one({"_id": ObjectId(id)}))
        except:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error updating user.")
        
    def updateRoles(self, roles: list, id: str) -> UserEntity:
        try:
            self.db.users.update_one({"_id": ObjectId(id)}, {"$set": {"roles": roles}})
            return UserEntity(self.db.users.find_one({"_id": ObjectId(id)}))
        except:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error updating user roles.")
        
    def updateCustomers(self, customers: list, id: str) -> UserEntity:
        try:
            self.db.users.update_one({"_id": ObjectId(id)}, {"$set": {"customers": customers}})
            return UserEntity(self.db.users.find_one({"_id": ObjectId(id)}))
        except:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error updating user customers.")
        
    def delete(self, id: str) -> UserEntity:
        user = self.db.users.find_one({"_id": ObjectId(id)})
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
        try:
            self.db.users.delete_one({"_id": ObjectId(id)})
            return UserEntity(user)
        except:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error deleting user.")