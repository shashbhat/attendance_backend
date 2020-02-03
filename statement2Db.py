from pymongo import MongoClient

uri = "mongodb://localhost:27017/dhi_analytics"


client = MongoClient(uri)
db = client.dhi_analytics

def get_academic_year():
    collection = db.dhi_student_attendance
 
    academic_year = []
    for x in collection.aggregate([ 

    {"$group": {"_id":"null", "academic_year":{ "$addToSet": "$academicYear" } }},
    {"$project":{"_id":0, "res":"$academic_year" }}
                                ]):
                                academic_year.append(x["res"])
    return academic_year