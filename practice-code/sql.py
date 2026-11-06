# # imports 
# from flask import Flask
# from datetime import date,datetime,timezone
# from sqlalchemy.exc import IntegrityError

# from flask_sqlalchemy import SQLAlchemy 
# # integrates flask and sqlalchemy 

# app = Flask(__name__)

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'
# # app.config['SQLALCHEMY_ECHO'] = True

# db = SQLAlchemy(app)
# # db.init_app(app)

# class User(db.Model):
    
#     __tablename__ = 'users' #optional
    
#     id = db.Column(db.Integer,primary_key=True)
#     name = db.Column(db.String(30),nullable=False)
#     email = db.Column(db.String(30),unique=True)
#     section = db.Column(db.String(30))
#     is_active = db.Column(db.Boolean,default=True)
#     # created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
#     # updated_at = db.Column(db.DateTime, onupdate=datetime.now)
    
#     __table_args__ = (db.UniqueConstraint('section','name',name='unique_section_name'),)
    
#     def __repr__(self):
#         return f'<User { user.email}>'
    

# with app.app_context(): 
#     db.drop_all()
#     db.create_all()
#     u1 = User(name="pallavi",email="p1@gmail.com",section="comp")
#     u2 = User(name="pallavi1",email="p2@gmail.com",section="comp")
#     # u3 = User(id=3,name="pallavi3",email="p3@gmail.com")
    
#     # date(year,month,date)
#     try:

#         db.session.add(u1) # adding u1 object in the session 
#         db.session.add(u2)
#         # db.session.add(u3)
    
    
#         user = db.session.get(User,1)
#         print(user) # <User 1>
        
#         db.session.commit() # commit the transaction , 
#     except IntegrityError:
#         print("Give unique username......")


from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template_string, request, abort
from sqlalchemy import asc, desc, func
app = Flask(__name__)
db = SQLAlchemy()

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_ECHO'] = False

db.init_app(app=app)

class User(db.Model):
    __tablename__ = 'some-table'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    budget = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

    def _export(self):
        return {'username': self.username, 'city': self.city, 'budget': self.budget}

@app.route('/')
def home():
    return "Welcome"

@app.route('/create_database')
def create_database():
    db.create_all()
    return "database created successfully"

@app.route('/create_users')
def create_users():

    user1 = User(username='Alice', city='New York', budget=1000.0)
    user2 = User(username='Bob', city='Los Angeles', budget=1500.0)
    user3 = User(username='Charlie', city='Chicago', budget=800.0)
    user4 = User(username='David', city='New York', budget=1200.0)
    user5 = User(username='Eve', city='Los Angeles', budget=900.0)
    db.session.add_all([user1, user2, user3, user4, user5])
    db.session.commit()

    return "users created successfully"

@app.route('/get_user/<int:user_id>')
def get_user(user_id):
    user = db.session.get(User, user_id)
    if user:
        return user._export()
    else:
        abort(404)

@app.route('/get_all_users')
def get_all_users():
    users = db.session.query(User).all()
    print(users)

    l = []
    for user in users:
        l.append(user._export())

    return l

@app.route('/get_user')
def get_username():
    args = request.args
    name = args.get('name')
    city = args.get('city')
    budget = args.get('budget')

    query = db.session.query(User.username.label('name'))
    users = query.filter(User.budget == budget).order_by(desc('username')).all()
    # users = query.filter_by(budget=budget)
    result = []

    for user in users:
        result.append(user._export())
    return result

@app.route('/summary')
def summary():
    from sqlalchemy import func
    # Count the total number of users
    user_count = db.session.query(func.count(User.budget)).scalar()
    print(user_count)  # 5
    # Get the average budget of users
    average_budget = db.session.query(func.avg(User.budget)).scalar()
    print(average_budget)  # 1080.0
    # Get the total budget of users
    total_budget = db.session.query(func.sum(User.budget)).first()
    print(total_budget[0])  # 5400.0
    # Get the total budget for each city
    budget_by_city = db.session.query(User.city, func.sum(User.budget)).group_by(User.city).scalar()
    print(budget_by_city)

    return "summary"

if __name__ == '__main__':
    app.run(port=5001, debug=True)

