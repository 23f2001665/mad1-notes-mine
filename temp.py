# # # from jinja2 import Template as T

# # # template2 = T(
# # #     """
# # #     Hello I am {{name[0]}}
# # #     {{dictionary.name}}
# # # """
# # # )

# # # d = {"name":"himanshu", "job":"TA"}

# # # d["name"]
# # # d.get("name", "default_name")

# # # output = template2.render(name="himanshu", dictionary=d)
# # # print(output)


# # # import sys

# # # # sys.argv        # -> a list of strings which corresponds to command line arguments
# # # # sys.exit()      # -> it is used to safely exit the program at a specific point

# # # l = sys.argv
# # # print(l)

# # # sys.exit()

# # # print("hello")


# # from flask import Flask, render_template, request, redirect, url_for, abort

# # # Create an instance of the Flask class
# # app = Flask(__name__)

# # # Define a "route" that maps a URL to a Python function

# # name = None

# # @app.route('/', methods=["GET", "POST"])
# # def hello_world():
# #     if request.method == "GET":
# #         return render_template('index.html')
# #     elif request.method == "POST":
# #         global name
# #         name = request.form["fullname"]
# #         print(url_for('bye'))
# #         return redirect(url_for('bye'))


# # @app.route("/bye")
# # def bye():
# #     if name[0] == "h":
# #         abort(401)
# #     return f"bye {name}"


# # # This block ensures the server only runs when the script is executed directly
# # if __name__ == '__main__':
# #     app.run(debug=True, port=3000)



# l = [1,2,3]

# l.append(4)
# db.session.add(l)

# db.session.get(id_of_l)  -> [1,2,3,4]

# List.query.get(id_of_l)  -> [1,2,3]


from flask import render_template, Flask, url_for, redirect, abort, request

app = Flask(__name__)

@app.route("/")
def home():
    data = request.args
    print(data.get("name", "Ravi"))
    print(data.get("user", "himanshu"))
    # print(url_for('hello', id=1, extra="discount"))
    return request.args

@app.route("/student/<int:id>/")
def hello(id):
    if id == 0:
        abort(401)
    return "hello", 200 

@app.errorhandler(401)
def handler_401(e):
    print(e)
    return redirect("/")

@app.route("/form", methods=["POST", "GET"])
def form():
    if request.method == "POST":
        form_data = request.form
        return form_data
    elif request.method == "GET":
        return render_template("index.html")

print(app.url_map)
app.run(debug=True)

# request.args -> query parameter
# request.form -> form data
# request.json -> json body of request

# dictionary