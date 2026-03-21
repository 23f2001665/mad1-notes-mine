
4. **Flask-RESTful API**: A structured and scalable way to build RESTful APIs using the Flask-RESTful extension. It organizes endpoints using class-based resources, making it easier to manage complex APIs.

   - Example:
     ```python
     from flask_restful import Resource, Api

     class Hello(Resource): #remember class from flask_sqlalchemy it aslo takes db.Model similar to Resource here
         def get(self):
             return {"message": "Hello, World!"}
     ```

This hierarchy shows how API development progresses from a simple function-based approach to a more scalable, structured Flask-RESTful approach.

## 6. Difference Between Flask Route and Flask-RESTful

| Feature           | Flask Route                         | Flask-RESTful                                               |
| ----------------- | ----------------------------------- | ----------------------------------------------------------- |
| API Creation      | Uses `@app.route` decorator         | Uses `Resource` class and `add_resource` method             |
| HTTP Methods      | Needs explicit function definitions | Handles multiple HTTP methods using class methods           |
| Code Organization | Less structured, function-based     | More structured, class-based                                |
| Scalability       | Can become complex with many routes | Easier to manage as API grows                               |
| Data Parsing      | Uses `request.json` for input       | Uses `reqparse.RequestParser` for structured input handling |
| Response Format   | Uses `jsonify()` for response       | Returns a dictionary, automatically converted to JSON       |

### Code Comparison: Jinja2 vs Flask-RESTful

#### Using Jinja2 (`render_template`)

```python
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
```

#### Using Flask-RESTful

```python
from flask import Flask
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

class Home(Resource):
    def get(self):
        return {"message": "Welcome to the API"}

api.add_resource(Home, '/')

if __name__ == '__main__':
    app.run(debug=True)
```

## 7. HTTP Methods and Implementation

HTTP methods allow interaction with APIs. Below is a comparison of Flask route and Flask-RESTful for different HTTP methods.

### Flask Route Example

```python
from flask import Flask, request, jsonify

app = Flask(__name__)
users = {}

@app.route('/user/<string:user_id>', methods=['GET'])
def get_user(user_id):
    return jsonify(users.get(user_id, "User not found"))

@app.route('/user/<string:user_id>', methods=['POST'])
def create_user(user_id):
    users[user_id] = request.json
    return jsonify({"message": "User added", "data": users[user_id]})

@app.route('/user/<string:user_id>', methods=['PUT'])
def update_user(user_id):
    users[user_id] = request.json
    return jsonify({"message": "User updated", "data": users[user_id]})

@app.route('/user/<string:user_id>', methods=['DELETE'])
def delete_user(user_id):
    users.pop(user_id, None)
    return jsonify({"message": "User deleted"})

if __name__ == '__main__':
    app.run(debug=True)
```

### HTML Form Restriction Example

```html
<form action="/user/1" method="post">
    <input type="text" name="name" placeholder="Enter Name">
    <input type="submit" value="Submit">
</form>
```

Note: HTML forms do not support `PUT` or `DELETE` methods.

### Flask-RESTful with Database Example

```python
from flask import Flask, request, jsonify
from flask_restful import Resource, Api, reqparse
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)
api = Api(app)

class UserModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))

with app.app_context():
    db.create_all()

class User(Resource):
    def get(self, user_id):
        user = UserModel.query.get(user_id)
        if user:
            return jsonify({"id": user.id, "name": user.name, "email": user.email})
        return jsonify({"message": "User not found"})

    def post(self, user_id):
        data = request.get_json()
        user = UserModel(id=user_id, name=data['name'], email=data['email'])
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "User added", "data": data})

    def put(self, user_id):
        user = UserModel.query.get(user_id)
        if not user:
            return jsonify({"message": "User not found"})
        data = request.get_json()
        user.name = data.get('name', user.name)
        user.email = data.get('email', user.email)
        db.session.commit()
        return jsonify({"message": "User updated", "data": {"name": user.name, "email": user.email}})

    def delete(self, user_id):
        user = UserModel.query.get(user_id)
        if not user:
            return jsonify({"message": "User not found"})
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "User deleted"})

api.add_resource(User, '/user/<int:user_id>')

if __name__ == '__main__':
    app.run(debug=True)
```


## 8. Fetch API (Client-Side Usage)

```javascript
fetch('http://127.0.0.1:5000/user/1')
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error('Error:', error));
```


### Example of a Simple REST API
To illustrate the REST concept, let’s create a simple API using Flask’s route decorator. This API will allow us to retrieve and create users.

### Install Flask-RESTful
```sh
pip install flask flask-restful flask-sqlalchemy
```

#### Using Flask Route with `jsonify`:
```python
from flask import Flask, jsonify, request

app = Flask(__name__)

users = {"1": {"name": "Alice", "email": "alice@example.com"}}

@app.route('/user/<string:user_id>', methods=['GET'])
def get_user(user_id):
    return jsonify(users.get(user_id, "User not found"))

@app.route('/user/<string:user_id>', methods=['POST'])
def create_user(user_id):
    users[user_id] = request.json
    return jsonify({"message": "User added", "data": users[user_id]})

if __name__ == '__main__':
    app.run(debug=True)
```

