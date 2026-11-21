# Debugging

**Debugging** is the process of finding and fixing errors (bugs) in your code. It is an essential skill and it can be frustrating, but with the right tools and a method you can find the cause quickly.

A simple method that always works:

1. **Reproduce** the problem: find the exact input or steps that trigger it.
2. **Locate** it: which function or line first gives a wrong value?
3. **Understand** it: why is the value wrong? (Do not change code at random.)
4. **Fix** it and **check** with the same input that it is gone.
5. Keep a **test** for it so it does not come back ([Week 10: testing](../week10/10-testing.md)).

> [!NOTE]
> The outputs on this page (tracebacks, `pdb` sessions, `flask shell`, the Flask debugger) were produced by running the examples with Python 3.13 and Flask 3.1 in [`verify_week7_claims.py`](verify_week7_claims.py).

## Common debugging techniques

1. **Print statements**: the simplest way: print the values of variables and show which part of the code runs. Quick, but you must remove them afterwards; for permanent messages use [logging](7-logging.md).
2. **A debugger**: most modern IDEs (for example VS Code) have a built-in debugger: you set **breakpoints**, run the program, and it stops there so you can step through the code line by line and inspect the variables.
3. **Unit testing**: tests catch bugs early and document how the code should behave (Week 10).
4. **The `pdb` module**: Python's own debugger for the terminal, useful where no IDE is used (for example on a server).
5. **`flask shell`**: an interactive Python shell that has your Flask application loaded.
6. **Flask's error page** (debug mode): the traceback in the browser, with an interactive console.

In this section we focus on the traceback, `pdb`, `flask shell` and the Flask error page.

## Read the traceback first

When an exception is not handled, Python prints a **traceback**. Read it **from the bottom**:

```python
def average(numbers):
    return sum(numbers) / len(numbers)

def report(groups):
    for g in groups:
        print(average(g))

report([[4, 8], []])
```

```text
6.0
Traceback (most recent call last):
  File "t.py", line 8, in <module>
    report([[4, 8], []])
  File "t.py", line 6, in report
    print(average(g))
  File "t.py", line 2, in average
    return sum(numbers) / len(numbers)
ZeroDivisionError: division by zero
```

- **The last line** is the **type and the message** of the error: `ZeroDivisionError: division by zero`.
- **The last "File" entry** (just above it) is the line where it was raised: line 2 in `average`.
- **The entries above** show **who called whom**, from the top of the program down to the failing line: `<module>` called `report`, which called `average`.
- Here the first group `[4, 8]` printed `6.0`; the second group is empty, so `len(numbers)` is 0. The bug is not in the division but in a call with an **empty list**.
- (Newer Python versions underline the failing part of a line with `~~~^^^` markers. They only point at the exact expression; the way you read the traceback does not change.)

## Print debugging

```python
total = 24
print(f"{total=}")      # prints: total=24   (Python 3.8+: the f-string shows the name and the value)
```

`f"{expression=}"` prints the expression *and* its value, which saves typing the label.

## The `pdb` module

`pdb` lets you **pause** the program at a chosen place and look around. Since Python 3.7 the easiest way is the built-in **`breakpoint()`**:

```python
def average(numbers):
    total = 0
    for n in numbers:
        total += n
    breakpoint()                      # the program stops here and shows the (Pdb) prompt
    return total / len(numbers)

print(average([4, 8, 12]))
```

(The older way, `import pdb` and `pdb.set_trace()`, does the same thing.) When the program reaches the line, you get the prompt and can type commands:

```text
> calc.py(5)average()
-> breakpoint()
(Pdb) p total
24
(Pdb) p numbers
[4, 8, 12]
(Pdb) n
> calc.py(6)average()
-> return total / len(numbers)
(Pdb) p total / len(numbers)
8.0
(Pdb) c
8.0
```

| Command | Meaning |
| --- | --- |
| `l` (list) | show the source code around the current line (`->` marks it) |
| `p expression` | **print** the value of any expression (`pp` prints it prettily) |
| `n` (next) | run the current line and stop at the **next line** of this function |
| `s` (step) | **step into** the function that is called on this line |
| `c` (continue) | run until the next breakpoint or the end |
| `w` (where) | show the **call stack** (who called this function) |
| `b 12` | set another breakpoint at line 12 |
| `q` (quit) | stop the program |
| `h` | help |

