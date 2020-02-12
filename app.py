from flask import Flask, jsonify,request
from flask_cors import CORS, cross_origin
from flask_pymongo import PyMongo
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity, get_jwt_claims

)

import statement2Db as sdb
app = Flask(__name__)
CORS(app)


app.config["MONGO_URI"] = "mongodb://localhost:27017/dhi_analytics"


mongo = PyMongo(app)
# Setup the Flask-JWT-Extended extension


app.config['JWT_SECRET_KEY'] = 'super-secret' 
jwt = JWTManager(app)


class UserObject:
    def __init__(self, username, roles):
        self.username = username
        self.roles = roles


@jwt.user_claims_loader
def add_claims_to_access_token(user):
    return {'roles': user.roles}

@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.username

# Provide a method to create access tokens. The create_access_token()
# function is used to actually generate the token, and you can return
# it to the caller however you choose.
@app.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400
    username = request.json.get('username', None)
    if not username:
        return jsonify({"msg": "Missing username parameter"}), 400
    user = mongo.db.dhi_user.find_one({'email': username})
    if not user:
        return jsonify({"msg": "Bad username or password"}), 401
    roles = [ x['roleName'] for x in user['roles']]
    user = UserObject(username=user["email"], roles=roles)
    # Identity can be any data that is json serializable
    access_token = create_access_token(identity=user,expires_delta=False)
    return jsonify(access_token=access_token), 200

@app.route('/message')
def message():
    return {"message":"Check you luck"}

# Protect a view with jwt_required, which requires a valid access token
# in the request to access.


@app.route('/user', methods=['GET'])
@jwt_required
def protected():
    # Access the identity of the current user with get_jwt_identity
    ret = {
        'user': get_jwt_identity(),  
        'roles': get_jwt_claims()['roles'] ,
        }
    return jsonify(ret), 200


@app.route('/academicYear')
def get_academic_year():
    res =  sdb.get_academic_year()
    return jsonify({"res":res})

@app.route('/termDetails')
def get_term_details():
    res = sdb.get_term_details()
    return jsonify({"res":res})

@app.route('/studentAttendanceDetails/<usn>/<term>/<academicYear>')
def get_student_attendance_details(usn, term, academicYear):
    res = sdb.get_student_attendance_details(usn, term, academicYear)
    return jsonify({"res":res})


@app.route('/studentUEmarksDetails/<usn>/<term>/<academicYear>')
def get_student_Umarks(usn, term, academicYear):
    res = sdb.get_student_Umarks(usn, term, academicYear)
    return jsonify({"res":res})

@app.route('/studentUSNlogin/<email>')
def get_usn_email(email):
    res = sdb.get_usn_email(email)
    return jsonify({"res":res})
    
@app.route('/getCourseAttendance/<course>/<usn>')
def courseAttendance(course,usn):
    res = sdb.getCourseAttendance(course,usn)
    return jsonify({"res":res})

# Faculty

# @app.route('/faculties/<string:dept>')
# def get_faculty(dept):
#     faculties = sdb.get_Faculty(dept)
#     return jsonify({"faculties":faculties})


@app.route('/facultyAttendenceDetails/<term>/<academicYear>/<eid>')
def get_faculty_attendence_details(term,academicYear,eid):
    res = sdb.get_faculty_attendence_details(term,academicYear,eid)
    return jsonify({"res":res})



# @app.route('/facultyMarksDetails')
# def get_faculty_marks_details():
#     usnList = ["4MT16ME008", "4MT16ME013"]
#     courseCode = "15ME53"
#     res = sdb.get_faculty_avg_marks_details()
#     return jsonify({"res":res})



@app.route('/facultyMarksDetails/<term>/<academicYear>/<eid>')
def get_faculty_marks1_details(term, academicYear, eid):
  
    res = sdb.get_faculty_marks_details(term, academicYear,eid)
    return jsonify({"res":res})

@app.route('/facultyEid/<email>')
def get_eid_by_email(email):
    res = sdb.get_eid_by_email(email)
    return jsonify({"res":res})

    
@app.route('/getDeptFaculty/<dept>')
def getDeptFaculty(dept):
    faculty = sdb.getDeptFaculty(dept)
    return jsonify({"res":faculty})

@app.route('/getFacultyNameByDeptId/<deptId>')
def getFacultyName(deptId):
    name = sdb.getFacultyName(deptId)
    return jsonify({"res":name})

@app.route('/getDeptNames')
def get_dept_names():
    dept = sdb.get_dept_names()
    return jsonify({'res':dept})

@app.route('/getTotalClassTaken/<eid>/<courseName>')
def get_total_class_taken(eid, courseName):
    total = sdb.get_total_class_taken(eid,courseName)
    return jsonify({'res':total})


@app.route('/getUserNameEmail/<email>')
def get_user_name_by_email(email):
    res = sdb.get_user_name_by_email(email)
    return jsonify({'name':res})

if __name__ == "__main__":
    app.run(port=8088,debug=True)
