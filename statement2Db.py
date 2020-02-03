from pymongo import MongoClient

uri = "mongodb://localhost:27017/dhi_analytics"


client = MongoClient(uri)
db = client.dhi_analytics

def get_academic_year():
    collection = db.dhi_internal
 
   
    res = collection.aggregate([ 

    {"$group": {"_id":"null", "academic_year":{ "$addToSet": "$academicYear" } }},
    {"$project":{"_id":0, "res":"$academic_year" }}
                                ])
    for r in res:
        r = r["res"]        
    return r

def get_term_details():
    collection = db.dhi_term_detail
    res = collection.aggregate([
  {"$unwind": "$academicCalendar"},
        {"$group": {"_id":"null", "termNo":{ "$addToSet": "$academicCalendar.termNumber" }}},
        {"$project":{"termNo":1, "_id":0}} ])
    

    for r in res:
        r = r["termNo"]

    r.sort()
    return r
