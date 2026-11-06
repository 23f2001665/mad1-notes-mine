from flask import Flask 
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
db = SQLAlchemy()

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///one_to_one.db'
app.config['SQLALCHEMY_ECHO'] = True

db.init_app(app)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    
    profile = db.relationship('Profile',uselist=False)
    
class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer,db.ForeignKey(Student.id),unique=True)
    
    student = db.relationship('Student')

def create_table():
    with app.app_context():
        db.create_all()
        s1 = Student(name="krishna1")
        s2 = Student(name="krishna2")
        s3 = Student(name="krishna3")
        
        db.session.add_all([s1,s2,s3])
        
        p1 = Profile(student_id=1)
        p2 = Profile(student_id=2)
        p3 = Profile(student_id=3)
        
        db.session.add_all([p1,p2,p3])
        db.session.commit()
with app.app_context():
    
    # student1 = db.session.query(Student).first()
    # print(student1) # <Student 1>
    # print(student1.profile) # [<Profile 1>]
    # print(type(student1.profile.id)) # <class 'sqlalchemy.orm.collections.InstrumentedList'>  uselist = False # <class '__main__.Profile'>
    # print(student1.profile.id)
    
    profile1 = db.session.query(Profile).first()
    print(profile1)
    print(profile1.student)
    print(type(profile1.student)) # <class '__main__.Student'>

if __name__ == "__main__":
    # create_table()
    app.run(debug=True)