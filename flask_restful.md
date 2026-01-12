# Flask-RESTful – Detailed Guide

## 1. Creating Basic RESTful Routes Using `Api` and `Resource`

Flask-RESTful provides a clean class-based structure to define APIs.

### Basic Setup

```python
from flask import Flask
from flask_restful import Api, Resource

app = Flask(__name__)
api = Api(app)
```

### Creating a Simple Resource

```python
class Hello(Resource):
    def get(self):
        return {"message": "Hello World"}

api.add_resource(Hello, '/hello')
```

### Resource Methods

| HTTP Method | Resource Method |
| ----------- | --------------- |
| GET         | `get()`         |
| POST        | `post()`        |
| PUT         | `put()`         |
| DELETE      | `delete()`      |
| PATCH       | `patch()`       |

### Example with Multiple Methods

```python
class Item(Resource):
    items = {}

    def get(self, name):
        return {"item": self.items.get(name)}

    def post(self, name):
        Item.items[name] = {"name": name}
        return {"message": "Item created", "item": Item.items[name]}, 201

api.add_resource(Item, '/item/<string:name>')
```

---

## 2. Fields, `marshal`, and `marshal_with`

These tools help enforce structured responses.

### Import Required Tools

```python
from flask_restful import fields, marshal, marshal_with
```

### Defining Output Fields

```python
item_fields = {
    'name': fields.String,
    'price': fields.Float,
    'in_stock': fields.Boolean,
}
```

### Using `marshal`

```python
data = {"name": "Laptop", "price": 59999.99, "in_stock": True}
formatted = marshal(data, item_fields)
# formatted → {'name': 'Laptop', 'price': 59999.99, 'in_stock': True}
```

### Using `marshal_with`

Decorates resource methods.

```python
class Product(Resource):

    @marshal_with(item_fields)
    def get(self):
        return {"name": "Laptop", "price": 59999.99, "in_stock": True}

api.add_resource(Product, '/product')
```

### Optional Field Arguments

```python
fields.String(attribute='username')
fields.Float(default=0.0)
fields.Integer(required=True)
```

---

## 3. Using `reqparse` for Request Parsing

`reqparse` validates and extracts request parameters.

### Import

```python
from flask_restful import reqparse
```

### Creating a Parser

```python
parser = reqparse.RequestParser()
parser.add_argument('name', type=str, required=True, help='Name cannot be empty')
parser.add_argument('price', type=float, required=True)
parser.add_argument('in_stock', type=bool, default=True)
```

### Using the Parser Inside a Resource

```python
class Store(Resource):
    @marshal_with(item_fields)
    def post(self):
        args = parser.parse_args()
        return args, 201

api.add_resource(Store, '/store')
```

### Argument Options

| Option            | Meaning                    |
| ----------------- | -------------------------- |
| `type`            | Converts the incoming data |
| `required=True`   | Rejects request if missing |
| `help`            | Error message              |
| `default`         | Uses this value if missing |
| `choices=[...]`   | Restrict allowed values    |
| `location='json'` | Accept only from JSON body |

### Example with Choices and Locations

```python
parser.add_argument(
    'category',
    type=str,
    choices=['electronics', 'food', 'clothing'],
    location='json'
)
```

---

## Summary

This document covered:

* Creating RESTful APIs using `Api` and `Resource`
* Using fields, marshal, and marshal_with for structured output
* Using reqparse for validation and extraction of request data
