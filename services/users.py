"""Users services module."""

from typing import List
from pymongo.database import Database
from pymongo.errors import PyMongoError
from bson import ObjectId
from services.companies import CompaniesServices
from models.user import UpdateUser, User
from models.user import Profile
from schemas.company import company_entity
from utils.auth import create_access_token, get_hashed_password, verify_password

class Error(Exception):
    """Base class for exceptions in this module."""

class UsersServices():
    """Users services class."""
    def __init__(self, database: Database) -> None:
        self.database = database

    def get_user(self, user_id: str) -> User:
        """
        Get a user.
        Args:
            user_id (str): User id.
        Returns:
            User: User.
        Raises:
            Exception: If there's an error reading the user.
        """

        try:
            user = self.database.users.find_one({"_id": ObjectId(user_id)})
            return user
        except PyMongoError as exception:
            raise Error(f"Error reading user: {exception}") from exception

    def get_by_email(self, email: str) -> User:
        """
        Get a user.
        Args:
            email (str): User email.
        Returns:
            User: User.
        Raises:
            Exception: If there's an error reading the user.
        """
        try:
            user = self.database.users.find_one({"email": email})
            return user
        except PyMongoError as exception:
            raise Error(f"Error reading user: {exception}") from exception

    def authenticate_user(self, email: str, password: str) -> User:
        """
        Authenticate a user.
        Args:
            email (str): User email.
            password (str): User password.
        Returns:
            User: User.
        Raises:
            Exception: If there's an error reading the user.
        """
        try:
            user = self.get_by_email(email)
            if user is None or not verify_password(password, user["password"]):
                raise Error("Authentication error")
            return user
        except PyMongoError as exception:
            raise Error(f"Error reading user: {exception}") from exception

    def create_user(self, user: User) -> User:
        """
        Create a user.
        Args:
            user (User): User to create.
        Returns:
            User: Created user.
        Raises:
            Exception: If there's an error creating the user.
        """
        try:
            del user["id"]
            if self.get_by_email(user["email"]):
                raise Error("User already exists")
            user["password"] = get_hashed_password(user["password"])
            insertion_result = self.database.users.insert_one(user)
            created_user = self.get_user(str(insertion_result.inserted_id))
            return created_user
        except PyMongoError as exception:
            raise Error(f"Error creating user: {exception}") from exception

    def login(self, email: str, password: str) -> dict:
        """
        Login a user.
        Args:
            email (str): User email.
            password (str): User password.
        Returns:
            dict: Token.
        Raises:
            Exception: If there's an error reading the user.
        """
        try:
            user = self.authenticate_user(email, password)
            token = create_access_token(data={"sub": user["email"], "roles": user["roles"]})
            return {"access_token": token, "token_type": "bearer"}
        except PyMongoError as exception:
            raise Error(f"Error reading user: {exception}") from exception

    def get_profile(self, email: str) -> Profile:
        """
        Get profile.
        Args:
            email (str): User email.
        Returns:
            Profile: Profile.
        Raises:
            Exception: If there's an error reading the user.
        """
        try:
            user = self.get_by_email(email)
            company = CompaniesServices(self.database).get_company(user["company"])
            user["company"] = company_entity(company)
            return user
        except PyMongoError as exception:
            raise Error(f"Error reading user: {exception}") from exception

    def get_by_company(self, company_id: str) -> List[User]:
        """
        Get users by company.
        Args:
            company (str): Company.
        Returns:
            List[User]: List of users.
        Raises:
            Exception: If there's an error reading the users.
        """
        try:
            users = self.database.users.find({"company": company_id})
            return users
        except PyMongoError as exception:
            raise Error(f"Error reading users: {exception}") from exception

    def update_user(self, user: UpdateUser, user_id: str) -> User:
        """
        Update a user.
        Args:
            user (User): User to update.
        Returns:
            User: Updated user.
        Raises:
            errors["Update error"]: If the user could not be updated.
        """
        try:
            self.database.users.update_one({"_id": ObjectId(user_id)}, {"$set": user})
            updated_user = self.get_user(user_id)
            return updated_user
        except PyMongoError as exception:
            raise Error(f"Error updating user: {exception}") from exception

    def delete_user(self, user_id: str) -> User:
        """
        Delete a user.
        Args:
            user_id (str): User id.
        Returns:
            User: Deleted user.
        Raises:
            errors["Delete error"]: If the user could not be deleted.
        """
        try:
            user = self.get_user(user_id)
            self.database.users.delete_one({"_id": ObjectId(user_id)})
            return user
        except PyMongoError as exception:
            raise Error(f"Error deleting user: {exception}") from exception
