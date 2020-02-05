from pymongo import MongoClient
from operator import itemgetter 

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


def get_student_attendance_details(usn, term, academicYear):
    collection = db.dhi_student_attendance
    res = collection.aggregate([

    {"$match":{"academicYear":academicYear}},
    {"$unwind":"$students"},
    {"$match":{"students.usn":usn}},
    {"$match":{"students.termNumber":term}},
    {"$group":{"_id":{"perc":"$students.percentage", "usn": "$students.usn", "course":"$courseName"}}},
    {"$project":{"perc":"$_id.perc", "usn":"$_id.usn", "courseName":"$_id.course", "_id":0}}

    ])
    arr = []
    for r in res:
        arr.append(r)
    ar = sorted(arr, key=itemgetter('courseName')) 
    return ar



def get_student_Umarks(usn, term, academicYear):
    collection = db.pms_university_exam
    res = collection.aggregate([

    {"$match":{"academicYear":academicYear }},
    {"$unwind": {'path':"$terms"}},
    {"$match":{"terms.termNumber": term}},
    {"$unwind":{"path": "$terms.scores"}},

    {"$match":{"terms.scores.usn": usn}},
    {"$unwind":{"path":"$terms.scores.courseScores"}},

  
    {"$group":{"_id":{"coursePerc":"$terms.scores.courseScores.totalScore", "usn":"$terms.scores.usn","courseName":"$terms.scores.courseScores.courseName" }}},
    {"$project":{"perc":"$_id.coursePerc", "usn":"$_id.usn", "courseName":"$_id.courseName", "_id":0}}

    ])

    arr = []
    for r in res:
            arr.append(r)
    ar = sorted(arr, key=itemgetter('courseName')) 
    return ar

            
def get_usn_email(email):
    collection = db.dhi_user
    usn = collection.aggregate([

  {"$match": {"email":email}},
    {"$project":{"usn":1, "_id":0}}
    
    ])
    res = []
    for x in usn:
        res = x["usn"]
    
    return res



