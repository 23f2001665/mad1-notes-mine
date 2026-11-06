from flask import Flask 
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
db = SQLAlchemy()

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///many_to_many.db'
app.config['SQLALCHEMY_ECHO'] = True

db.init_app(app)

# associative table 
class Enrollment(db.Model): 
        
    student_id = db.Column(db.Integer,db.ForeignKey('student.id'),primary_key=True)
    course_id = db.Column(db.Integer,db.ForeignKey('course.id'),primary_key=True)
    

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))

    course = db.relationship('Course',secondary='enrollment')
    
class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    
    student = db.relationship('Student',secondary='enrollment')
    
    
    


def create_table():
    with app.app_context():
        db.create_all()
        
        s1 = Student(name="krishna1")
        s2 = Student(name="krishna2")
        s3 = Student(name="krishna3")
                            
        db.session.add_all([s1,s2,s3])
        
        c1 = Course(name="mad1")
        c2 = Course(name="mad2")
        c3 = Course(name="mad3")
        
        db.session.add_all([c1,c2,c3])
        
        e1  = Enrollment(student_id= 1, course_id = 1)
        e3  = Enrollment(student_id= 1, course_id = 2)
        e2  = Enrollment(student_id= 1, course_id = 3)
        
        db.session.add_all([e1,e2,e3])
        
        db.session.commit()
        
        
if __name__ == "__main__":
    create_table()
    app.run()