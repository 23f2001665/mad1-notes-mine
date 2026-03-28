# Debugging

Debugging is the process of finding and fixing errors in your code. It is an essential skill for any programmer, and it can be a challenging and frustrating process. However, with the right tools and techniques, you can become an effective debugger and quickly identify and resolve issues in your code.

## Common Debugging Techniques

1. **Print Statements**: The simplest form of debugging is to use print statements to output the values of variables and the flow of execution. This can help you understand what your code is doing and identify where things are going wrong.
2. **Using a Debugger**: Most modern IDEs come with built-in debuggers that allow you to step through your code line by line, inspect variables, and set breakpoints. This can be a powerful way to understand the behavior of your code and find bugs.
3. **Unit Testing**: Writing unit tests for your code can help you catch bugs early and ensure that your code is working as expected. Unit tests can also serve as documentation for how your code is supposed to work. We will cover this in week10.
4. **pdb Module**: Python's built-in `pdb` module allows you to set breakpoints and step through your code in the terminal. This can be useful for debugging scripts that are not run in an IDE.
5. **Flask-Shell**: If you are working on a Flask application, you can use the Flask shell to interact with your application and test out code snippets in an interactive environment.
6. **Flask Error UI**: Flask provides a built-in error UI that shows you the stack trace and allows you to inspect variables at the point where an error occurred. This can be very helpful for debugging issues in your Flask application.

In this section we will focus on `pdb`, `flask-shell` and `Flask Error UI` for debugging Flask applications.

## pdb Module

The `pdb` module is a powerful tool for debugging Python code. You can use it to set breakpoints, step through your code, and inspect variables. To use `pdb`, you can insert the following line in your code where you want to start debugging:

```python
import pdb

def my_function():
    # some code
    pdb.set_trace()  # This will start the debugger at this point
    # more code
```

When you run your code, it will pause at the `pdb.set_trace()` line, and you can use various commands to navigate through your code and inspect variables.
pdb.set_trace()
```

## Flask Shell

The Flask shell is an interactive Python shell that has your Flask application context loaded. This means you can interact with your application, test out code snippets, and inspect variables in an environment that is aware of your Flask app. To start the Flask shell, you can use the following command in your terminal:

```bash
flask shell
```

Once you are in the Flask shell, you can import your application and interact with it. For example, if you have a Flask app defined in a file called `app.py`, you can do the following:

```python
from app import app
print(various_variables)
```

## Flask Error UI

When an error occurs in a Flask application, Flask provides a built-in error UI that shows you the stack trace and allows you to inspect variables at the point where the error occurred. This can be very helpful for debugging issues in your Flask application. To see the error UI, make sure you are running your Flask app in debug mode:

```bash
export FLASK_ENV=development
flask run
```

When an error occurs, you will see a detailed error page with the stack trace and the ability to inspect variables. This can help you quickly identify the source of the error and understand what went wrong.

we will complete it later.