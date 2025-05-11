import os
import pymongo
import dotenv

dotenv.load_dotenv()

MONGO_URI = os.getenv('MONGO_URI')

if not MONGO_URI:
    raise ValueError('Env variable not set: MONGO_URI (add to server/.env)')

class DatabaseInterace:
    def __init__(self):
        self.client = pymongo.MongoClient(MONGO_URI)
        self.db = self.client['converge']

        self.users = self.db['users']
        self.games = self.db['games']

db = DatabaseInterace()
