"""Database client for MongoDB"""

import os
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from dotenv import load_dotenv

load_dotenv()
db_client = MongoClient(os.getenv("MONGO_URI"))

try:
    db_client.server_info()
    print("Connected to Database")
except PyMongoError as exception:
    print(f"Error connecting to Database: {exception}")
    exit(1)
