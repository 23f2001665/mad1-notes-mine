# Flask Restful and API Basics

In this section, we will learn about Flask Restful and how to create APIs using it. Flask Restful is an extension for Flask that adds support for quickly building REST APIs. It provides a simple way to create API endpoints and handle HTTP requests.

API stands for Application Programming Interface. It is a set of rules and protocols that allows different software applications to communicate with each other. In the context of web development, APIs are often used to allow clients (like web browsers or mobile apps) to interact with a server and access data or perform actions.

## SSR, CSR Applications and Need of APIs

There are two main components of an application:

- **Frontend**: The part of the application that interacts with the user. It is responsible for displaying data and handling user interactions. Examples of frontend technologies include HTML, CSS, JavaScript, and frontend frameworks like React, Angular, and Vue.js.
- **Backend**: The part of the application that runs on the server. It is responsible for processing requests, managing data, and performing business logic. Examples of backend technologies include Python, Node.js, Ruby, and backend frameworks like Flask, Django, and Express.

There are two main types of applications based on how the frontend and backend interact:

- **Server-Side Rendered (SSR) Applications**: In SSR applications, the server generates the HTML for each page and sends it to the client. The client then renders the page in the browser. This approach is simpler to implement but can be less efficient for dynamic content and may result in slower page loads due to the need to reload the entire page for each interaction.
- **Client-Side Rendered (CSR) Applications**: In CSR applications, the server provides an API that the client can use to fetch data. The client is responsible for rendering the HTML and updating the page dynamically based on user interactions. This approach can provide a better user experience and faster interactions, but it requires more complex frontend development. In CSR applications, client ask for very specific data from the server and the server responds with only that data, which is used to update the page dynamically without reloading the entire page. This is where APIs come into play. APIs allow the frontend to communicate with the backend and fetch the necessary data to update the user interface.

*API is a contract between the frontend and backend that defines how they will communicate with each other. It specifies the endpoints, request methods, and data formats that the frontend can use to interact with the backend.*

## Creating a API resource in plain Flask

Before we dive into Flask Restful, let's see how we can create an API resource using plain Flask. Here's an example of how to create a simple API that returns a list of items (and accepts a new one with `POST`):

```python
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/items', methods=['GET', 'POST'])
def items():
    if request.method == 'GET':
        return jsonify({'items': ['item1', 'item2', 'item3']})
    elif request.method == 'POST':
        # Here we would handle the logic for creating a new item based on the data sent in the request body.
        return jsonify({'message': 'Item created successfully'}), 201

if __name__ == '__main__':
    app.run(debug=True)
```

The `methods` list decides which requests reach the function: with `methods=['GET']` a `POST` request is answered with **405 Method Not Allowed** and the `POST` branch would never run.

Now we can run this script and access the API by navigating to `http://localhost:5000/items` in our web browser or using a tool like `Postman` or `Thunder Client` or we can use `curl`. We should see a JSON response with the list of items.

#### Browser

![Browser showing JSON response](../static/week6/6-browser.png)

#### Thunder Client

![Thunder Client showing JSON response](../static/week6/6-thunder-client.png)

#### curl

![curl showing JSON response](../static/week6/6-curl.png)

Here we have used the `@app.route` decorator to define the API endpoints and `jsonify` to return JSON responses. This approach works, but as our API grows in complexity, it can become difficult to manage and maintain. This is where Flask Restful comes in handy, providing a more structured way to create API resources and handle different HTTP methods.

### Browser Limitations and Api Testing Tools

Before we move on to Flask Restful, it's important to note that while we can test our API using a web browser, it has limitations. Browsers are primarily designed for rendering HTML and may not handle all HTTP methods (like POST, PUT, DELETE) or allow us to easily send data in the request body of a **html form**.

Without js feature like `fetch`, browser can only use `get` method (default) or `post` method in a **html form**. For testing APIs, we can use tools like:

- Postman
- Thunder Client
- curl
- HTTPie
- fetch (from javascript)
- axios (from javascript)
- requests (from python)

These tools allows us to send data and headers in our requests using different HTTP methods, making it easier to test our API endpoints and ensure they are working correctly. They also provide features like saving requests, organizing them into collections, and generating code snippets for different programming languages, which can be very helpful during development.

## Flask Restful

