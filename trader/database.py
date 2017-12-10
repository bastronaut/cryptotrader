from pymongo import MongoClient




class database:

    def __init__(self, dbname):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client[dbname]

    def save(self, collection, data):
        if isinstance(data, dict):
            self.db[collection].insert_one(data)
        if isinstance(data, list):
            self.db[collection].insert_many(data)

    def getdb(self):
        return self.db
