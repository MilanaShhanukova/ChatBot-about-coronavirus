import pymongo


class DataBase_for_bot:
	
    def __init__(self):
        client = pymongo.MongoClient("localhost", 27017)
        db = client.mongo_bd
        self.corona_collection = db.corona_data

    def inserting(self, data):
        self.corona_collection.insert_one(data)

    def finding(self):
        return self.corona_collection.find()
