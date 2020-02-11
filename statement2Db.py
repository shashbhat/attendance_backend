from pymongo import MongoClient
from operator import itemgetter 
import bson
import re

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
        res.append(x)
    return res

def getCourseAttendance(course,usn):
    collection = db.dhi_student_attendance
    res = collection.aggregate([
    {"$match":{"courseName":course}},
    {"$unwind":"$students"},
    {"$match":{"students.usn":usn}},
    {"$project":{"total":"$students.totalNumberOfClasses","present":"$students.presentCount","_id":0}}
    ])
    arr = []
    for x in res:
        arr.append(x)
    return arr.pop()

# Faculty

# def get_Faculty(dept):
#     pattern = re.compile(f'^{dept}')
#     regex = bson.regex.Regex.from_native(pattern)
#     regex.flags ^= re.UNICODE
#     faculties = db.dhi_user.aggregate([
        
#         {"$match":{"roles.roleName":"FACULTY","employeeGivenId":{"$regex":regex}}},
#         {"$sort":{"name":1}},
#         {"$project":{"employeeGivenId":1,"name":1,"_id":0}}
        
#     ])
#     arr = []
#     for x in faculties:
#         arr.append(x)
#     return arr    



def get_faculty_attendence_details(term,academicYear,eid):
    collection = db.dhi_student_attendance
    res = collection.aggregate([


    {"$match":{"academicYear":academicYear,"students.termNumber":term}},
    {"$unwind":{'path':"$faculties"}},
    {"$unwind":{'path':"$faculties.facultyName"}},
    {"$match":{"faculties.employeeGivenId":eid}},
    {"$group":{"_id":{"avg":{"$avg":"$students.percentage"},"faculty":"$faculties.facultyName","course":"$courseName"}}},
    {"$project":{"faculty":"$_id.faculty","course":"$_id.course","_id":0,"avg":"$_id.avg"}}
    ])
    arr = []
    for r in res:
        arr.append(r)
    ar = sorted(arr, key=itemgetter('course')) 
    return ar



def get_faculty_avg_marks_details(res):
    courseCode = res[0]['courseCode']
    usnList = res[0]['usn']
    collection = db.pms_university_exam
    res = collection.aggregate([

    {

    '$unwind':'$terms'
    },
    {

    '$unwind':'$terms.scores'
    },
    {

    '$unwind':'$terms.scores.courseScores'
    },

    {

    '$match':{
    'terms.scores.courseScores.courseCode':courseCode,
    'terms.scores.usn':{'$in': usnList}
    }
    },
    {"$group":{"_id":"null", "ue" : {"$push": "$terms.scores.courseScores.ueScore"}
    }},
    {"$project":{"courseCode":"$_id.courseCode","avgMarks":{"$avg":"$ue"},"_id":0}}

    ])

    arr = []
    for x in res:
        arr.append(x)

    return arr



def get_faculty_marks_details(term, academicYear,eid):
    # collection = db.dhi_student_attendance
    # res =collection.aggregate([
    # {"$unwind":"$departments"},
    # {"$match":{"academicYear":academicYear,"faculties.employeeGivenId":eid,"departments.termNumber":term}},

    # {"$unwind":"$students"},
    # {"$group":{"_id":{"courseCode":"$courseCode"},"usn" : {"$push": "$students.usn"}
    # }},
    # {"$project":{"courseCode":"$_id.courseCode","usn":"$usn", "_id":0}}
    # ])
    # arr = []
    # for x in res:
    #     arr.append(x)
    # print(arr)
    # res1 = get_faculty_avg_marks_details(arr)
    # return res1
    collection =db.dhi_student_attendance
    emp = collection.aggregate([
    {"$match":{"academicYear":academicYear,"students.termNumber":term}},
    {"$unwind":{'path':"$faculties"}},
    {"$unwind":{'path':"$faculties.facultyName"}},
    {"$match":{"faculties.employeeGivenId":eid}},
    {
    "$lookup":
    {
    "from":"pms_university_exam",
    "localField":"students.usn",
    "foreignField":"terms.scores.usn",
    "as":"usn"
    }
    },
    {"$unwind":{'path':"$usn"}},
    {"$unwind":{'path':"$usn.terms"}},
    {"$unwind":{'path':"$usn.terms.scores"}},
    {"$unwind":{'path':"$usn.terms.scores.courseScores"}},
    {"$match":{"$expr":{"$eq":["$usn.terms.scores.courseScores.courseCode","$courseCode"]}}},
    {"$group":{"_id":{"course":"$courseName"},"ue":{"$push":"$usn.terms.scores.courseScores.ueScore"}}},
    {"$project":{"course":"$_id.course","Avg":{"$avg":"$ue"},"_id":0}}
    ])
    res = []
    for x in emp:
        res.append(x)
    result = sorted(res,key=itemgetter("course"))
    return result


def get_eid_by_email(email):
    collection = db.dhi_user
    eid = collection.aggregate([

    {"$match": {"email":email}},
    {"$project":{"employeeGivenId":1, "_id":0}}
    ])
    res = []
    for x in eid:
        res.append(x)
    return res

def getFacultyName(deptId):
    collection = db.dhi_student_attendance
    name = collection.aggregate([
        {"$unwind":{'path':"$departments"}},
        {"$match":{"departments.deptId":deptId}},
        {"$unwind":{'path':"$faculties"}},
        {"$group":{"_id":{"name":"$faculties.facultyName","empId":"$faculties.employeeGivenId"}}},
        {"$project":{"name":"$_id.name","empId":"$_id.empId","_id":0}}
        ])
    res = []
    for n in name:
        res.append(n)
    return res

def getDeptFaculty(dept):
    collection = db.dhi_user
    pattern = re.compile(f'^{dept}')
    regex = bson.regex.Regex.from_native(pattern)
    regex.flags ^= re.UNICODE 
    faculties = collection.aggregate([
        {"$match":{"roles.roleName":"FACULTY","employeeGivenId":{"$regex":regex}}},
        {"$sort":{"name":1}},
        {"$project":{"employeeGivenId":1,"name":1,"_id":0}}
    ])
    res = []    
    for x in faculties:
        res.append(x)
    return res
