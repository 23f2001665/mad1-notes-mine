from flask import Flask 
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
db = SQLAlchemy()

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///one_to_many.db'
app.config['SQLALCHEMY_ECHO'] = True

db.init_app(app)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    
    enrollments = db.relationship('Enrollment',back_populates='student')

class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer,db.ForeignKey(Student.id))
    
    student = db.relationship('Student',back_populates='enrollments',lazy = 'subquery')
  


def create_table():
    with app.app_context():
        db.create_all()
        s1 = Student(name="krishna1")
        s2 = Student(name="krishna2")
        s3 = Student(name="krishna3")
                    
        db.session.add_all([s1,s2,s3])
            
        e1 = Enrollment(student_id = 1)
        e2 = Enrollment(student_id = 1)
        e3 = Enrollment(student_id = 1)
            
        db.session.add_all([e1,e2,e3])
            
        db.session.commit()
        
with app.app_context():
    
    # student1 = db.session.query(Student).first()
    # print(student1)
    # print(student1.enrollments)
    # print(type(student1.enrollments)) 
    # # [<Enrollment 1>, <Enrollment 2>, <Enrollment 3>, <Enrollment 4>, <Enrollment 5>, <Enrollment 6>, <Enrollment 7>, <Enrollment 8>, <Enrollment 9>]
    
    e1 = db.session.query(Enrollment).first()
    
    # this e1 belongs to which student 
    print(e1)
    print("#"*20)
    print(e1.student)
    
    
    
    


if __name__ == "__main__":
    # create_table()
    app.run(debug=True)