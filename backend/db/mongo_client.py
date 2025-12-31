# mongo_client.py
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

ATLAS_URI = os.getenv("ATLAS_URI")
DB_NAME = os.getenv("DB")
COLLECTION_NAME = os.getenv("COLLECTION")


class AtlasClient():
   def __init__ (self, ATLAS_URI, DB_NAME):
       self.mongodb_client = MongoClient(ATLAS_URI)
       self.database = self.mongodb_client[DB_NAME]
   ## A quick way to test if we can connect to Atlas instance
   def ping (self):
       self.mongodb_client.admin.command('ping')
   def get_collection (self, COLLECTION_NAME):
       collection = self.database[COLLECTION_NAME]
       return collection
   def find (self, COLLECTION_NAME, filter = {}, limit=0):
       collection = self.database[COLLECTION_NAME]
       items = list(collection.find(filter=filter, limit=limit))
       return items
   
atlas_client = AtlasClient (ATLAS_URI, DB_NAME)
try:
    atlas_client.ping()
    print("Connected to Atlas instance!")
except Exception as e:
    print(f"MongoDB connection failed: {e}")