Flask Restful provides a more structured way to create API resources. It allows us to define resources as classes and handle different HTTP methods (GET, POST, PUT, DELETE) in a more organized manner. This can make our code cleaner and easier to maintain, especially as our API grows in complexity.

### Setting Up Flask Restful

To get started with Flask Restful, we need to install it first. we can do this using pip:

```bash
pip install flask-restful
```

or if you are using uv:

```bash
uv add flask-restful
```

### Creating a Basic API

Once we have Flask Restful installed, we can create a basic API. Here’s an example of how to create a simple API that returns a list of items:

```python
from flask import Flask
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

class ItemList(Resource):
    def get(self):
        return {'items': ['item1', 'item2', 'item3']}
        
api.add_resource(ItemList, '/items')

if __name__ == '__main__':
    app.run(debug=True)
```

In this example, we define a resource class called `ItemList` that has a `get` method. This method returns a JSON response containing a list of items. We then add this resource to our API and specify the endpoint `/items`.

### Running the API

To run the API, simply execute the script. We can then access the API by navigating to `http://localhost:5000/items` in our **web browser** or using a tool like `Postman` or `Thunder Client` or we can use `curl`. We should see a JSON response with the list of items.

```json
{
    "items": ["item1", "item2", "item3"]
}
```

## Flask Restful Features

Flask Restful provides several features that make it easier to build APIs:

<details>
<summary>click to expand</summary>

**What Flask Restful provides**

- **Resource Classes**: We can define resources as classes (they are Flask `MethodView`s), with one method per HTTP verb, which allows us to organize our code better.
- **Routing helpers**: `api.add_resource(Resource, url1, url2, ...)` attaches a resource to one or several URLs.
- **Request Parsing**: The `reqparse` module extracts and validates data from incoming requests (it is slated for removal, see the note below).
- **Output formatting**: `fields`, `marshal` and `marshal_with` turn Python objects into a fixed JSON structure.
- **Automatic JSON responses**: A dict or list returned from a resource method becomes a JSON response, and a tuple `(data, status_code, headers)` sets the status code and headers. Other formats can be added with `api.representation`.
- **Error Handling**: Errors are returned as JSON (`{"message": ...}`), `abort(404, message='...')` is a shortcut to raise them and `Api(errors=...)` customises them.
- **Decorators per resource**: `method_decorators = [...]` on a resource applies decorators (for example a login check) to all its methods.
- **Integration with Flask**: Since Flask Restful is an extension of Flask, we can still use the rest of Flask (`request`, `app.errorhandler`, blueprints, other extensions).

**What it does not provide** (we have to write it ourselves or add another library)

- **Authentication**: not built in; use a decorator or an extension.
- **Pagination**: not built in; we implement it with query parameters (`?page=2&limit=10`).
- **Documentation (Swagger / OpenAPI)**: not generated by Flask Restful; other libraries such as Flask-RESTX, flask-smorest or apispec can produce it (see the OpenAPI page).
- **Testing tools**: none of its own; use Flask's `app.test_client()`.

</details>

In summary, Flask Restful is a small extension for Flask that makes it easier to build REST APIs. It provides a structured way to define resources and handle HTTP requests, making our code cleaner and more maintainable.

## Resource Classes and HTTP Methods

In Flask Restful, we define resources as classes that inherit from the `Resource` class. Each resource class can have methods that correspond to different HTTP methods (GET, POST, PUT, DELETE). This allows us to handle different types of requests in a clean and organized way. After defining our resource classes, we need to add them to our API with the appropriate endpoints. REST usually has two kinds of URLs, the **collection** (`/items`) and a **single item** (`/items/5`), so we define two resource classes:

```python
from flask import Flask
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

class ItemList(Resource):          # the collection: /items
    def get(self):
        return {'items': ['item1', 'item2', 'item3']}

    def post(self):
        return {'message': 'Item created successfully'}, 201

class Item(Resource):              # one item: /items/<item_id>
    def get(self, item_id):
        return {'item': f'item{item_id}'}

    def put(self, item_id):
        return {'message': f'Item {item_id} updated successfully'}

    def delete(self, item_id):
        return {'message': f'Item {item_id} deleted successfully'}

api.add_resource(ItemList, '/items')
api.add_resource(Item, '/items/<int:item_id>')

if __name__ == '__main__':
    app.run(debug=True)
```

