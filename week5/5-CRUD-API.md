# CRUD Operations
CRUD is:
<div class="card">
C – <b>Create</b><br>
R – <b>Read</b><br>
U – <b>Update</b><br>
D – <b>Delete</b><br>
</div>

- A set of **actions that define the complete life cycle of data.** In the library system we [discussed before](../week4/4-SQL-Recap.html#database-example-library-management-system):

1. A book is **Created**.
2. Users can **Read** books many times.
3. Book details may be **Updated**.
4. Eventually, records may be **Deleted**.

## 1. CREATE Operation

The **Create** operation inserts a new record into a database table.
* Creates a new entry.
* The record must not already exist.
* The system checks for conflicts (e.g., duplicate primary keys).
* Mandatory fields must be provided (`nullable=False`)

#### Example 1: Adding a New Book

Suppose the library acquires a new book:

| book_id | title             | category |
| ------- | ----------------- | -------- |
| B4      | Operating Systems | CS       |

Before insertion:
1. The system checks whether `book_id = B4` already exists → reject insertion
2. Fields like `edition, publisher` are not provided but it's fine as they are optional 

#### Example 2: Creating a Borrow Entry

If student S102 borrows B2:

| student_id | book_id | borrow_date |
| ---------- | ------- | ----------- |
| S102       | B2      | 2024-02-01  |

System checks:
* Does student S102 exist?
* Does book B2 exist?
* Are foreign key constraints satisfied?

Only then is the record created.


## 2. READ Operation
The **Read** operation retrieves data from the database without modifying it.

- Examples: 
1. Get List of Students: the system retrieves all rows from the Students table.
2. Summary statistics for librarian dashboard: aggregation functions such as
- `COUNT` to get total number of books 
- `GROUP BY` to get number of books per category (maybe plot a `matplotlib` piechart of the same).



## 3. UPDATE Operation

* Record must already exist.
* Only specified fields are changed.
* Data integrity must be preserved.

#### Example 1: Changing Department

Suppose Rohan (S102) changes department from EE to CS.
* Locates record where `student_id = S102`.
* Updates only the dept column.

#### Example 2: Correcting a Borrow Date

Before:
| S101 | B1 | 2024-01-10 |

After correction:
| S101 | B1 | 2024-01-11 |

Only borrow_date field is modified.



## 4. DELETE Operation

The **Delete** operation removes records from the database.

#### Example 1: Removing a Student

If `student_id = S103` leaves the institution:
The system must ensure:

* Related `BorrowedBooks` entries are handled.
* Either prevent deletion (if constraints exist) or [cascade delete](https://docs.sqlalchemy.org/en/21/orm/cascades.html#delete) related records.

### Example 2: Removing a Borrow Record

When a book is returned, the borrow entry may be deleted:

Delete:
| S101 | B2 | 2024-01-15 |


#### Database Optimization
1. **Read-Heavy Systems**: Large number of queries, few insertions or updates.
Optimization: Indexing, Caching

2. **Write-Heavy Systems**: Frequent inserts and updates<br>
Optimization: Efficient transaction logging, Data durability mechanisms.


## API – Application Programming Interface

An API (Application Programming Interface) is a <span style="font-weight:bold; color:rgb(181, 118, 244)">standardized way</span> for a client (frontend/external system) to communicate with a server.

:::attention An API acts as a layer that translates HTTP requests into CRUD operations on the database.
:::

- It is a set of definitions and protocols that allow two applications to communicate with
each other.
- APIs are follows a **request-response model** to share data and functionality between applications, where one application sends requests to another
to access data or perform actions.
- There are many different types of APIs, such as Web APIs, Library APIs, Database APIs
and Hardware APIs.
- Web APIs include REST APIs, RPC APIs, GraphQL APIs, etc

The client only knows <span style="font-weight:bold; color:rgb(98, 151, 208)">API endpoints</span>. The client does NOT know:
- Database schema
- Internal business logic
- Server implementation details

### Why API?
- **Scalability**: enables distributed systems to grow
- **Efficiency**: allows reuse of backend services
- **Automation**: enables systems to interact without human input
- **Security** : controlled access via authentication and authorization


A Controller groups related actions logically:
| Controller             | Actions                                      |
| ---------------------- | -------------------------------------------- |
| BookController         | createBook, getBooks, updateBook, deleteBook |
| StudentController      | createStudent, getStudents                   |
| BorrowController       | createBorrow, returnBook                     |

The server exposes structured URLs and HTTP methods

## Routes and URL Mapping
Routes define how incoming HTTP requests are mapped to specific functions (**handlers**) in the server.
- **Maps a URL to a function handler functions** (typically within controllers)
- **HTTP methods** (GET, POST, PUT, DELETE) specify the type of **CRUD** operation to perform.
- **URL structure** like `students/<int:student_id>` identifies **resource**, while route determines which **function** is executed.

#### Route Handling using Decorators

In Python frameworks like Flask, decorators are used to map routes to functions.
```py

@app.route("/books", methods=["GET"])
def get_books():
    ...
```
The decorator binds the URL `/books` to the function `get_books()`
- When a request hits `/books`, this function is executed

<LibraryAPI />

:::details `flask_restful` code for the same example

```py
from flask import Flask
from flask_restful import Resource, Api, reqparse, marshal_with, fields
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
api = Api(app)

# ---------------------- MODELS ----------------------

class Student(db.Model):
    student_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    dept = db.Column(db.String(5))


class Book(db.Model):
    book_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(20))
    edition = db.Column(db.String(10))
    publisher = db.Column(db.String(100))


class Borrow(db.Model):
    borrow_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(4), db.ForeignKey('student.student_id'))
    book_id = db.Column(db.String(4), db.ForeignKey('book.book_id'))
    borrow_date = db.Column(db.String(20))


with app.app_context():
    db.create_all()

# ---------------------- PARSERS ----------------------

student_parser = reqparse.RequestParser()
student_parser.add_argument("name", required=True)
student_parser.add_argument("dept")

book_parser = reqparse.RequestParser()
book_parser.add_argument("title", required=True)
book_parser.add_argument("category")
book_parser.add_argument("edition")
book_parser.add_argument("publisher")

borrow_parser = reqparse.RequestParser()
borrow_parser.add_argument("student_id", required=True)
borrow_parser.add_argument("book_id", required=True)
borrow_parser.add_argument("borrow_date", required=True)

# ---------------------- FIELDS ----------------------

student_fields = {
    "student_id": fields.Integer,
    "name": fields.String,
    "dept": fields.String
}

book_fields = {
    "book_id": fields.Integer,
    "title": fields.String,
    "category": fields.String,
    "edition": fields.String,
    "publisher": fields.String
}

borrow_fields = {
    "borrow_id": fields.Integer,
    "student_id": fields.String,
    "book_id": fields.String,
    "borrow_date": fields.String
}

# ---------------------- BOOK RESOURCES ----------------------

class BookListResource(Resource):

    @marshal_with(book_fields)
    def get(self):
        return Book.query.all()

    def post(self):
        args = book_parser.parse_args()

        book = Book(
            title=args["title"],
            category=args["category"],
            edition=args["edition"],
            publisher=args["publisher"]
        )

        db.session.add(book)
        db.session.commit()

        return {"message": "Book created"}, 201


class BookResource(Resource):

    @marshal_with(book_fields)
    def get(self, book_id):
        book = Book.query.get(book_id)
        if not book:
            return {"message": "Book not found"}, 404
        return book

    def put(self, book_id):
        args = book_parser.parse_args()
        book = Book.query.get(book_id)

        if not book:
            return {"message": "Book not found"}, 404

        book.title = args["title"]
        book.category = args["category"]
        book.edition = args["edition"]
        book.publisher = args["publisher"]

        db.session.commit()
        return {"message": "Book updated"}

    def delete(self, book_id):
        book = Book.query.get(book_id)

        if not book:
            return {"message": "Book not found"}, 404

        db.session.delete(book)
        db.session.commit()

        return {"message": "Book deleted"}

# ---------------------- STUDENT RESOURCES ----------------------

class StudentListResource(Resource):

    @marshal_with(student_fields)
    def get(self):
        return Student.query.all()

    def post(self):
        args = student_parser.parse_args()

        student = Student(
            name=args["name"],
            dept=args["dept"]
        )

        db.session.add(student)
        db.session.commit()

        return {"message": "Student created"}, 201


class StudentResource(Resource):

    @marshal_with(student_fields)
    def get(self, student_id):
        student = Student.query.get(student_id)
        if not student:
            return {"message": "Student not found"}, 404
        return student

    def put(self, student_id):
        args = student_parser.parse_args()
        student = Student.query.get(student_id)

        if not student:
            return {"message": "Student not found"}, 404

        student.name = args["name"]
        student.dept = args["dept"]

        db.session.commit()
        return {"message": "Student updated"}

    def delete(self, student_id):
        student = Student.query.get(student_id)

        if not student:
            return {"message": "Student not found"}, 404

        db.session.delete(student)
        db.session.commit()

        return {"message": "Student deleted"}

# ---------------------- BORROW RESOURCES ----------------------

class BorrowListResource(Resource):

    @marshal_with(borrow_fields)
    def get(self):
        return Borrow.query.all()

    def post(self):
        args = borrow_parser.parse_args()

        # FK validation
        if not Student.query.get(args["student_id"]) or not Book.query.get(args["book_id"]):
            return {"message": "Invalid student or book"}, 400

        borrow = Borrow(
            student_id=args["student_id"],
            book_id=args["book_id"],
            borrow_date=args["borrow_date"]
        )

        db.session.add(borrow)
        db.session.commit()

        return {"message": "Borrow created"}, 201


class BorrowResource(Resource):

    @marshal_with(borrow_fields)
    def get(self, borrow_id):
        borrow = Borrow.query.get(borrow_id)
        if not borrow:
            return {"message": "Borrow not found"}, 404
        return borrow

    def put(self, borrow_id):
        args = borrow_parser.parse_args()
        borrow = Borrow.query.get(borrow_id)

        if not borrow:
            return {"message": "Borrow not found"}, 404

        borrow.student_id = args["student_id"]
        borrow.book_id = args["book_id"]
        borrow.borrow_date = args["borrow_date"]

        db.session.commit()
        return {"message": "Borrow updated"}

    def delete(self, borrow_id):
        borrow = Borrow.query.get(borrow_id)

        if not borrow:
            return {"message": "Borrow not found"}, 404

        db.session.delete(borrow)
        db.session.commit()

        return {"message": "Borrow deleted"}

# ---------------------- ROUTES ----------------------

api.add_resource(BookListResource, "/books")
api.add_resource(BookResource, "/books/<int:book_id>")

api.add_resource(StudentListResource, "/students")
api.add_resource(StudentResource, "/students/<int:student_id>")

api.add_resource(BorrowListResource, "/borrows")
api.add_resource(BorrowResource, "/borrows/<int:borrow_id>")

if __name__ == "__main__":
    app.run(debug=True)
```


##### Example Testing CURL Requests
Create Student
```sh
curl -X POST http://127.0.0.1:5000/students/5 \
-H "Content-Type: application/json" \
-d '{"name":"Kunal","dept":"ME"}'
```
Get Student
```sh
curl http://127.0.0.1:5000/students/1
```
Borrow Book
```sh
curl -X POST http://127.0.0.1:5000/borrow \
-H "Content-Type: application/json" \
-d '{"student_id":"S101","book_id":"B1","borrow_date":"2024-02-01"}'
```
:::