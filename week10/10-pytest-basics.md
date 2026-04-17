# PyTest

In the previous section, we discussed various types of testing and tools for testing. Now, let's focus on unit testing in Python using PyTest.

PyTest is a popular testing framework for Python that allows us to write simple and scalable test cases. It provides a rich set of features for writing and running tests, including fixtures, parameterization, and powerful assertions. PyTest is an independent testing framework, but it is compatible with Python’s built-in unittest framework and provides a more user-friendly and flexible interface for writing tests.

To get started with PyTest, we can install it using pip:

:::code-group

```bash [pip]
pip install pytest
```

```bash [uv]
uv add pytest
```

:::

Once we have PyTest installed, we can create a test file (e.g., `test_example.py`) and write our test cases.

## Naming Conventions

PyTest uses specific naming conventions by default to discover test files, classes, and functions. Here are the default conventions:

- Test files should be named starting with `test_` or ending with `_test.py` (e.g., `test_example.py` or `example_test.py`).
- Test classes should be named starting with `Test` (e.g., `TestExample`).
- Test functions should be named starting with `test_` (e.g., `test_addition`).

PyTest will automatically discover and run any test files, classes, and functions that follow these naming conventions. We can also customize the naming conventions if needed by using command-line options or configuration files.

## Writing and Running Test Cases

Here is an example of a simple test case using PyTest:

```python
# test_example.py
def add(a, b):
    return a + b

def test_addition():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
    assert add(0, 0) == 0
```

To run the tests, we have to execute the `pytest` command in the terminal:

```bash
(web-venv) himanshu@fedora my-notes  main* $ pytest test_example.py
================================ test session starts =================================
platform linux -- Python 3.14.3, pytest-9.0.3, pluggy-1.6.0
rootdir: /home/himanshu/Documents/IITM/Mad1/my-notes
plugins: Faker-38.2.0
collected 1 item                                                                     

test_example.py .                                                                      [100%]

================================= 1 passed in 0.08s ==================================
```

PyTest will automatically discover the test file `test_example.py` and run the `test_addition` function. If all assertions pass, we will see a success message. If any assertion fails, we will get a detailed error message indicating which assertion failed and what the expected and actual values were.
We can also run specific test files, classes, or functions by providing their names as arguments to the `pytest` command. For example:

```bash
pytest test_example.py
pytest test_example.py::TestExample
pytest test_example.py::TestExample::test_addition
```

This allows us to run specific tests without having to run the entire test suite, which can be useful for debugging and development purposes.

:::details `AssertionError in python and How PyTest Handles It`

In Python, an `AssertionError` is raised when an assertion statement fails. An assertion statement is a way to test if a condition is true, and if it is not, it raises an `AssertionError` with an optional error message. For example:

```python
assert 2 + 2 == 5, "Math is broken!"
# second argument is the error message to be displayed when the assertion fails
```

This will raise an `AssertionError` with the message "Math is broken!" because the condition `2 + 2 == 5` is false.

As `AssertionError` is an Exception subclass, it interrupts the current execution flow unless handled. However, when running tests with PyTest, it catches the `AssertionError` and reports it as a test failure instead of terminating the entire test suite. This allows PyTest to continue running other tests even if one test fails, providing a comprehensive report of all test results at the end of the test run.

A code example of how PyTest handles `AssertionError`:

```python
def test_example1():
    assert 2 + 2 == 5, "Addition is broken!"
    assert 3 * 3 == 8, "Multiplication is broken!"

def test_example2():
    assert 1 - 1 == 0, "Subtraction is broken!"
    assert 4 / 2 == 1, "Division is broken!"
```

output

```bash
test_example.py:7: AssertionError
============================== short test summary info ===============================
FAILED test_example.py::test_example1 - AssertionError: Addition is broken!
FAILED test_example.py::test_example2 - AssertionError: Division is broken!
================================= 2 failed in 0.10s ==================================
```

