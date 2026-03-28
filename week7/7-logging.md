# Logging

Logging is the process of recording information about the execution of a program. It is an essential part of software development and maintenance, as it helps developers to understand the behavior of their applications, identify issues, and debug problems.

We have already seen how to use the `print` function to output information to the console. However, using `print` statements for logging is not recommended for production applications, as it can lead to cluttered code and is not flexible enough for different logging levels and outputs.

In Python, the `logging` module provides a powerful and flexible framework for logging. It allows us to log messages with different severity levels (DEBUG, INFO, WARNING, ERROR, CRITICAL) and to configure different handlers to output logs to various destinations (console, files, etc.).

## Basic Logging Setup

To set up basic logging in our Python application, we can use the following code:

```python
import logging
logging.basicConfig(level=logging.DEBUG, filename='app.log', format='%(asctime)s - %(levelname)s - %(message)s')
logging.debug('This is a debug message')
logging.info('This is an info message')
logging.warning('This is a warning message')
logging.error('This is an error message')
logging.critical('This is a critical message')
```

In this example, we configure the logging to write messages to a file named `app.log` with a specific format that includes the timestamp, log level, and message. We also set the logging level to DEBUG, which means that all messages of level DEBUG and above will be logged.

### Logging Levels

- **DEBUG**: Detailed information, typically of interest only when diagnosing problems.
- **INFO**: Confirmation that things are working as expected.
- **WARNING**: An indication that something unexpected happened, or indicative of some problem in the
near future (e.g., ‘disk space low’). The software is still working as expected.
- **ERROR**: Due to a more serious problem, the software has not been able to perform some function.
- **CRITICAL**: A very serious error, indicating that the program itself may be unable to continue running.

Actually logging levels are just integer values, and we can define our own levels if needed. The standard levels are defined as follows:

| Level    | Value |
|----------|-------|
| CRITICAL | 50    |
| ERROR    | 40    |
| WARNING  | 30    |
| INFO     | 20    |
| DEBUG    | 10    |
| NOTSET   | 0     |

## Example Usage

Here is an example of how to use logging in a simple application:

```python
import logging
logging.basicConfig(level=20, filename='app.log', format='%(asctime)s - %(levelname)s - %(message)s')
# 20 is the value for INFO level, so only INFO and above messages will be logged    
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

In this example, we have a function `divide` that performs division. We log a debug message before performing the division and an error message if there is an attempt to divide by zero. We also log the result of the division as an info message.

## Logging in Flask Applications

In a Flask application, we can use the `logging` module to log messages in our routes and other parts of the application. Flask also provides a built-in logger that we can use. Here is an example of how to use logging in a Flask application:

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

Here in this example we use `app.logger` to log messages in our Flask route. The logging configuration is the same as before, and we log debug, error, and info messages based on the operations performed in the route.

## Extra: Logger, Handler, and Formatter

The `logging` module provides a more advanced way to configure logging using loggers, handlers, and formatters.

- **Logger**: This is the main object that we use to log messages. We can create multiple loggers for different parts of our application.
- **Handler**: This is responsible for sending the log messages to the appropriate destination (e.g., console, file, etc.). We can have multiple handlers for a single logger.
- **Formatter**: This defines the format of the log messages. We can create custom formatters to include different information in the log messages.

::: details click to expand

Here is an example of how to use loggers, handlers, and formatters:

```python
import logging
# Create a logger
logger = logging.getLogger('my_logger') # or better use __name__ to get the module name as logger name
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

In this example, we create a logger named `my_logger` and set its level to DEBUG. We then create a file handler that writes log messages to `app.log` and a console handler that outputs log messages to the console. We set the logging level for *file_handler* to `DEBUG` and *console_handler* to `INFO`, and define a formatter to specify the format of the log messages. Finally, we add both handlers to the logger and log messages at different levels.

:::

## Rotating Log Files

When logging to a file, it is often useful to rotate the log files to prevent them from growing indefinitely. The `logging` module provides a `RotatingFileHandler` that can be used for this purpose.

:::details click to expand

```python
import logging
from logging.handlers import RotatingFileHandler
# Create a rotating file handler
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
rotating_handler = RotatingFileHandler('app.log', maxBytes=2000, backupCount=5)
rotating_handler.setLevel(logging.DEBUG)
rotating_handler.setFormatter(formatter)
logger.addHandler(rotating_handler)
```

In this example, we create a `RotatingFileHandler` that will write log messages to `app.log`. The `maxBytes` parameter specifies the maximum size of the log file in bytes, and the `backupCount` parameter specifies the number of backup files to keep. When the log file reaches the specified size, it will be rotated, and a new log file will be created.

:::

## Extra: Email Logging

:::details click to expand

We can also send important log messages via email. This can be done in various ways, but we will use `flask-mail` for this purpose. First, we need to install the `flask-mail` package:

```bash
pip install flask-mail
```

Then, we need get the mail:app-passcode from the email account we want to use for sending emails. After that, we can set up an SMTP handler in our logging configuration to send critical log messages via email:

```python
import logging
import flask_mail
mail_handler = flask_mail.SMTPHandler(
    mailhost=('smtp.gmail.com', 587),
    fromaddr='from@example.com',
    toaddrs=['to@example.com'],
    subject='Critical Error in Application'
)
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

In this example, we set up an SMTP handler that will send an email whenever a critical log message is logged. In the `divide_route`, if there is an attempt to divide by zero, a critical log message is logged, which will trigger the email notification.

:::

## Conclusion

Using the `logging` module allows us to have more control over how and where our log messages are output, and it provides a structured way to manage different levels of logging. It is a best practice to use logging instead of print statements for production applications, as it helps in maintaining clean code and provides better insights into the application's behavior.
