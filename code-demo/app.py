# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy

# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"

# db = SQLAlchemy(app)

# # Models


# # Association table (NO model class needed)
# user_project = db.Table(
#     "user_project",
#     db.Column("user_id", db.Integer, db.ForeignKey("user.id"), primary_key=True),
#     db.Column("project_id", db.Integer, db.ForeignKey("project.id"), primary_key=True),
# )


# class User(db.Model):
#     __tablename__ = "user"

#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(50), unique=True, nullable=False)
#     email = db.Column(db.String(120), unique=True, nullable=False)

#     projects = db.relationship(
#         "Project",
#         secondary=user_project,
#         back_populates="users",
#     )

#     def __repr__(self):
#         return f"<User {self.username}>"


# class Project(db.Model):
#     __tablename__ = "project"

#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100), nullable=False)
#     is_active = db.Column(db.Boolean, default=True)

#     users = db.relationship(
#         "User",
#         secondary=user_project,
#         back_populates="projects",
#     )

#     def __repr__(self):
#         return f"<Project {self.name}>"

# @app.route("/")
# def home():
#     return "hello"

# @app.route("/init")
# def init():
#     db.create_all()
#     from fake_data import seed_data

#     seed_data(db=db, Project=Project, User=User)
#     return "done"

# @app.route("/get/<param>")
# def get(param):
#     result1 = db.session.query(eval(f"User.{param}")).all()
#     result2 = User.query.with_entities(User.id).all()

#     return (str(result1) + "\n" + str(result2))


    
# if __name__ == "__main__":
#     # print(app.url_map)
#     app.run(debug=True, port=5000)


from flask import Flask
from time import sleep, asctime

app = Flask(__name__)

x = 0

@app.route("/")
def home():
    global x
    x += 1
    t = asctime()
    print(x, t)
    sleep(2)
    return f"{x=}\n{t=}"

if __name__ == "__main__":
    app.run(threaded=1, debug=True, host='0.0.0.0', port=5000)