As we can notice pytest stops executing the current test function after the first failed assertion, but continues executing other test functions, and it will report the failure with the corresponding error message. However, it will continue to execute the next test function, allowing us to see all the failed tests in one run.

**PyTest internally rewrites assert statements to extract expressions and values, which is why it can display detailed failure messages without requiring manual logging.**

:::

## Test Classes

In addition to writing test functions, we can also organize our tests into test classes. A test class is a way to group related tests together and can be useful for organizing larger test suites. Test classes should be named starting with `Test` and should not have an `__init__` method, as pytest handles the instantiation of test classes automatically. Here is an example of a test class in PyTest:

```python
class TestMathOperations:
    def test_addition(self):
        assert 2 + 3 == 5
        assert -1 + 1 == 0
        assert 0 + 0 == 0
    def test_subtraction(self):
        assert 5 - 2 == 2  # incorrect assertion to demonstrate failure
        assert 0 - 1 == -1
        assert 0 - 0 == 0
```

In this example, we have a test class `TestMathOperations` that contains two test methods: `test_addition` and `test_subtraction`. Each test method contains assertions to verify the correctness of the corresponding mathematical operations. When we run the tests, PyTest will automatically discover the test class and execute all the test methods within it, providing a structured way to organize our tests.

Output:

```bash
(web-venv) himanshu@fedora my-notes  main* $ pytest test_example.py
================================ test session starts =================================
platform linux -- Python 3.14.3, pytest-9.0.3, pluggy-1.6.0
rootdir: /home/himanshu/Documents/IITM/Mad1/my-notes
plugins: Faker-38.2.0
collected 2 items                                                                    

test_example.py .F                                                                     [100%]

====================================== FAILURES ======================================
________________________ TestMathOperations.test_subtraction _________________________

self = <test.TestMathOperations object at 0x7f960da88050>

    def test_subtraction(self):
>       assert 5 - 2 == 2
E       assert (5 - 2) == 2

test_example.py:7: AssertionError
============================== short test summary info ===============================
FAILED test_example.py::TestMathOperations::test_subtraction - assert (5 - 2) == 2
============================ 1 failed, 1 passed in 0.13s =============================
```

In this output, we can see that the `test_addition` method passed successfully, while the `test_subtraction` method failed due to an assertion error. PyTest provides detailed information about the failure, including the file name, line number, and the specific assertion that failed. This allows us to quickly identify and fix issues in our code.

## PyTest Workflow

To truly understand how to use PyTest effectively, it's important to understand the typical workflow of pytest execution. The workflow typically involves the following steps:

1. **Test Discovery**: PyTest automatically discovers test files, classes, and functions based on the naming conventions we discussed earlier. It searches for files that match the specified patterns (e.g., `test_*.py` or `*_test.py`) and identifies test classes and functions within those files.
2. **Test Collection**: Once the test files are discovered, PyTest collects the test cases and organizes them into a test suite. This involves creating instances of test classes and preparing the test functions for execution. **If an error occurs outside an assertion (e.g., during setup or import), pytest reports it as an error instead of a failure.**
3. **Test Execution**: PyTest executes the collected test cases one by one. During execution, it evaluates the assertions in each test function and records the results (pass, fail, and other possible outcomes).
4. **Test Reporting**: After all tests have been executed, PyTest generates a test report that summarizes the results of the test run. The report includes information about the number of tests that passed, failed, or encountered errors, as well as details about any failures or errors that occurred during the test execution.

Example of error outside the method/function being tested:

```python
def test_example():
    x = 0
    assert x == 0, "Value is not zero"  

y = 1/0 # This will cause a ZeroDivisionError, which pytest will report as an error instead of a failure.
```

This explanation assumes that we have basic understanding of how python code is executed. Classes are executed top to bottom at global scope, and functions are executed when called. So if these things are not clear, please refer to some basic python tutorial before proceeding further.

## Conclusion

These were the basics of writing and running tests using PyTest. In the next sections, we will explore more advanced features of PyTest, such as fixtures, parameterization, and test discovery options.