In this example, we have defined a resource class `ItemList` for the URL `/items` (GET to list, POST to create) and a resource class `Item` for the URL `/items/<int:item_id>` (GET, PUT and DELETE of one item). A method that the class does not define (for example `POST /items/5`) is answered with **405 Method Not Allowed**.

> [!NOTE]
> **A Question for you**
>
> - Think why we have two resources (and two URLs) for the same kind of thing?
> - Why post method does not have an item_id in the endpoint?

<details>
<summary>View Answer</summary>

We have two URLs because the POST method is used to create a new item in the *collection* and it does not require an item_id in the endpoint. The item_id is typically generated by the server when a new item is created. On the other hand, the GET, PUT and DELETE methods require an item_id in the endpoint to specify which item we want to retrieve, update, or delete. This allows us to manage individual items in our API using their unique identifiers.

</details>

> [!WARNING]
> **Why not one class on both URLs?** `api.add_resource(Item, '/item/<int:item_id>', '/item')` is allowed, but the same methods are then called for both URLs, with different arguments. With `def get(self, item_id)` the request `GET /item` calls `get()` without `item_id`, and `POST /item/5` calls `post(item_id=5)` on a method that takes none: Python raises a `TypeError` and the client gets **500 Internal Server Error**. If we really want one class, every method needs a default (`def get(self, item_id=None)`) and has to handle both cases.

In summary, resource classes in Flask Restful allow us to define how our API will handle different HTTP methods for specific endpoints. This structured approach makes it easier to manage our API and ensures that our code is organized and maintainable.

## Request Parsing

Request parsing is the process of extracting data from incoming HTTP requests. Flask Restful provides a built-in request parsing mechanism that allows us to easily extract data from requests and validate it. This is especially useful when we want to handle POST or PUT requests where the client sends data to the server.

Data sent by the client can be in various formats, such as JSON, form data, or query parameters and can be malicious. Therefore, it is important to validate the incoming data to ensure that it meets our requirements and does not cause any issues in our application.

Flask Restful provides a `reqparse` module that allows us to define the expected parameters and their types. We can also specify whether a parameter is required or optional. Here's an example of how to use `reqparse` to parse incoming data:

```python
from flask import Flask
from flask_restful import Resource, Api, reqparse

app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('name', type=str, required=True, help='Name of the item is required')
parser.add_argument('price', type=float, required=True, help='Price of the item is required')

class ItemList(Resource):
    def post(self):
        args = parser.parse_args()  # process the incoming request and extract the data based on the defined arguments
        
        name = args['name']
        price = args['price']
        
        return {'message': f'Item {name} with price {price} created successfully'}, 201

api.add_resource(ItemList, '/items')

if __name__ == '__main__':
    app.run(debug=True)
```

In this example, we define a POST method for the `ItemList` resource. We create a `RequestParser` object and add expected parameters (`name` and `price`) with their types and validation rules. When a POST request is made to the `/items` endpoint, the parser will extract the data from the request, validate it, and return an appropriate response. If a required parameter is missing or has the wrong type, Flask Restful will automatically return an error message with a 400 status code.

By default the arguments are read from the **JSON body** of the request. What the parser above answers:

| Request to `POST /items` | Response |
| ------------------------ | -------- |
| JSON body `{"name": "pen", "price": 1.5}` | `201 {"message": "Item pen with price 1.5 created successfully"}` |
| JSON body without `name` | `400 {"message": {"name": "Name of the item is required"}}` |
| JSON body `{"name": "pen", "price": "abc"}` | `400 {"message": {"price": "Price of the item is required"}}` (the `help` text is shown for any problem with that argument) |
| HTML form data, query string, or no body | `415 Unsupported Media Type` (the parser looked for JSON) |

To read form data or the query string we must say so with the `location` argument (see the frontend example below).

<details>
<summary>More about Reqparse Object</summary>

The `RequestParser` object in Flask Restful is a powerful tool for handling and validating incoming request data. It allows us to define the expected parameters, their types, and validation rules in a clean and organized way. Here are some key features of the `RequestParser` object:

### Adding Arguments

