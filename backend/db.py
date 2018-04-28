import sys

from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

class Mongo():

    def __init__(self, username, password, host, port, db):
        try:
            self.client = MongoClient('mongodb://{}:{}@{}:{}/{}'
                .format(username, password, host, port, db))
            self.client.server_info()
            self.db = db
        except ServerSelectionTimeoutError:
            print("Could not connect to mongo!", file=sys.stderr)
            self.client = None

    def get(self, text):
        result = []
        if self.client:
            collection = self.client[self.db].url
            for obj in collection.find({'title': {'$regex': text}}):
                result.append(obj)
        return result
