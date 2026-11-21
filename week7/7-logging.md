# Logging

**Logging** is the process of recording information about what a program is doing while it runs. It helps developers to understand the behaviour of an application, to find problems **after** they happened (for example on a server where nobody was watching) and to debug.

We have already used `print` to output information. For real applications `print` is a poor logger:

| `print` | `logging` |
| --- | --- |
| every message looks the same | each message has a **severity level** (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| always goes to the console | can go to the console, a **file**, e-mail, a network service, all at once |
| no time or origin | can add the **time**, the module, the line number automatically |
| to silence it you must edit or delete the code | change **one setting** (the level) to show more or fewer messages |

> [!NOTE]
> Every example and every output on this page was run for real in [`verify_week7_claims.py`](verify_week7_claims.py) (Python 3.13, Flask 3.1). Timestamps in the sample outputs will of course differ on your machine.

## Basic logging setup

```python
import logging
logging.basicConfig(level=logging.DEBUG, filename='app.log', format='%(asctime)s - %(levelname)s - %(message)s')
logging.debug('This is a debug message')
logging.info('This is an info message')
logging.warning('This is a warning message')
logging.error('This is an error message')
logging.critical('This is a critical message')
```

Nothing is printed on the screen: everything goes to the file `app.log`, which now contains:

```text
2026-11-21 12:14:19,112 - DEBUG - This is a debug message
2026-11-21 12:14:19,112 - INFO - This is an info message
2026-11-21 12:14:19,112 - WARNING - This is a warning message
2026-11-21 12:14:19,112 - ERROR - This is an error message
2026-11-21 12:14:19,112 - CRITICAL - This is a critical message
```

`basicConfig` configures the logging system once, with:

- `level`: the **minimum level** that is recorded. `DEBUG` is the lowest, so *all* messages are logged.
- `filename`: the file to write to (without it, the messages go to the console, `stderr`).
- `format`: how each line looks. Some of the available fields:

| Field | Meaning |
| --- | --- |
| `%(asctime)s` | date and time of the message |
| `%(levelname)s` | `DEBUG`, `INFO`, ... |
| `%(message)s` | the text that you passed |
| `%(name)s` | the name of the logger (the root logger is `root`) |
| `%(filename)s`, `%(lineno)d`, `%(funcName)s` | file, line number and function where the call was made |

> [!WARNING]
> **Two surprises**
>
> 1. **Without any configuration only `WARNING` and above are shown.** The default level is `WARNING` (30). `logging.debug(...)` and `logging.info(...)` print nothing, while `logging.warning('w')` prints `WARNING:root:w` on the console.
> 2. **`basicConfig()` works only the first time.** If the root logger already has a handler, later calls are ignored: calling `basicConfig(level=INFO, filename='first.log')` and then `basicConfig(level=DEBUG, filename='second.log')` leaves the level at INFO and creates only `first.log`. Add `force=True` to replace the old configuration.

### Logging levels

- **DEBUG**: detailed information, typically of interest only when diagnosing problems.
- **INFO**: confirmation that things are working as expected.
- **WARNING**: something unexpected happened, or a problem is coming (for example "disk space low"); the software still works.
- **ERROR**: because of a more serious problem the software could not perform some function.
- **CRITICAL**: a very serious error; the program itself may be unable to continue.

The levels are just **integers**, and a message is recorded when its level is **greater than or equal to the configured level**:

| Level | Value |
| --- | --- |
| CRITICAL | 50 |
| ERROR | 40 |
| WARNING | 30 |
| INFO | 20 |
| DEBUG | 10 |
| NOTSET | 0 |

Because they are numbers, `level=20` means the same as `level=logging.INFO`, and we can even define our own level in between (for example 25).

## Example usage

```python
import logging
logging.basicConfig(level=20, filename='app.log', format='%(asctime)s - %(levelname)s - %(message)s')
# 20 is the value of INFO, so only INFO and above are logged

def divide(a, b):
    logging.debug(f'Dividing {a} by {b}')
    if b == 0:
        logging.error('Attempt to divide by zero')
        return None
    return a / b

result = divide(10, 2)
logging.info(f'Result of division: {result}')
result = divide(10, 0)
logging.info(f'Result of division: {result}')
```

The `divide` function logs a debug message before dividing and an error message if the divisor is zero; the result is logged as `INFO`. The file `app.log` contains:

```text
2026-11-21 12:14:19,145 - INFO - Result of division: 5.0
2026-11-21 12:14:19,145 - ERROR - Attempt to divide by zero
2026-11-21 12:14:19,145 - INFO - Result of division: None
```

The two `DEBUG` lines ("Dividing ...") are missing because their level (10) is below the configured level (20). Change `level=20` to `level=10` and they appear: the program is unchanged, only the setting.

### Logging an exception with its traceback

Inside an `except` block `logging.exception(...)` logs at `ERROR` level **and adds the traceback**, which is exactly what you need to find the cause later:

```python
try:
    1 / 0
except ZeroDivisionError:
    logging.exception('Division failed')
```

```text
ERROR - Division failed
Traceback (most recent call last):
  File "t.py", line 5, in <module>
    1 / 0
    ~~^~~
ZeroDivisionError: division by zero
```

(For other levels use `exc_info=True`, e.g. `logging.warning('retrying', exc_info=True)`.)

### Tip: let `logging` do the formatting

```python
logging.debug('Dividing %s by %s', a, b)       # preferred
logging.debug(f'Dividing {a} by {b}')           # works, but the string is always built
```

With `%s` arguments the text is built **only if the message is really logged**. We checked it with an object whose `__str__` counts its calls: with the level at INFO the lazy debug call ran `__str__` **0 times**, the f-string version **once**. It matters when building the message is expensive.

## Logging in Flask applications

Flask has its own logger, `app.logger` (a normal `logging` logger whose name is the name of the app). Use it inside routes:

```python
from flask import Flask, request
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG, filename='app.log', format='%(asctime)s - %(levelname)s - %(message)s')

@app.route('/divide')
def divide_route():
    a = int(request.args.get('a', 0))
    b = int(request.args.get('b', 1))
    app.logger.debug(f'Dividing {a} by {b}')
    if b == 0:
        app.logger.error('Attempt to divide by zero')
        return 'Error: Division by zero is not allowed', 400
    result = a / b
    app.logger.info(f'Result of division: {result}')
    return f'Result: {result}'
```

After the requests `/divide?a=10&b=4` and `/divide?a=1&b=0` the file `app.log` contains:

```text
2026-11-21 12:14:19,349 - DEBUG - Dividing 10 by 4
2026-11-21 12:14:19,349 - INFO - Result of division: 2.5
2026-11-21 12:14:19,350 - DEBUG - Dividing 1 by 0
2026-11-21 12:14:19,350 - ERROR - Attempt to divide by zero
```

and **nothing** appears on the console: the messages of `app.logger` travel up to the root logger, whose handler (from `basicConfig`) writes them to the file. What you see depends on the configuration:

| Configuration | Where do `app.logger` messages go? |
| --- | --- |
| `basicConfig(..., filename='app.log')` as above | **only to the file**, all levels from the configured one |
| nothing configured, normal mode | Flask adds its own console handler, but only `WARNING` and above appear (`[2026-11-21 12:14:19,544] WARNING in app: warn`) |
| nothing configured, **debug mode** (`app.debug = True`, `--debug`) | the console shows **DEBUG** and above |

## Extra: Logger, Handler and Formatter

For more control the logging module is built from three parts:

- **Logger**: the object that you call (`logger.info(...)`). You can have several, named after the parts of your application. Use `logging.getLogger(__name__)` to name it after the current module.
- **Handler**: sends the record to a **destination** (console, file, e-mail, ...). One logger can have **several** handlers.
- **Formatter**: defines the **format** of the text.

<details>
<summary>Example: debug and above into a file, info and above on the console</summary>

```python
import logging
# Create a logger
logger = logging.getLogger('my_logger')   # or better: logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create a file handler
file_handler = logging.FileHandler('app.log')
file_handler.setLevel(logging.DEBUG)

# Create a console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Create a formatter and set it for both handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Log messages
logger.debug('This is a debug message')
logger.info('This is an info message')
logger.warning('This is a warning message')
logger.error('This is an error message')
logger.critical('This is a critical message')
```

The console shows four lines (INFO, WARNING, ERROR, CRITICAL, no DEBUG):

```text
2026-11-21 12:14:19,791 - my_logger - INFO - This is an info message
2026-11-21 12:14:19,791 - my_logger - WARNING - This is a warning message
2026-11-21 12:14:19,791 - my_logger - ERROR - This is an error message
2026-11-21 12:14:19,791 - my_logger - CRITICAL - This is a critical message
```

and `app.log` contains **all five** lines (starting with the DEBUG one).

A record has to pass **two filters**: the level of the **logger** (`DEBUG`: let everything in) and then the level of **each handler** (file: `DEBUG`, console: `INFO`). The logger's level should therefore be the **lowest** of the handler levels.

</details>

<details>
<summary>Why do I see every message twice? Propagation</summary>

Loggers form a **hierarchy** by their dotted names: `app.sub` is a child of `app`, and all of them are children of the **root logger**. A record is handled by the handlers of its logger **and then also by the handlers of all its ancestors** (this is called *propagation*). If both the child and the root have a console handler, you get the message **twice**:

```python
import logging
logging.basicConfig(level=logging.INFO, format='ROOT %(message)s')            # handler on the root logger
lg = logging.getLogger('app.sub')
h = logging.StreamHandler(); h.setFormatter(logging.Formatter('CHILD %(message)s')); lg.addHandler(h)
lg.info('hello')            # CHILD hello   and   ROOT hello
lg.propagate = False
lg.info('no propagation')   # only: CHILD no propagation
```

Set `logger.propagate = False` (or configure handlers only in one place) to avoid duplicates. Also, calling `logger.addHandler(...)` twice for the same handler, for example every time a function runs, makes duplicate lines.

</details>

## Rotating log files

A log file that is never cleaned grows without limit. A `RotatingFileHandler` starts a **new file when the current one reaches a size** and keeps only a fixed number of old ones.

<details>
<summary>Example</summary>

```python
import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger('rot')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Create a rotating file handler
rotating_handler = RotatingFileHandler('app.log', maxBytes=2000, backupCount=5)
rotating_handler.setLevel(logging.DEBUG)
rotating_handler.setFormatter(formatter)
logger.addHandler(rotating_handler)

for i in range(120):
    logger.info('message number %d with some padding text to fill the file', i)
```

`maxBytes` is the maximum size of a file in bytes and `backupCount` the number of old files to keep. When `app.log` is full it is renamed to `app.log.1` (the previous `app.log.1` becomes `app.log.2`, and so on) and a new, empty `app.log` is started; the file that would become `app.log.6` is deleted. After the 120 messages above the folder held `app.log` (the **newest** messages) and `app.log.1` to `app.log.5` (older and older), each at most 2,000 bytes. The oldest messages had already been **deleted**, so the disk use is bounded by $(5 + 1) \times 2000$ bytes.

(There is also `TimedRotatingFileHandler`, which starts a new file at a time interval, for example every midnight.)

</details>

## Extra: e-mail logging

Important messages can be sent by e-mail with the **`SMTPHandler` of the standard library** (`logging.handlers.SMTPHandler`). *Flask-Mail is not needed* (it is for sending e-mail from your routes) and it does not contain an `SMTPHandler`.

<details>
<summary>Example</summary>

```python
import logging
from logging.handlers import SMTPHandler

mail_handler = SMTPHandler(
    mailhost=('smtp.gmail.com', 587),
    fromaddr='from@example.com',
    toaddrs=['to@example.com'],
    subject='Critical Error in Application',
    credentials=('from@example.com', 'APP-PASSWORD'),   # an app password, not the normal account password
    secure=(),                                          # () = switch to an encrypted connection (STARTTLS)
)
mail_handler.setLevel(logging.CRITICAL)                 # only CRITICAL records are e-mailed
logging.getLogger().addHandler(mail_handler)

@app.route('/divide')
def divide_route():
    a = int(request.args.get('a', 0))
    b = int(request.args.get('b', 1))
    logging.debug(f'Dividing {a} by {b}')
    if b == 0:
        logging.critical('Attempt to divide by zero')
        return 'Error: Division by zero is not allowed', 400
    result = a / b
    logging.info(f'Result of division: {result}')
    return f'Result: {result}'
```

- The **mail account** needs credentials: for Gmail you create an **app password** (this requires 2-step verification); the real account password should never be put in code.
- **`mail_handler.setLevel(logging.CRITICAL)` is essential.** A handler without a level mails **every** record that reaches it. In a test with a local mail server, two log calls (a debug and an error) produced **two e-mails**; after `setLevel(logging.CRITICAL)` only the critical record produced a mail (with the subject `Critical Error in Application`). So with the level set, only `logging.critical(...)` in `divide_route` triggers an e-mail.

</details>

## Good practice

- **Choose the right level**: `DEBUG` for details, `INFO` for normal events, `WARNING` for suspicious things, `ERROR` for failures, `CRITICAL` for emergencies. Do not leave `DEBUG` on in production: it produces a huge amount of text.
- **Never log secrets**: passwords, tokens, full card numbers. A log file is plain text and usually less protected than the database.
- Give each message **context** (the user id, the request, the values): "Attempt to divide by zero" is more useful with `a` and `b`.
- **Rotate** log files so the disk does not fill up.
- Logs are also how attacks and failures are noticed; see [logging in Week 9](../week9/9-https-logging.md#logging). To find the cause of a bug *while* developing, see [debugging](debugging.md).

## Practice questions

<details>
<summary>1. The default level of the root logger: what does <code>logging.info('x')</code> print without any configuration?</summary>

Nothing: the default level is `WARNING` (30), and `INFO` is 20. `logging.warning('w')` would print `WARNING:root:w`.

</details>

<details>
<summary>2. You call basicConfig(level=DEBUG) after another library already configured logging. Why does it have no effect?</summary>

`basicConfig` does nothing if the root logger already has a handler. Use `logging.basicConfig(..., force=True)`.

</details>

<details>
<summary>3. Every log line appears twice on the console. Likely cause?</summary>

The same message is handled by a handler on the logger and again by a handler on the root logger (propagation), or the same handler was added twice. Set `propagate = False` or configure the handlers in one place only.

</details>

<details>
<summary>4. Your mail handler e-mails every single message. What is missing?</summary>

A level on the handler: `mail_handler.setLevel(logging.CRITICAL)` (or `ERROR`).

</details>

## Conclusion

The `logging` module gives control over **how, where and how much** is recorded, and a structured way to manage the levels. It is best practice to use `logging` instead of `print` in applications, because the code stays clean and the logs give better insight into the behaviour of the application, especially when it runs on a server.