### Another Way to Create APIs: Using `Flask` with `Response` Object
Instead of using `jsonify`, we can directly use the `Response` object to create API responses:

```python
from flask import Flask, Response, request
import json

app = Flask(__name__)

users = {"1": {"name": "Alice", "email": "alice@example.com"}}

@app.route('/user/<string:user_id>', methods=['GET'])
def get_user(user_id):
    response = json.dumps(users.get(user_id, {"error": "User not found"}))
    return Response(response, status=200, mimetype='application/json')

@app.route('/user/<string:user_id>', methods=['POST'])
def create_user(user_id):
    users[user_id] = request.json
    response = json.dumps({"message": "User added", "data": users[user_id]})
    return Response(response, status=201, mimetype='application/json')

if __name__ == '__main__':
    app.run(debug=True)
```


```python
from flask import Flask, request, jsonify
from flask_restful import Resource, Api, reqparse
from flask_sqlalchemy import SQLAlchemy
```
- `Flask`: The core Flask framework for building the web application.
- `request`: Used to handle incoming request data (e.g., JSON).
- `jsonify`: Converts Python dictionaries into JSON responses.
- `flask_restful.Resource`: A class-based approach to defining API endpoints.
- `flask_restful.Api`: Wraps the Flask app to support RESTful routes.
- `reqparse`: Helps validate and parse request arguments.
- `flask_sqlalchemy.SQLAlchemy`: SQLAlchemy ORM for database operations.

---

### **2. Flask App and Database Configuration**
```python
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)
api = Api(app)

with app.app_context():
    db.create_all()

```
- Creates a Flask app instance.
- Configures the app to use an SQLite database (`users.db`).
- Initializes SQLAlchemy (`db`) for ORM functionality.
- Initializes Flask-RESTful API (`api`).
- Creates a context with the app for database operations. and creates the database tables.

---

### **3. Defining the UserModel (Database Table)**
```python
class UserModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
```
- `UserModel`: Represents a `users` table in the database.
- `id`: An integer column that acts as the primary key.
- `name`: A string column for storing the user’s name.
- `email`: A string column for storing the user’s email.

---

### **4. Creating the User Resource**
```python
class User(Resource):
    def get(self, user_id):
        user = UserModel.query.get(user_id)
        if user:
            return jsonify({"id": user.id, "name": user.name, "email": user.email})
        return jsonify({"message": "User not found"})
```
- `get(self, user_id)`: Fetches a user by ID.
- `UserModel.query.get(user_id)`: Retrieves the user from the database.
- If the user exists, returns their details as JSON.
- If not found, returns a JSON message: `{"message": "User not found"}`.

---

### **5. Handling User Creation**
```python
    def post(self, user_id):
        data = request.get_json()
        user = UserModel(id=user_id, name=data['name'], email=data['email'])
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "User added", "data": data})
```
- `post(self, user_id)`: Handles `POST` requests to add a new user.
- `request.get_json()`: Extracts JSON data from the request body.
- Creates a new `UserModel` object and adds it to the database.
- Commits changes using `db.session.commit()`.
- Returns a success message.

---

### **6. Updating an Existing User**
```python
    def put(self, user_id):
        user = UserModel.query.get(user_id)
        if not user:
            return jsonify({"message": "User not found"})
        data = request.get_json()
        user.name = data.get('name', user.name)
        user.email = data.get('email', user.email)
        db.session.commit()
        return jsonify({"message": "User updated", "data": {"name": user.name, "email": user.email}})
```
- `put(self, user_id)`: Updates an existing user.
- Fetches the user by `user_id`. If not found, returns a message.
- Uses `data.get('key', default_value)` to update only provided fields.
- Saves changes using `db.session.commit()`.
- Returns the updated user details.

---

### **7. Deleting a User**
```python
    def delete(self, user_id):
        user = UserModel.query.get(user_id)
        if not user:
            return jsonify({"message": "User not found"})
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "User deleted"})
```
- `delete(self, user_id)`: Deletes a user.
- Fetches the user by `user_id`. If not found, returns a message.
- Deletes the user from the database using `db.session.delete(user)`.
- Commits the deletion using `db.session.commit()`.
- Returns a success message.

---

### **8. Adding Resource to the API**
```python
api.add_resource(User, '/user/<int:user_id>')
```
- Maps the `User` class to the `/user/<user_id>` route.
- `<int:user_id>` ensures `user_id` is an integer.

---

### **9. Running the Application**
```python
if __name__ == '__main__':
    app.run(debug=True)
```

- `app.run(debug=True)`: Starts the Flask server in debug mode.


---

### **`json.dumps()`**
`json.dumps()` converts a Python dictionary into a JSON-formatted string.

```python
import json

data = {"name": "Alice", "age": 30}
json_string = json.dumps(data)
print(json_string)  # Output: {"name": "Alice", "age": 30}
```

📌 **Use case:** Serializing Python objects for storage, logging, or API responses.

