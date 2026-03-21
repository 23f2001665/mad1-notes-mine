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
    "student_id": fields.String,
    "name": fields.String,
    "dept": fields.String
}

book_fields = {
    "book_id": fields.String,
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
api.add_resource(BookResource, "/books/<string:book_id>")

api.add_resource(StudentListResource, "/students")
api.add_resource(StudentResource, "/students/<string:student_id>")

api.add_resource(BorrowListResource, "/borrows")
api.add_resource(BorrowResource, "/borrows/<int:borrow_id>")

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)