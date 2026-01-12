# from flask import Flask, request
# from flask_restful import Api, Resource

# app = Flask(__name__)
# api = Api(app)

# student_data = {
#     1: {"first_name": "himanshu", "last_name": "rastogi", "role": "TA"},
#     2: {"first_name": "rahul", "last_name": "suresh", "role": "student"}
# }

# class StudentApi(Resource):
#     def get(self, student_id):
#         student = student_data.get(student_id, None)
#         return student
    
#     def delete(self, student_id):
#         student = student_data.get(student_id, None)
#         if student:
#             del student_data[student_id]
#             return "done"
#         else:
#             return "not present"
    
#     def post(self):
#         request_body = request.json
#         f_name = request_body["first_name"]
#         l_name = request_body["last_name"]
#         role   = request_body["role"]

#         student_data[3] = {"first_name": f_name, "last_name": l_name, "role": role}
#         return "created successfully", 201
    
#     def put(self, student_id):
#         request_body = request.json
#         f_name = request_body["first_name"]
#         l_name = request_body["last_name"]
#         role   = request_body["role"]

#         student = student_data[student_id]
#         student["first_name"] = f_name
#         student["last_name"]  = l_name
#         student["role"]       = role

#         return "change sucessful", 201

    
# api.add_resource(StudentApi, "/api/student/<int:student_id>", "/api/student/")


# if __name__ == "__main__":
#     app.run(debug=True)


# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy


# app = Flask(__name__)

# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.sqlite3"

# db = SQLAlchemy(app)
# # db = SQLAlchemy()
# # db.init_app(app)

class Student(db.Model):            #-> student
    __tablename__ = "student"

    student_id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(50), nullable=False)
    roll_number = db.Column(db.String(10), unique=True, nullable=False)
    courses = db.relationship("Course", back_populates="students")

# s1.courses      -> Student to course -> it gives you courses associated with students

class Course(db.Model):
    __tablename__ = "course"

    course_id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String(50), nullable=False)
    course_code = db.Column(db.String(6), unique=True, nullable=False)

    student_id =  db.Column(db.Integer, db.ForeignKey("Student.student_id"), unique=True)
    # one-to-one, one-to-many, many-to-one, many-to-many
    students = db.relationship("Student", back_populates="courses")


    # lazy="select,dynamic,True,joined,eager"  

    # 
from flask import Flask, redirect, url_for

app = Flask(__name__)

@app.route("/student/<int:id>")
def student_details(id, name):
    return "student with id"

@app.route("/test")
def test():
    output = []
    output.append(url_for('student_details', id=1, name="himanshu"))

    return output


if __name__ == "__main__":
    app.run(debug=True)

# case1: TypeError: student_details() got an unexpected keyword argument 'id'
# case2: TypeError: student_details() missing 1 required positional argument: 'name'


api.add_resource(Student, "/student", "/student/<int:student_id>")

add_argument("student_id", type="int")