---

### **`flask.Response` in Flask**
`Response` is used to **return HTTP responses** with custom headers, content, and status codes.

```python
from flask import Flask, Response, jsonify

app = Flask(__name__)

@app.route("/")
def custom_response():
    data = {"message": "Hello, Flask!"}
    response = Response(json.dumps(data), status=200, mimetype="application/json")
    return response

if __name__ == "__main__":
    app.run(debug=True)
```

📌 **Use case:** When you need to manually control the HTTP response.

---

### **`flask_restful.Resource`**
In **Flask-RESTful**, `Resource` is a class-based way to define REST API endpoints.

```python
from flask import Flask
from flask_restful import Api, Resource

app = Flask(__name__)
api = Api(app)

class HelloWorld(Resource):
    def get(self):
        return {"message": "Hello, Flask-RESTful!"}

api.add_resource(HelloWorld, "/")

if __name__ == "__main__":
    app.run(debug=True)
```

📌 **Use case:** `Resource` makes REST API development structured and reusable.

---

### **Final Thoughts**
- ✅ **Use `json.dumps()`** when converting Python objects to JSON strings.
- ✅ **Use `Response`** when customizing Flask API responses.
- ✅ **Use `Resource` (Flask-RESTful)** to create structured REST APIs.
- ✅ **Use JSON for APIs**, while **YAML is better for configurations**.

---

### **`json.dump()` vs `json.dumps()`**
Both functions **convert Python objects to JSON format**, but they differ in their output.

| Function | Purpose | Output |
|----------|---------|--------|
| `json.dumps()` | Converts Python object to JSON **string** | Returns a string |
| `json.dump()` | Writes JSON data **to a file** | Saves directly to a file |

#### **Example: `json.dump()`**
Writes JSON data to a file.

```python
import json

data = {"name": "Alice", "age": 30}

with open("data.json", "w") as file:
    json.dump(data, file)  # Saves JSON directly to data.json
```

📌 **Use case:** Storing JSON data in files.

---

### **`flask.jsonify()`**
`jsonify()` is a Flask helper function that **automatically converts Python dictionaries into JSON responses** and sets the correct `Content-Type` (`application/json`).

#### **Example: `jsonify()`**
```python
from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def json_response():
    data = {"message": "Hello, Flask!"}
    return jsonify(data)  # Converts to JSON and sets Content-Type

if __name__ == "__main__":
    app.run(debug=True)
```

🔹 **Advantages over `json.dumps()` in Flask:**
1. **Automatically sets `Content-Type: application/json`**
2. **Handles Unicode characters correctly**
3. **Handles lists and tuples properly**

---

### **`JSON.stringify()` (JavaScript)**
`JSON.stringify()` is a JavaScript function that **converts a JavaScript object into a JSON string**.

#### **Example: `JSON.stringify()`**
```javascript
const data = { name: "Alice", age: 30 };
const jsonString = JSON.stringify(data);
console.log(jsonString);  // Output: {"name":"Alice","age":30}
```

📌 **Use case:** Sending JSON data in AJAX requests or APIs.

---

| Function | Language | Purpose |
|----------|----------|---------|
| `json.dumps()` | Python | Converts Python object to JSON string |
| `json.dump()` | Python | Writes JSON data to a file |
| `jsonify()` | Flask (Python) | Converts dictionary to JSON and sets `Content-Type` |
| `JSON.stringify()` | JavaScript | Converts JavaScript object to JSON string |

---

Sure! In **Flask-RESTful**, `marshal` and `marshal_with` are used for **formatting** API responses according to a specified structure. They help in ensuring that API responses follow a consistent format.

---

## **`marshal` and `marshal_with` in Flask-RESTful**

| Feature           | `marshal` | `marshal_with` |
|------------------|------------|---------------|
| Type            | Function | Decorator |
| Usage          | Called manually | Used above a method automatically |
| When to Use | If you need to format multiple responses | If formatting is always required for a function's return value |
```python
from flask_restful import marshal, fields

# Define response structure
resource_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'age': fields.Integer
}

# Sample data
data = {'id': 1, 'name': 'John', 'age': 30, 'extra_field': 'Not needed'}

# Use marshal to format data
formatted_data = marshal(data, resource_fields)

print(formatted_data)  # Output: {'id': 1, 'name': 'John', 'age': 30}
```
**Extra fields** (`extra_field`) not mentioned in `resource_fields` are **ignored**.

```python
from flask import Flask
from flask_restful import Api, Resource, fields, marshal_with

app = Flask(__name__)
api = Api(app)

# Define response structure
resource_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'age': fields.Integer
}

class User(Resource):
    @marshal_with(resource_fields)  # Apply formatting automatically
    def get(self):
        user_data = {'id': 1, 'name': 'John', 'age': 30, 'extra_field': 'Ignored'}
        return user_data  # No need to call marshal manually

api.add_resource(User, '/user')

if __name__ == '__main__':
    app.run(debug=True)
```
The response will automatically be:
```json
{
    "id": 1,
    "name": "John",
    "age": 30
}
```