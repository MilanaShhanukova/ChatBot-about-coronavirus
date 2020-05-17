import pymongo

class DataBase_for_bot:
    def __init__(self):
        client = pymongo.MongoClient("localhost", 27017)
        db = client.mongo_bd
        self.corona_collection = db.corona_data
        self.video_collection = db.video_corona

    def inserting(self, data):
        self.video_collection.insert_one(data)

    def finding(self):
        return self.video_collection.find()

    def replacing(self, one_dict, new_dict):
        return self.video_collection.replace_one(one_dict, new_dict)

    def dropping(self):
        return self.video_collection.drop()



