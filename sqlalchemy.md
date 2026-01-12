# Flask SQLAlchemy ORM – Detailed Guide

## 1. Setting up Flask-SQLAlchemy

Before performing queries and handling errors, you need to set up **Flask-SQLAlchemy** in your Flask application:

```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
```

- `SQLALCHEMY_DATABASE_URI`: Specifies the database URL (in this case, SQLite).
- `SQLALCHEMY_TRACK_MODIFICATIONS`: Disables tracking modifications for better performance.

---

## 1. Flask-SQLAlchemy ORM Basics

Flask-SQLAlchemy integrates SQLAlchemy ORM with Flask and session handling.

### Defining Models

```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True)
```

---

## 2. Creating Various Types of Relationships

SQLAlchemy supports **One-to-One**, **One-to-Many**, and **Many-to-Many**.

### One-to-Many

```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    posts = db.relationship('Post', backref='author', lazy=True)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
```

### One-to-One

```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    profile = db.relationship('Profile', backref='user', uselist=False)

class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)
```

### Many-to-Many

Uses association table.

```python
user_roles = db.Table(
    'user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'))
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    roles = db.relationship('Role', secondary=user_roles, backref='users')

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
```

---

## 3. Association Tables (Explicit Association Object)

This is used when many-to-many needs extra metadata.

```python
class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    grade = db.Column(db.String(5))

    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))

    student = db.relationship('Student', back_populates='courses')
    course = db.relationship('Course', back_populates='students')

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    courses = db.relationship('Enrollment', back_populates='student')

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    students = db.relationship('Enrollment', back_populates='course')
```

---

## 4. Query Objects

`Model.query` gives you a **BaseQuery** object.

### Examples

```python
# Get all users
users = User.query.all()

# Get one by primary key
u = User.query.get(1)

# First matching record
u = User.query.filter_by(username="john").first()

# Order results
users = User.query.order_by(User.id.desc()).all()
```

---

## 5. filter() vs filter_by()

### filter_by()

Uses **keyword arguments**.

```python
User.query.filter_by(username="john", email="a@b.com").all()
```

### filter()

Uses **SQL expressions**.

```python
User.query.filter(User.username == "john").all()
User.query.filter(User.age > 18).all()
```

Use `filter()` for OR, AND, LIKE, IN, etc.

---

## 6. SQLAlchemy Operators

Common operators:

### Comparison

```python
User.age == 21
User.age != 30
User.age > 18
User.age <= 60
```

### Text operators

```python
User.username.like('%john%')
User.email.ilike('%gmail%')
```

### Logical operators

```python
from sqlalchemy import and_, or_

User.query.filter(and_(User.age > 20, User.age < 30))
User.query.filter(or_(User.username=='a', User.username=='b'))
```

### IN operator

```python
User.query.filter(User.id.in_([1,2,3])).all()
```

### NOT IN

```python
User.query.filter(~User.id.in_([5,6])).all()
```

---

## 7. Session vs Database Querying

### Flask-SQLAlchemy Sessions

Flask-SQLAlchemy manages sessions automatically:

```python
db.session.add(obj)
# complete this himanshu
```

---

---

### Common SQLAlchemy Exceptions

Here are some frequently encountered exceptions when working with SQLAlchemy:

- **`IntegrityError`**: Raised for constraint violations (e.g., unique constraints, foreign keys).
- **`OperationalError`**: Raised for errors like database connection issues or table not found.
- **`InvalidRequestError`**: Raised when a request is not valid, such as when trying to use an invalid query or accessing a closed session.
- **`FlushError`**: Raised when there are issues with flushing data to the database, typically during `db.session.commit()`.

### **6. Best Practices for Error Handling with Flask-SQLAlchemy:**

- **Always Rollback After an Error**: Use `db.session.rollback()` to ensure that the session state is clean after a failed transaction.
- **Log Errors for Debugging**: Use logging to record errors and understand the cause of issues:

   ```python
   import logging
   logging.basicConfig(filename='error.log', level=logging.ERROR)
   
   try:
       # Some database operation
   except Exception as e:
       logging.error(f"An error occurred: {e}")
   ```
 
- **Use Specific Exception Classes**: Catch specific exceptions like `IntegrityError` to handle known issues, rather than using a generic `Exception` class.
- **Graceful User Feedback**: If handling exceptions in routes, ensure that the user receives friendly and clear feedback about what went wrong, especially for input validation errors.

---

### **7. Example: Complete Code with Error Handling:**

```python
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

with app.app_context():
    db.create_all()

@app.route('/add_user', methods=['POST'])
def add_user():
    data = request.json
    new_user = User(username=data['username'], email=data['email'])
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify(message="User added successfully"), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify(error="Username or email already exists"), 400
    except Exception as e:
        return jsonify(error=str(e)), 500

if __name__ == '__main__':
    app.run(debug=True)
```

- This example demonstrates adding a user through a POST request with error handling.
- It handles `IntegrityError` for duplicate usernames or emails and provides a custom error message.
- Other general exceptions return a 500 status code with the error message.

