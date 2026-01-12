from flask import Flask, request, render_template, url_for, redirect, abort

app = Flask(__name__, template_folder='./')

class Student:
    def __init__(self):
        self.name = ""

student = Student()

@app.route("/student/<int:id>", methods=["GET", "POST"])
def student_details(id):
    if request.method == "GET":
        return render_template("form.html")
    
    elif request.method == "POST":
        form_data = request.form           # this gives me a dict like object
        # student.name = form_data["student_name"]    # setting a new name taken from form 
        # return "student modified", 201
        return form_data
    
    else:
        return "none"

@app.route("/home")
@app.route("/")
def home():
    abort(401)
    return redirect(url_for('student_details', id=1))
    # return redirect("/student/1")


if __name__ == "__main__":
    print(app.url_map)
    app.run(debug=True)



# User.query -> query_object -> filter, order -> all, first, 
# db.session.query(TableName) -> filter, order

# User.query(NotAllowedHere)
# db.session.get("TableName", fieldName)

# add -> session -> get fetches from session.
# filter(tAbleName.fieldName condition sqlalchemyoperator)
# filter_by attribute comparison as keyword argument