We can add expected parameters using the `add_argument` method. This method takes the name of the parameter, its type, whether it is required, and an optional help message for validation errors. Each argument can have various parameters defining the rules for the expected data:

- `type`: Specifies the expected data type (e.g., `str`, `int`, `float`).
- `required`: Indicates whether the parameter is required (default is `False`).
- `help`: Provides a custom error message if the validation fails.
- `default`: Specifies a default value for the parameter if it is not provided in the request.
- `choices`: Defines a list of valid values for the parameter.
- `location`: Specifies where to look for the parameter: `'json'`, `'args'` (query string), `'form'`, ... or a list such as `['form', 'args']`. The default is the JSON body.

### Parsing Arguments

Once we have defined our expected parameters, we can call the `parse_args` method to extract the data from the incoming request. This method will validate the data based on the rules we defined and return a dictionary of the parsed arguments. If any validation fails, it will automatically return an error response with a 400 status code.

### Example of Using `RequestParser`

```python
from flask import Flask
from flask_restful import Resource, Api, reqparse

app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('name', type=str, required=True, help='Name of the item is required')
parser.add_argument('price', type=float, required=True, help='Price of the item is required')
parser.add_argument('category', type=str, choices=['electronics', 'clothing', 'food'], help='Category must be one of: electronics, clothing, food')

class ItemList(Resource):
    def post(self):
        
        args = parser.parse_args()
        
        name = args['name']
        price = args['price']
        category = args['category']
        
        return {'message': f'Item {name} with price {price} in category {category} created successfully'}, 201

api.add_resource(ItemList, '/items')

if __name__ == '__main__':
    app.run(debug=True)
```

A missing optional argument is `None` (`category` above); a value outside `choices` gives `400 {"message": {"category": "Category must be one of: electronics, clothing, food"}}`.

> [!WARNING]
> **Deprecation Note**
>
> The `reqparse` module in Flask Restful is slated for removal (the Flask-RESTful documentation says so). It is recommended to use other libraries such as `marshmallow` or `pydantic` for request parsing and validation in modern Flask applications. These libraries provide more powerful and flexible ways to handle data validation and serialization, making them a better choice for new projects.

</details>

## Frontend Integration

Now that we know how to create an API and parse the incoming requests, we can integrate our Flask Restful API with a frontend application. This allows us to create dynamic web applications that can interact with our API to fetch and display data, as well as send data back to the server.

For now let's assume that we are handling only form data in our API. We can create a simple HTML form that allows users to submit data to our API. Here's an example of how to create a basic HTML form that interacts with our Flask Restful API:

#### templates/form.html

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Flask Restful API Form</title>
</head>
<body>
    <h1>Submit Item</h1>
    <form action="/items" method="post">
        <label for="name">Item Name:</label>
        <input type="text" id="name" name="name" required><br><br>
        <label for="price">Price:</label>
        <input type="number" id="price" name="price" step="0.01" required><br><br>
        <input type="submit" value="Submit">
    </form>
</body>
</html>
```

python code for serving the form and handling the form data in the API:

```python
from flask import Flask, render_template
from flask_restful import Resource, Api, reqparse

app = Flask(__name__)
api = Api(app)

item_parser = reqparse.RequestParser()
item_parser.add_argument('name', type=str, required=True, location='form', help='Name of the item is required')
item_parser.add_argument('price', type=float, required=True, location='form', help='Price of the item is required')

class ItemList(Resource):
    def post(self):
        args = item_parser.parse_args()
        name = args['name']
        price = args['price']
        return {'message': f'Item {name} with price {price} created successfully'}, 201

api.add_resource(ItemList, '/items')

@app.route('/')
def form():
    return render_template('form.html')   # a normal Flask route serves the page

if __name__ == '__main__':
    app.run(debug=True)