---

The `first_or_404` method is a handy feature provided by **Flask-SQLAlchemy** for handling queries when you want to return a single result or automatically raise a `404 Not Found` error if the query does not yield any results. This is especially useful when building APIs where you want to ensure a resource exists before proceeding with further actions.

### **8. Using `first_or_404` with Flask-SQLAlchemy:**

- **Purpose**: 
  - `first_or_404` is a method used when querying for a single record, ensuring that if no result is found, a `404 Not Found` error is automatically raised.
  - It simplifies the process of handling missing resources by combining the query and error handling in a single step.
  
- **Syntax**:
  ```python
  user = User.query.filter_by(username='john_doe').first_or_404()
  ```

  - This will attempt to retrieve the first `User` with the username `'john_doe'`.
  - If no such user exists, it will raise a `404 Not Found` error automatically.

- **Use Case**:
  - `first_or_404` is particularly useful in **RESTful APIs** when you need to retrieve a specific record and want to return a `404` response if it doesn’t exist.

- **Example**:
  ```python
  from flask import Flask, jsonify
  from flask_sqlalchemy import SQLAlchemy
  
  app = Flask(__name__)
  app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'
  app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
  db = SQLAlchemy(app)
  
  class User(db.Model):
      id = db.Column(db.Integer, primary_key=True)
      username = db.Column(db.String(80), unique=True, nullable=False)
      email = db.Column(db.String(120), unique=True, nullable=False)
  
  @app.route('/user/<int:user_id>', methods=['GET'])
  def get_user(user_id):
      # Retrieve user by ID, or return a 404 error if not found.
      user = User.query.filter_by(id=user_id).first_or_404()
      return jsonify(username=user.username, email=user.email)
  
  if __name__ == '__main__':
      app.run(debug=True)
  ```

  - In this example, if a user with the specified `user_id` does not exist, Flask will automatically return a `404` response with a default error message.
  - This eliminates the need for manual checking and error handling:
    ```python
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    ```

- **Custom Error Handling with `first_or_404`**:
  - While `first_or_404` provides a simple way to raise a `404`, you can customize the error response by catching the `404` using Flask's `@app.errorhandler`:
    ```python
    from flask import abort
    
    @app.route('/user/<int:user_id>', methods=['GET'])
    def get_user(user_id):
        user = User.query.filter_by(id=user_id).first_or_404(description='User not found')
        return jsonify(username=user.username, email=user.email)
    
    @app.errorhandler(404)
    def handle_404(e):
        return jsonify({"error": str(e)}), 404
    ```
  - In this example, if a user is not found, `first_or_404` will return a `404` response with the message `'User not found'`.

### **Summary of `first_or_404`:**

| **Feature**      | **Description**                                              |
| ---------------- | ------------------------------------------------------------ |
| **Purpose**      | Retrieve a single record or automatically raise a `404 Not Found` error if no result is found. |
| **Use Case**     | Useful in RESTful APIs for simplifying retrieval of a resource with automatic error handling. |
| **Syntax**       | `User.query.filter_by(attribute=value).first_or_404()`       |
| **Custom Error** | You can provide a custom `description` for the error message or handle it with `@app.errorhandler`. |

### **9. How `first_or_404` Fits into Error Handling:**

- **Advantages**:
  - It makes the code cleaner by combining querying and error handling.
  - Reduces boilerplate code needed for checking if a resource exists.
  - Integrates seamlessly with Flask's built-in error handling mechanisms.

- **Combining with `try-except`**:
  - Although `first_or_404` simplifies a lot of error handling, you can still use `try-except` blocks if you want to catch the `404` for additional custom logic:
    ```python
    from sqlalchemy.exc import SQLAlchemyError
    
    @app.route('/user/<int:user_id>', methods=['GET'])
    def get_user(user_id):
        try:
            user = User.query.filter_by(id=user_id).first_or_404()
            return jsonify(username=user.username, email=user.email)
        except SQLAlchemyError as e:
            return jsonify({"error": str(e)}), 500
    ```

---

### **Final Notes Summary:**

1. **Queries**:
   - Add, retrieve, update, and delete records.
   - Use `first_or_404` for simple retrievals with automatic `404` handling.
   
2. **Error Handling**:
   - Use `try-except` blocks for robust error handling.
   - Roll back transactions with `db.session.rollback()` to avoid invalid states.
   - Handle specific SQLAlchemy exceptions like `IntegrityError` and `OperationalError`.
   
3. **Custom Error Messages**:
   - Use `@app.errorhandler` for global error handling and to customize error responses.

4. **Example with `first_or_404`**:
   - Simplifies API development by reducing manual checks for resource existence.
   - Ensures cleaner and more readable code when working with resource retrieval.

By understanding and using `first_or_404` along with other error handling practices, you can make your Flask-SQLAlchemy application more robust and user-friendly.

This document covered:

* Flask-SQLAlchemy ORM setup
* Relationship types
* Association tables
* Query objects
* Filters and operators
* Session handling

---
