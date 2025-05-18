import os
from pymongo import MongoClient

# Initialize and export a shared Mongo client instance
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017')
mongo_client = MongoClient(MONGO_URI)