```

In this example, we have created a simple HTML form that allows users to submit an item name and price. The form sends a POST request to the `/items` endpoint of our Flask Restful API when the user submits the form. The API then parses the incoming data using `reqparse`, validates it, and returns a response indicating that the item was created successfully (the browser shows that JSON response). This integration allows us to create a dynamic web application that can interact with our API to manage items.

> [!IMPORTANT]
> The browser sends an HTML form as `application/x-www-form-urlencoded`, but a parser without `location` looks only in the JSON body and answers `415 Unsupported Media Type`. That is why the arguments above say `location='form'`. A parser reads from one kind of source: with `location='form'` a JSON request is in turn rejected (`400`, the form field is missing), so an API for a JSON client and one for an HTML form use different parsers. (A list such as `location=['form', 'args']` combines form data with the query string.)

## Database Integration

Flask Restful can be easily integrated with databases to store and retrieve data for our API. We can use libraries like SQLAlchemy or Flask-SQLAlchemy to manage our database interactions. This allows us to create more complex APIs that can handle persistent data storage. For example, we can define a database model for our items and use it to create, read, update, and delete items in our API. Here's a simple example of how to integrate Flask Restful with a database using Flask-SQLAlchemy:

```python
from flask import Flask
from flask_restful import Resource, Api, reqparse
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///items.db'
db = SQLAlchemy(app)
api = Api(app)

user_parser = reqparse.RequestParser()
user_parser.add_argument('name', type=str, required=True, help='Name of the user is required')

purchase_parser = reqparse.RequestParser()
purchase_parser.add_argument('item_name', type=str, required=True, help='Name of the item is required')

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    purchase = db.relationship('Purchase', back_populates='user', lazy='selectin')

class Purchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(80), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', back_populates='purchase', lazy='joined')
    # I hope you remember these parameters from the previous weeks. If not, please review the SQLAlchemy section in week 5.

class UserList(Resource):
    def post(self):
        args = user_parser.parse_args()
        user = User(name=args['name'])
        db.session.add(user)
        db.session.commit()
        return {'message': f'User {user.name} created successfully', 'id': user.id}, 201

class UserApi(Resource):
    def get(self, user_id):
        user = db.session.get(User, user_id)
        if user:
            return {'user': user.name, 'purchases': [purchase.item_name for purchase in user.purchase]}
        else:
            return {'message': 'User not found'}, 404

    def patch(self, user_id):
        user = db.session.get(User, user_id)
        if user:
            args = user_parser.parse_args()
            user.name = args['name']
            db.session.commit()
            return {'message': f'User {user.name} updated successfully'}
        else:
            return {'message': 'User not found'}, 404

class UserItemApi(Resource):
    # here in post request we are taking user_id as a path parameter and item details in the request body. We will use these details to create a new purchase record in the database.
    def post(self, user_id):
        user = db.session.get(User, user_id)
        if not user:
            return {'message': 'User not found'}, 404

        args = purchase_parser.parse_args()
        new_purchase = Purchase(item_name=args['item_name'], user=user)
        db.session.add(new_purchase)
        db.session.commit()

        return {'message': f'Item {args["item_name"]} purchased by user {user.name} successfully'}, 201

class ItemApi(Resource):
    def get(self, item_id):
        item = db.session.get(Purchase, item_id)
        if item:
            return {'item': item.item_name, 'user': item.user.name}
        else:
            return {'message': 'Item not found'}, 404

    def delete(self, item_id):
        item = db.session.get(Purchase, item_id)
        if item:
            db.session.delete(item)
            db.session.commit()
            return {'message': 'Item deleted successfully'}
        else:
            return {'message': 'Item not found'}, 404

api.add_resource(UserList, '/user')
api.add_resource(UserApi, '/user/<int:user_id>')
api.add_resource(UserItemApi, '/user/<int:user_id>/item')
api.add_resource(ItemApi, '/item/<int:item_id>')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create the database tables
    app.run(debug=True)
