"""Workers services module."""

import datetime
from typing import List
import pytz
from bson import ObjectId
from pymongo.database import Database
from pymongo.errors import PyMongoError
from pymongo import UpdateOne, InsertOne
from models.worker import Worker, UpdateWorker
from schemas.user import user_entity

class Error(Exception):
    """Base class for exceptions in this module."""

class WorkersServices():
    """Workers services class."""
    def __init__(self, database: Database) -> None:
        self.database = database

    def create_worker(self, company: str, worker: Worker, user: user_entity) -> Worker:
        """
        Create a worker.
        Args:
            company (str): Company name.
            worker (Worker): Worker data.
            user (user_entity): User data.
        Returns:
            Worker: Worker created.
        Raises:
            Error: Worker already exists.
            Error: Error creating worker.
        """
        try:
            del worker["id"]
            worker["company"] = company
            if self.database.workers.find_one({"identification": worker["identification"]}):
                raise Error("Worker already exists")
            worker["userName"] = user["userName"]
            worker["updatedBy"] = user["userName"]
            worker["createdAt"] = datetime.datetime.now(
                pytz.timezone("America/Bogota")).strftime("%d/%m/%Y %H:%M")
            worker["updatedAt"] = datetime.datetime.now(
                pytz.timezone("America/Bogota")).strftime("%d/%m/%Y %H:%M")
            fields = []
            for field in worker["fields"]:
                fields.append(dict(field))
            worker["fields"] = fields
            worker = self.database.workers.insert_one(worker)
            worker = self.database.workers.find_one({"_id": worker.inserted_id})
            return worker
        except PyMongoError as exception:
            raise Error(f"Error creating worker: {exception}") from exception

    def create_and_update_workers(
        self,
        company: str,
        workers: List[Worker],
        user: user_entity) -> List[Worker]:
        """
        Create workers.
        Args:
            company (str): Company name.
            workers (List[Worker]): Workers data.
            user (user_entity): User data.
        Returns:
            List[Worker]: Workers created.
        Raises:
            Error: Error creating workers.
        """
        try:
            existing_workers = self.database.workers.find({})
            existing_workers = [dict(worker) for worker in existing_workers]
            existing_identifications = [worker["identification"] for worker in existing_workers]
            create_operations = []
            update_operations = []
            for worker in workers:
                del worker["id"]
                worker["company"] = company
                fields = []
                for field in worker["fields"]:
                    fields.append(dict(field))
                if worker["identification"] in existing_identifications:
                    update_operations.append(UpdateOne(
                        {"identification": worker["identification"]},
                        {"$set": dict(worker)}))
                else:
                    worker["userName"] = user["userName"]
                    worker["updatedBy"] = user["userName"]
                    worker["createdAt"] = datetime.datetime.now(
                        pytz.timezone("America/Bogota")).strftime("%d/%m/%Y %H:%M")
                    worker["updatedAt"] = datetime.datetime.now(
                        pytz.timezone("America/Bogota")).strftime("%d/%m/%Y %H:%M")
                    worker["fields"] = fields
                    create_operations.append(InsertOne(dict(worker)))
            if create_operations:
                self.database.workers.bulk_write(create_operations)
            if update_operations:
                self.database.workers.bulk_write(update_operations)
            workers = self.database.workers.find(
                {"identification": {"$in": existing_identifications}})
            return workers
        except PyMongoError as exception:
            raise Error(f"Error creating workers: {exception}") from exception

    def create_workers(
        self,
        company: str,
        workers: List[Worker],
        user: user_entity) -> List[Worker]:
        """
        Create workers.
        Args:
            company (str): Company name.
            workers (List[Worker]): Workers data.
            user (user_entity): User data.
        Returns:
            List[Worker]: Workers created.
        Raises:
            Error: Error creating workers.
        """
        try:
            for worker in workers:
                del worker["id"]
                worker["company"] = company
                if self.database.workers.find_one({"identification": worker["identification"]}):
                    raise Error("Worker already exists")
                worker["userName"] = user["userName"]
                worker["updatedBy"] = user["userName"]
                worker["createdAt"] = datetime.datetime.now(
                    pytz.timezone("America/Bogota")).strftime("%d/%m/%Y %H:%M")
                worker["updatedAt"] = datetime.datetime.now(
                    pytz.timezone("America/Bogota")).strftime("%d/%m/%Y %H:%M")
                fields = []
                for field in worker["fields"]:
                    fields.append(dict(field))
                worker["fields"] = fields
            workers = self.database.workers.insert_many(workers)
            workers = self.database.workers.find({"_id": {"$in": workers.inserted_ids}})
            return workers
        except PyMongoError as exception:
            raise Error(f"Error creating workers: {exception}") from exception

    def get_worker_by_id(self, company: str, worker_id: str) -> Worker:
        """
        Get a worker by id.
        Args:
            company (str): Company name.
            worker_id (str): Worker id.
        Returns:
            Worker: Worker data.
        Raises:
            Error: Worker not found.
            Error: Error reading worker.
        """
        try:
            worker = self.database.workers.find_one({"_id": ObjectId(worker_id)})
            if not worker:
                return Error("Worker not found")
            if worker["company"] != company:
                raise Error("Unauthorized")
            return worker
        except PyMongoError as exception:
            raise Error(f"Error reading worker: {exception}") from exception

    def get_workers_by_name_or_identification(
        self,
        company: str,
        search: str,
        limit: int,
        skip: int,
        user_tags: list) -> List[Worker]:
        """
        Get workers by name or identification.
        Args:
            company (str): Company name.
            search (str): Search text.
            limit (int): Limit.
            skip (int): Skip.
            user_tags (list): User tags.
        Returns:
            List[Worker]: Workers data.
        Raises:
            Error: Error reading workers.
        """
        try:
            if "all" in user_tags:
                workers = self.database.workers.find(
                    {"company": company, "$or": [
                        {"name": {"$regex": search, "$options": "i"}},
                        {"identification":
                            {"$regex": search, "$options": "i"}}]}).limit(limit).skip(skip)
                return workers
            workers = self.database.workers.find(
                {"company": company, "tags": {"$in": user_tags}, "$or": [
                    {"name": {"$regex": search, "$options": "i"}},
                    {"identification":
                        {"$regex": search, "$options": "i"}}]}).limit(limit).skip(skip)
            return workers
        except PyMongoError as exception:
            raise Error(f"Error reading workers: {exception}") from exception

    def get_workers_by_an_array(self, company: str, worker_ids: List[str]) -> List[Worker]:
        """
        Find workers by an array.
        Args:
            company (str): Company name.
            worker_ids (List[str]): Workers ids.
        Returns:
            List[Worker]: Workers data.
        Raises:
            Error: Error reading workers.
        """
        try:
            workers = self.database.workers.find(
                {"company": company, "_id": {"$in": [ObjectId(id) for id in worker_ids]}})
            return workers
        except PyMongoError as exception:
            raise Error(f"Error reading workers: {exception}") from exception

    def update_worker(
        self,
        company: str,
        worker_id: str,
        data: UpdateWorker,
        user: user_entity) -> Worker:
        """
        Update a worker.
        Args:
            company (str): Company name.
            worker_id (str): Worker id.
            data (UpdateWorker): Worker data.
            user (user_entity): User data.
        Returns:
            Worker: Worker updated.
        Raises:
            Error: Worker not found.
            Error: Unauthorized.
            Error: Error updating worker.
        """
        try:
            worker = self.database.workers.find_one({"_id": ObjectId(worker_id)})
            if not worker:
                return Error("Worker not found")
            if worker["company"] != company:
                raise Error("Unauthorized")
            user_tags = user["workers"]
            if not set(worker["tags"]).intersection(user_tags) and "all" not in user_tags:
                raise Error("Unauthorized")
            data = dict(data)
            fields = []
            for field in data["fields"]:
                fields.append(dict(field))
            data["fields"] = fields
            data["updatedAt"] = datetime.datetime.now(
                pytz.timezone("America/Bogota")).strftime("%d/%m/%Y %H:%M")
            data["updatedBy"] = user["userName"]
            self.database.workers.update_one({"_id": ObjectId(worker_id)}, {"$set": data})
            worker = self.database.workers.find_one({"_id": ObjectId(worker_id)})
            return worker
        except PyMongoError as exception:
            raise Error(f"Error updating worker: {exception}") from exception

    def delete_worker(self, company: str, worker_id: str, user_tags: list) -> Worker:
        """
        Delete a worker.
        Args:
            company (str): Company name.
            worker_id (str): Worker id.
            user_tags (list): User tags.
        Returns:
            Worker: Worker deleted.
        Raises:
            Error: Worker not found.
            Error: Unauthorized.
            Error: Error deleting worker.
        """
        try:
            worker = self.database.workers.find_one({"_id": ObjectId(worker_id)})
            if not worker:
                raise Error("Worker not found")
            if not set(worker["tags"]).intersection(user_tags) and "all" not in user_tags:
                raise Error("Unauthorized")
            if worker["company"] != company:
                raise Error("Unauthorized")
            self.database.workers.delete_one({"_id": ObjectId(worker_id)})
            return worker
        except PyMongoError as exception:
            raise Error(f"Error deleting worker: {exception}") from exception
