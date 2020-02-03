from pymongo import MongoClient

uri = "mongodb://localhost:27017/dhi_analytics"

client = MongoClient(uri)

def get_academic_year():
    