- To switch all `breakpoint()` calls off without editing the code, set the environment variable `PYTHONBREAKPOINT=0` (the program above then simply prints `8.0`).
- **Post-mortem debugging:** `python -m pdb script.py` runs the script and, if it crashes, drops you at the failing line with the message *"Uncaught exception. Entering post mortem debugging"*, so you can print the variables at the moment of the crash.

### Using it in a Flask route

`breakpoint()` also works inside a view function. The request **waits** while the debugger is open in the terminal where the server is running; after `c` the browser gets its response:

```python
@app.route('/total/<int:n>')
def total(n):
    s = sum(range(n))
    breakpoint()
    return f'total={s}'
```

Opening `/total/5` stops in that terminal at `(Pdb)`; `p n` prints `5`, `p s` prints `10`, and `c` lets the page load with `total=10`.

## Flask shell

The **Flask shell** is an interactive Python shell with your application already loaded, so you can try code, call functions and inspect the data in an environment that knows your app. Start it in the folder of the application:

```bash
flask --app app shell
```

(`--app app` is the name of the file `app.py`; Flask also finds `app.py` by itself.) The banner tells you which app was loaded, and **`app` is already defined**: there is no need to `from app import app`.

```text
Python 3.13.18 ... on linux
App: app
Instance: /path/to/instance
>>> app
<Flask 'app'>
>>> from app import COUNTER        # anything else defined in your file is imported as usual
>>> COUNTER
42
>>> app.test_client().get('/').data    # call your own route without starting the server
b'hi'
>>> from flask import current_app
>>> current_app.name               # the application context is active
'app'
```

This is also how you test database code (see the `db` object of [Flask-SQLAlchemy](../week5/5-flask-sqlalchemy-basics.md)) with the application context ready.

## Flask error page (debug mode)

When an error happens, Flask normally shows only a plain **"500 Internal Server Error"** page: the details are hidden from the visitor on purpose. In **debug mode** Flask instead shows an error page with the **full traceback** and an **interactive debugger** (the Werkzeug debugger).

Turn debug mode on with one of:

```bash
flask --app app run --debug           # the command-line option
FLASK_DEBUG=1 flask --app app run     # or the environment variable
```

or `app.run(debug=True)` in the code. The start-up message confirms it:

```text
 * Debug mode: on
 * Debugger is active!
 * Debugger PIN: 118-130-247
```

> [!WARNING]
> **`export FLASK_ENV=development` no longer works.** The `FLASK_ENV` variable was removed in Flask 2.3: with Flask 3.1 the server still says `Debug mode: off` and shows the plain 500 page. Use `--debug`, `FLASK_DEBUG=1` or `app.run(debug=True)`.

With a route that fails (`return 1 / (x - 10)` with `x = 10`), debug mode gives a page titled **`ZeroDivisionError: division by zero // Werkzeug Debugger`**:

- the **traceback with the lines of source code** of each frame;
- a **console in every frame**: click the small console icon next to a frame, enter the **PIN** printed in the terminal, and type Python expressions to inspect the variables at that frame (`x` is `10`);
- the **automatic reloader** also restarts the server whenever you save a file.

> [!CAUTION]
> **Never run debug mode in production.** The console lets anyone who gets past the PIN run **any Python code on your server**, and the tracebacks reveal the source code and the settings. Use it only on your own machine while developing.

## Which tool when?

| Situation | Tool |
| --- | --- |
| a script crashed | read the **traceback** from the bottom |
| "what is the value of x here?" | `print(f"{x=}")` or `breakpoint()` and `p x` |
| the program takes a strange path | `breakpoint()`, then `n` and `s` to follow it |
| a Flask page shows 500 | run with `--debug` and read the error page, or check the [log](7-logging.md) |
| trying a function or a query in the app | `flask shell` |
| the bug must never come back | write a test ([Week 10](../week10/10-testing.md)) |