```

In this example, we have defined two database models: `User` and `Purchase`, and four resource classes. `UserList` creates a user (`POST /user`), `UserApi` reads and updates one user (`GET`/`PATCH /user/<user_id>`), `UserItemApi` creates a purchase for a user (`POST /user/<user_id>/item`) and `ItemApi` reads or deletes one purchase (`GET`/`DELETE /item/<item_id>`). Every resource class must be added to the API with `api.add_resource`, otherwise its URL does not exist. This integration with a database allows us to create a more dynamic and persistent API.

## Response Handling

In Flask Restful, we can easily return responses to clients in JSON format. When we return a dictionary from our resource methods, Flask Restful automatically converts it to JSON and sets the appropriate content type. We can also specify the HTTP status code for our responses.

For example, when we create a new item in our API, we can return a success message along with a 201 status code to indicate that the item was created successfully:

```python
return {'message': f'Item {name} with price {price} created successfully'}, 201
```

In this example, we are returning a JSON response with a message and a status code of 201, which indicates that the item was created successfully. Flask Restful will handle the conversion to JSON and set the appropriate headers for us. We can also return different status codes based on the outcome of our operations. For example, if we try to retrieve an item that does not exist, we can return a 404 status code to indicate that the item was not found:

```python
return {'message': 'Item not found'}, 404
```

### marshalling the response

Flask Restful also provides a way to marshal our responses using the `marshal_with` decorator. This allows us to define a structure for our responses and ensure that they are consistent across our API. We can define a resource field structure and use it to format our responses. A field reads the attribute with the same name from the returned object (or the key of a dictionary); `attribute='...'` reads a differently named one. Here's an example of how to use `marshal_with`:

```python
from flask import Flask
from flask_restful import Resource, Api, fields, marshal_with, abort

app = Flask(__name__)
api = Api(app)

class Purchase:  # stands in for the database model of the previous section
    def __init__(self, id, item_name, user_name):
        self.id = id
        self.item_name = item_name
        self.user_name = user_name

purchases = {1: Purchase(1, 'pen', 'Alice')}

item_fields = {
    'id': fields.Integer,
    'name': fields.String(attribute='item_name'),   # output key "name" reads the attribute item_name
    'user': fields.String(attribute='user_name'),
}

class ItemApi(Resource):
    @marshal_with(item_fields)
    def get(self, item_id):
        item = purchases.get(item_id)
        if item:
            return item
        else:
            abort(404, message='Item not found')

api.add_resource(ItemApi, '/items/<int:item_id>')
```

`GET /items/1` returns `{"id": 1, "name": "pen", "user": "Alice"}` and `GET /items/2` returns `404 {"message": "Item not found"}`.

In this example, we define a resource field structure called `item_fields` that specifies the expected fields in our response. We then use the `@marshal_with` decorator on our GET method to indicate that the response should be formatted according to the defined structure. This helps ensure that our API responses are consistent and well-structured.

> [!WARNING]
> **`marshal_with` formats everything the method returns, errors included.** If the method above did `return {'message': 'Item not found'}, 404`, the status code would stay 404 but the body would become `{"id": 0, "name": null, "user": null}`: the message has no matching field and is lost. Likewise a field that finds no attribute gives `null` (`fields.Integer` gives its default `0`). So raise the error with `abort(404, message=...)` as above, or use `marshal(...)` only on the success path (next section).

### Marshal and Marshal_with

The `marshal` function in Flask Restful is used to format a response according to a specified structure. It takes a data object and a resource field structure as arguments and returns a formatted response. The `marshal_with` decorator is a convenient way to apply the `marshal` function to the return value of a resource method. It allows us to define the expected structure of our responses and ensures that all responses from that method are formatted consistently. When we use `marshal_with`, we define a resource field structure that specifies the fields and their types that we want to include in our response. The `marshal_with` decorator then automatically applies the `marshal` function to the return value of the decorated method, ensuring that the response is formatted according to the defined structure. This helps maintain consistency in our API responses and makes it easier for clients to consume our API.

```python
from flask import Flask
from flask_restful import Resource, Api, fields, marshal

app = Flask(__name__)
api = Api(app)

class Purchase:  # stands in for the database model of the previous section
    def __init__(self, id, item_name, user_name):
        self.id = id
        self.item_name = item_name
        self.user_name = user_name

purchases = {1: Purchase(1, 'pen', 'Alice')}

item_fields = {
    'id': fields.Integer,
    'name': fields.String(attribute='item_name'),
    'user': fields.String(attribute='user_name'),
}

class ItemApi(Resource):
    def get(self, item_id):
        item = purchases.get(item_id)
        if item:
            return marshal(item, item_fields)
        else:
            return {'message': 'Item not found'}, 404

