# Python Logging Guide

## Introduction

Python's `logging` library allows programs to record events, errors, and runtime information. Compared to `print()`, logging is configurable, supports levels, and integrates with production systems.

Use logging to:

* Debug code execution
* Monitor long‑running scripts
* Track errors and warnings
* Record timestamps and context automatically

---

## Basic Logging Example

`basicConfig()` sets a default logging setup. `level` defines the minimum severity to record.

Example:

```python
import logging

logging.basicConfig(level=logging.INFO)
logging.info("Application started")
```

---

## Log Levels

Logging levels define the importance of a message. Lower level = more verbose.

* DEBUG: internal details, helps debugging
* INFO: regular application state messages
* WARNING: unexpected situations not breaking execution
* ERROR: failures preventing part of the program from working
* CRITICAL: serious errors stopping the whole program

Example:
Python logging levels:

* DEBUG  == 10
* INFO   == 20
* WARNING == 30
* ERROR   == 40
* CRITICAL == 50

Example:

```python
import logging

logging.basicConfig(level=logging.WARNING)
logging.debug("Debug message")
logging.info("Info message")
logging.warning("Warning message")
logging.error("Error message")
logging.critical("Critical message")
```

---

## Logging to File

Use `filename` and `format` in `basicConfig()` to store logs in a file instead of console.

Example:

```python
import logging

logging.basicConfig(filename="app.log", level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

logging.info("Logging to a file")
```

---

## Debugging with pdb (Python Debugger)

`pdb` allows stepping through code interactively, inspecting variables, and pausing execution.

### Example

```python
import pdb

def divide(a, b):
    pdb.set_trace()  # Breakpoint
    result = a / b
    return result

print(divide(10, 2))
```

### Explanation

* `pdb.set_trace()` pauses execution at that line
* You can run commands in the debug prompt:

  * `n` = next line
  * `s` = step into function
  * `c` = continue to end/breakpoint
  * `p variable` = print a variable
  * `q` = quit debugger

Useful for inspecting program state when debugging complex logic.

---

## Conclusion

The `logging` library enables scalable, configurable debugging and monitoring for applications. It supports multiple outputs, severity levels, and log rotation for production use.
`logging` provides a robust system for tracing how your program runs in real-time and in production environments.
