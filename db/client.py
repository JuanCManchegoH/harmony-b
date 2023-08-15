import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
db_client = MongoClient(os.getenv("MONGO_URI"))

try:
    db_client.server_info()
    print("Connected to MongoDB")
except Exception as e:
    print("Unable to connect to MongoDB")
    print(e)
    exit(1)