api.add_resource(ItemApi, '/items/<int:item_id>')
```

In this example, we are using the `marshal` function directly in the GET method to format the response according to the `item_fields` structure. This achieves the same result as using the `@marshal_with` decorator, but it allows us to have more control over when and how we apply the marshalling to our responses: the error response is returned as it is.

## Error Handling

Flask Restful has built-in error handling that allows us to return appropriate error messages and status codes when something goes wrong. Errors raised inside a resource (for example with `abort`) are answered with a JSON body `{"message": ...}`, and an unexpected exception gives `500 {"message": "Internal Server Error"}` (only when debug mode is off: with `debug=True`, as in our examples, Flask re-raises it and shows the interactive debugger instead). The idiomatic way to return an error from a resource is `flask_restful.abort(status_code, message=...)`:

```python
from flask import Flask
from flask_restful import Resource, Api, abort

app = Flask(__name__)
api = Api(app)

items = {1: 'pen'}

@app.errorhandler(404)
def not_found(error):
    return {'message': 'The resource you are looking for was not found'}, 404

class Item(Resource):
    def get(self, item_id):
        if item_id not in items:
            abort(404, message='Item not found')
        return {'name': items[item_id]}

api.add_resource(Item, '/item/<int:item_id>')

if __name__ == '__main__':
    app.run(debug=True)
```

| Request | Response |
| ------- | -------- |
| `GET /item/1` | `200 {"name": "pen"}` |
| `GET /item/9` | `404 {"message": "Item not found"}` (raised by `abort` inside the resource, handled by Flask Restful) |
| `GET /nothing` | `404 {"message": "The resource you are looking for was not found"}` (no route matches, so our `@app.errorhandler(404)` answers) |

Two things to remember: a response that a resource simply **returns** (`return {...}, 404`) is sent as it is and never goes through an error handler, and `@app.errorhandler` only sees the errors that Flask Restful does not handle itself, such as a URL that matches no route.

## Custom Error: HTTPException

Flask Restful allows us to define custom error responses for specific error scenarios. We can create a custom error class that inherits from `HTTPException` and tell the `Api` how to turn it into a response. The simplest way is the `errors` dictionary of `Api`, keyed by the **class name** of the exception:

```python
from flask import Flask
from flask_restful import Resource, Api
from werkzeug.exceptions import HTTPException

class ItemNotFound(HTTPException):
    code = 404
    description = 'Item not found'

errors = {
    'ItemNotFound': {
        'message': 'Item not found',
        'status': 404,
    },
}

app = Flask(__name__)
api = Api(app, errors=errors)

class Item(Resource):
    def get(self, item_id):
        raise ItemNotFound()

api.add_resource(Item, '/item/<int:item_id>')
```

`GET /item/1` answers `404 {"message": "Item not found", "status": 404}`: the fields of the dictionary are added to the response (and `status` is used as the status code). The message of this dictionary is fixed for the class.

If the response has to be built from the exception itself (for example its own message), we subclass `Api` and override `handle_error`:

```python
from flask import Flask
from flask_restful import Resource, Api
from werkzeug.exceptions import HTTPException

class CustomError(HTTPException):
    def __init__(self, message, status_code):
        super().__init__(description=message)
        self.code = status_code

class MyApi(Api):
    def handle_error(self, e):
        if isinstance(e, CustomError):
            return self.make_response({'message': e.description, 'status_code': e.code}, e.code)
        return super().handle_error(e)

app = Flask(__name__)
api = MyApi(app)

class Item(Resource):
    def get(self, item_id):
        raise CustomError('Item not found', 404)

api.add_resource(Item, '/item/<int:item_id>')
```

`GET /item/1` answers `404 {"message": "Item not found", "status_code": 404}`.

> [!CAUTION]
> A handler registered with `@app.errorhandler(CustomError)` is **not** used for exceptions raised inside Flask Restful resources: the `Api` handles them first and answers only `{"message": ...}` (without our `status_code` field). Use `Api(errors=...)` or override `handle_error` as shown.

## Summary

- Flask Restful is an extension for Flask that makes it easier to build REST APIs.
- We can define resources as classes and handle different HTTP methods in a structured way (one class for the collection, one for a single item).
- Request parsing allows us to extract and validate data from incoming requests (JSON by default, `location=` for form data and query strings).
- We can integrate Flask Restful with databases to manage persistent data.
- Flask Restful returns errors as JSON, offers `abort(code, message=...)`, and allows us to define custom errors with `Api(errors=...)` or `handle_error`.
- We can use the `marshal` function and `marshal_with` decorator to format our API responses consistently (and must not return error dictionaries from a `marshal_with` method).
