# `sys` Module

The `sys` module in Python provides access to some variables used or maintained by the interpreter and to functions that interact strongly with the interpreter. We will only cover a few important aspects of the `sys` module here.

- `sys.argv`: A list of command-line arguments passed to a Python file. The first element is the file name.
- `sys.exit([arg])`: Exit from Python. This function can take an optional argument to specify the exit status.
- `sys.version`: A string containing the version of the Python interpreter.
- `sys.platform`: A string that identifies the platform on which Python is running.

## sys.argv

The `sys.argv` list contains the command-line arguments passed to the file. The first element, `sys.argv[0]`, is the name of the file itself. The subsequent elements are the arguments passed to the file.

Here is an example of how to use `sys.argv` to print the file name and its arguments:

```python
import sys
print("file name:", sys.argv[0])
```

If you run the file with arguments like this:

```bash
python myfile.py arg1 arg2
```

```txt
file name: myfile.py
```

```python
import sys
print(sys.argv)
```

If you run the file with arguments like this:

```bash
python myfile.py argument1 argument2 "complex argument 3"
```

![sys-argv](../static/sys-argv.png)

```txt
['myfile.py', 'argument1', 'argument2', 'complex argument 3']
```

- The first element of `sys.argv` is always the file name.
- If no arguments are passed, `sys.argv` will contain only one element, the file name.
- Arguments are space-separated strings but we can enclose them in quotes to include spaces in arguments or name of the file.

**Note: Python does not decide what arguments are — it simply receives them from the operating system as a list of strings.**

- [Inspect Developer Tools](https://youtu.be/Pf2z_Ue73qE?si=XAul5yx0EI6pAZWH)
- [sys module documentation](https://docs.python.org/3/library/sys.html)
