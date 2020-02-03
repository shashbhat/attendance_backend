from pymongo import MongoClient

uri = "mongodb://localhost:27017/dhi_analytics"
db = dhi_analytics

client = MongoClient(uri)

def get_academic_year():
    collection = dhi_student_attendance
    db = dhi_analytics
    academic_year = []
    res = for x in collection.aggregate([[{ "$group": { "_id": "null","academicYear":{"$addToSet":"$academicYear"} } },
                                {"$project":{"res":"$academicYear","_id":0}}]])
    return [x for x in res ]