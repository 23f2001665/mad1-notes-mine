from flask import Flask, request, render_template, url_for, redirect, abort

app = Flask(__name__)

x = 0

@app.route('/')
def home():
    global x
    x += 1
    data = request.args
    print(data)
    return render_template('form.html', gender='m', name='himanshu', age=57, x=x)


@app.route('/add/<int:x>/<int:y>')  # path parameters of the url
def add(x, y):

    if y == 0:
        abort(402)
    return str(x + y)

@app.route('/register/user', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('form.html')
    elif request.method == 'POST':
        data = request.form
        name = data['fullname']
        dob = data['dob']
        years = 2026 - int(dob.strip()[:4])
        gender = data['gender']
        return render_template('dashboard.html', name=name, age=years, gender=gender)

# @app.route('/dump', methods=['GET', 'POST'])
# def dump():
#     print(request.args)
#     print(request.form)
#     return request.args or request.form

# print(app.url_map)

@app.route('/url')
def url():
    # print(app.url_map)
    # print('-'*40)
    # print(url_for('register'))
    # print(url_for('home'))
    # print(url_for('add', x=5, y=6, z=7))
    # print('-'*40)

    data = request.args
    x = data['x']
    y = data['y']

    return redirect(url_for('add', x=x, y=y))

app.run(debug=True)

