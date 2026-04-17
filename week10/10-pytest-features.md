# Pytest Features

In the previous section, we discussed the basics of writing tests in pytest. Now let's explore some of the key features of pytest that make it a powerful and flexible testing framework for Python.

## Fixtures

Fixtures are a powerful feature in pytest that allow us to set up an environment for our tests. They can be used to create test data, set up database connections, or perform any necessary setup before running the tests. Fixtures are defined using the `@pytest.fixture` decorator and can be used in test functions by including them as parameters.Fixtures act like dependency injection—pytest automatically provides required resources based on function parameters. Here's an example of how to use fixtures in pytest:

```python
import pytest

@pytest.fixture
def sample_data():
    return {"name": "Alice", "age": 30}

# now we can use the sample_data fixture in our test function
def test_sample_data(sample_data): # we don't need to call the function
    assert sample_data["name"] == "Alice"
    assert sample_data["age"] == 30
```

In this example, the `sample_data` fixture returns a dictionary with some sample data. The `test_sample_data` function uses the fixture by including it as a parameter, and pytest will automatically call the fixture function and pass its return value to the test function.

### Fixture Scope

Fixtures can have different scopes, which determine how often the fixture is set up and torn down. The available scopes are:

- `function`: The fixture is set up and torn down for each test function (default).
- `class`: The fixture is set up and torn down once per test class.
- `session`: The fixture is set up and torn down once per test session.
- `module`: The fixture is set up and torn down once per test module.
- `package`: The fixture is set up and torn down once per test package. This is useful for larger projects with multiple modules and subpackages.

```python
import pytest
@pytest.fixture(scope="module") # this fixture will be set up once for the entire module and shared among all tests in the module
def sample_data():
    return {"name": "Alice", "age": 30}

def test_sample_data1(sample_data):
    assert sample_data["age"] == 30
    sample_data["name"] = "Bob" # this will affect all tests that use the sample_data fixture

def test_sample_data2(sample_data):
    assert sample_data["name"] == "Bob"
```

output:

```bash
==================== 2 passed in 0.05s =====================
```

### conftest.py

The `conftest.py` file is a special configuration file in pytest that allows us to define fixtures and hooks that can be shared across multiple test modules. It is typically placed in the root directory of the test suite or in a subdirectory, and pytest will automatically discover and use the fixtures defined in it. This is useful for organizing and reusing fixtures across different test modules without having to import them explicitly. For example, if we have a `conftest.py` file with the following content:

```python
import pytest

@pytest.fixture
def sample_data():
    return {"name": "Alice", "age": 30}
```

We can then use the `sample_data` fixture in any test module within the same directory or subdirectories without having to import it:

```python
def test_sample_data(sample_data):
    assert sample_data["name"] == "Alice"
    assert sample_data["age"] == 30
```

When we run the tests, pytest will automatically discover the `sample_data` fixture from the `conftest.py` file and use it in the test function. But the local fixtures defined in the test module will take precedence over the fixtures defined in `conftest.py` if there is a name conflict.

:::info conftest.py

The name `conftest.py` is a convention in pytest. This is case-sensitive, so it must be named exactly `conftest.py` for pytest to recognize it as a configuration file. If we name it differently, pytest will not discover the fixtures defined in it unless imported or configured explicitly.

:::

## Markers

Markers are a way to categorize and organize tests in pytest. They allow us to label tests with specific tags, which can be used to selectively run or skip tests based on certain criteria. We can define custom markers using the `@pytest.mark` decorator.

```python
import pytest

@pytest.mark.slow
def test_slow_function():
    pass

@pytest.mark.fast
def test_fast_function():
    raise Exception("This test is broken!")
```

To run only the tests marked as `slow`, we can use the following command:

```bash
pytest -m slow
```

Output:

```bash
==================== 1 passed, 1 deselected, 2 warnings in 0.06s =====================
```

In this example, we have two test functions, one marked as `slow` and the other marked as `fast`. When we run the tests with the `-m slow` option, only the test marked as `slow` will be executed, while the test marked as `fast` will be disselected. By default, user-defined markers will throw a warning when used. That's why we have `2 warnings`, `1 passed`, and `1 deselected` in the output.

:::info User-defined markers

- If we don't select which markers to run, all the tests will be executed

- By default, user-defined markers don't have any special meaning and throw a warning when used. To avoid this warning and define a custom behavior for user-defined markers, we can add the marker to the `pytest.ini` configuration file. For example, if we want to define a custom marker called `slow`, we can add the following lines to our `pytest.ini` file. But for now, we can ignore the warnings and use the markers as needed.

:::

### Marker Types

Markers can be categorized into different types based on their purpose and usage. Here are some common types of markers in pytest:

- **Custom Markers**: These are user-defined markers that can be created to categorize tests based on specific criteria. For example, we can create markers like `slow`, `fast`, `database`, etc., to label tests based on their characteristics or requirements.
- **Built-in Markers**: Pytest provides several built-in markers that have specific meanings
and behaviors. Some common built-in markers include:
  - `skip`: Used to skip a test unconditionally.
  - `skipif`: Used to skip a test conditionally based on a specified condition.
  - `xfail`: Used to mark a test as expected to fail due to known issues or bugs.
  - `parametrize`: Used to run a test function with different sets of input data.
  - `usefixtures`: Used to specify that a test function should use a particular fixture.

### Marker Algebra

Pytest markers follow the rules of boolean algebra, which means we can combine markers using logical operators like `and`, `or`, and `not`. This allows us to create complex test selection criteria based on multiple markers. For example, if we want to run tests that are marked as `slow` and not marked as `fast`, we can use the following command:

```bash
pytest -m "slow and not fast"
```

This is equivalent of `{slow} ∩ {not fast}` in set theory, which means we want to run tests that are in the `slow` set and not in the `fast` set.

### Marker Inheritance

Markers can also be inherited by test classes and modules. If we mark a test class with a specific marker, all the test functions within that class will inherit that marker. Similarly, if we mark a test module with a specific marker, all the test functions within that module will inherit that marker. This allows us to organize our tests and apply markers at different levels of our test suite.

```python
import pytest
@pytest.mark.slow
class TestSlowFunctions:
    def test_slow_function1(self):
        pass
    def test_slow_function2(self):
        pass
```

In this example, the `TestSlowFunctions` class is marked as `slow`, which means that both `test_slow_function1` and `test_slow_function2` will inherit the `slow` marker. When we run the tests with the `-m slow` option, both of these test functions will be executed.

## Parametrization

Parametrization is a built-in-marker in pytest that allows us to run a test function with different sets of input data. This is useful for testing the same functionality with multiple inputs without having to write separate test functions for each case. We can use the `@pytest.mark.parametrize` decorator to achieve this.

```python
import pytest

@pytest.mark.parametrize("x,y, expected", [
    (1, 2, 3),
    (2, 3, 5),
    (3, 3, 7)
])
def test_addition(x, y, expected):
    assert x + y == expected

def test_subtraction():
    assert 5 - 2 == 3
```

In this example, the `test_addition` function will be run three times with different values of `x`, `y`, and `expected`.

Running the tests will give us the following output:

```bash
pytest -m parametrize test_example.py  # or just pytest test_example.py
```

Output:

```bash
===================== 1 failed, 2 passed, 1 deselected in 0.10s ======================
```

In this output, we can see that the first two test cases for addition passed, while the third test case failed because `3 + 3` does not equal `7`. The `test_subtraction` function is not parametrized and will be executed as a regular test.

## Skipping Tests

Sometimes, we may want to skip certain tests based on specific conditions. Pytest provides the `@pytest.mark.skip` and `@pytest.mark.skipif` decorators to skip tests unconditionally or conditionally, respectively.

```python
import pytest

@pytest.mark.skip(reason="This test is not relevant for the current environment.")
def test_irrelevant():
    pass
@pytest.mark.skipif(condition=True, reason="This test is skipped because the condition is true.")
def test_conditional_skip():
    pass

def test_normal():
    assert 1 + 1 == 2
```

run the tests:

```bash
pytest test_example.py
```

Output:

```bash
==================== 1 passed, 2 skipped in 0.05s =====================
```

In this example, the `test_irrelevant` function is skipped unconditionally with a reason provided, while the `test_conditional_skip` function is skipped conditionally based on the value of `condition`. The `test_normal` function will be executed as a regular test.

## Expected Failures

Pytest also provides a way to mark tests that are expected to fail using the `@pytest.mark.xfail` decorator. This is useful for tests that are known to fail due to bugs or unimplemented features, but we still want to include them in our test suite.

```python
import pytest

@pytest.mark.xfail(reason="This test is expected to fail due to a known bug.")
def test_known_issue():
    assert 1 + 1 == 3
def test_normal():
    assert 1 + 1 == 2
```

run the tests:

```bash
pytest test_example.py
```

Output:

```bash
==================== 1 passed, 1 xfailed in 0.05s =====================
```

In this example, the `test_known_issue` function is marked as expected to fail with a reason provided. When we run the tests, we see that it is reported as `xfailed`, indicating that it failed as expected, while the `test_normal` function passed successfully.

:::info pass in xfail

- If a test marked with `@pytest.mark.xfail` unexpectedly passes, it will be reported as `xpassed`, indicating that it passed when it was expected to fail.

:::

## Flags in pytest

Pytest provides several command-line flags that can be used to control the behavior of the test runner. Some common flags include:

- `-v` or `--verbose`: Increases the verbosity of the test output, showing more details about each test case.
- `-q` or `--quiet`: Decreases the verbosity of the test output, showing only the summary of test results.
- `-s`: Disables output capturing, allowing you to see print statements and other output from the tests in real-time.
- `-k`: Allows you to specify an expression to select tests based on their names or markers. For example, `pytest -k "addition"` will run all tests that have "addition" in their name. It matches substrings in test names, class names, and other identifiers (like markers). So `pytest -k "add"` will also run tests with "addition" in their name.
- `-m`: Allows you to specify a marker expression to select tests based on their markers. For example, `pytest -m "slow"` will run all tests marked with `slow`.
- `-x` or `--exitfirst`: Stops the test run after the first failure is encountered.
- `--maxfail`: Specifies the maximum number of test failures before pytest stops running the tests. For example, `pytest --maxfail=2` will stop the test run after 2 failures.
- `--tb`: Controls the traceback style for failed tests. For example, `pytest --tb=short` will show a shorter traceback for failed tests.
- `--disable-warnings`: Suppresses warning messages during the test run.

These flags can be combined to customize the test run according to your needs. For example, you can run tests with increased verbosity and select specific tests based on their names or markers using a combination of `-v`, `-k`, and `-m` flags.

## Summary

In this section, we explored some of the key features of pytest, including fixtures, markers, parametrization, skipping tests, expected failures, and command-line flags. These features make pytest a powerful and flexible testing framework for Python, allowing us to write efficient and organized tests for our code. In the next section, we will dive deeper into writing unit tests using pytest and explore best practices for test organization and maintenance.

Pytest also supports various plugins that can extend its functionality, such as `pytest-cov` for measuring test coverage, `pytest-mock` for mocking objects in tests, and `pytest-xdist` for running tests in parallel. These plugins can be easily installed and integrated into your pytest workflow to enhance your testing capabilities.

In the next section, we will focus on writing unit tests using pytest for flask applications. Till then you can explore the pytest documentation and try out the features we discussed in this section to get a better understanding of how pytest works and how it can be used to write effective tests for your Python code.

### Complete Code Example

```python
import pytest

#skip
@pytest.mark.skip(reason="Work in progress")
def test_feature0():
    assert False   # <-- This will be *skipped*, not executed

#xfail
@pytest.mark.xfail(reason="Bug #101")
def test_feature1():
    assert 1 == 2  # <-- Expected to fail

#xpass
@pytest.mark.xfail(reason="Bug #101")
def test_feature2():
    assert 1 == 1  # <-- Expected to fail, but will return XPASS, This demonstrates XPASS (unexpected pass)

#parameterize
@pytest.mark.parametrize("a, b, result", [(1, 2, 3), (4, 5, 9), (1, 5, 8)])
def test_feature3(a, b, result):
    assert a + b == result


#custom markers
@pytest.mark.my_marker_1
def test_feature4():
    assert  1 == 1

@pytest.mark.my_marker_1
def test_feature5():
    assert 1 == 2

@pytest.mark.my_marker_2
def test_feature6():
    assert 1 == 1

@pytest.mark.my_marker_2
def test_feature7():
    assert 1 == 2


#fixture and conftest.py
# scope defines how often the fixture be running. For every function or class or module or session or package.
@pytest.fixture(scope='function')  # or it can be class, module or session or package
def data_list():
    return [1, 2, 3]

def test_feature8(data_list):
    assert sum(data_list) == 6

def test_feature9(data_list):
    assert sum(data_list) == 5

# While fixtures can be imported, the preferred way to share them is via conftest.py
from file2 import data_list2        # [2, 4, 6]

def test_feature10(data_list2):
    assert sum(data_list2) == 12

def test_feature11(data_list2):
    assert sum(data_list2) == 11

# we can also use conftest.py to import fixture in all files in the current directory and subdirectories.
# import not needed it is present in downward hierarchy scope.

def test_feature12(data_list3):     # [4, 5, 9]
    print("hello")                  # use -s flag `pytest -s` to see the output from print()
    assert sum(data_list3) == 18

def test_feature13(data_list3):      
    assert sum(data_list3) == 20

#tmpdir (legacy)
def test_tmpdir(tmpdir):
    file = tmpdir.join("example.txt")
    file.write("Hello pytest")
    assert file.read() == "Hello pytest"

#tmp_path (modern, pathlib)
def test_tmp_path(tmp_path):
    file = tmp_path / "example.txt"
    file.write_text("Hello tmp_path")
    assert file.read_text() == "Hello tmp_path"

class TestMath:
    def test_addition(self):
        assert 1 + 1 == 2

    def test_subtraction(self):
        assert 2 - 1 == 1

    def test_multiplication(self):
        assert 2 * 3 == 6
    
```

Output:

```bash
(web) himanshu@debian:~/Desktop/pytest_directory$ pytest -s -v
======================================== test session starts =========================================
platform linux -- Python 3.13.3, pytest-8.4.1, pluggy-1.6.0 -- /home/himanshu/Documents/Mad1/web/bin/python
cachedir: .pytest_cache
rootdir: /home/himanshu/Desktop/pytest_directory
configfile: pytest.ini
plugins: Faker-37.4.0
collected 16 items                                                                                   

test_xfails.py::test_feature0 SKIPPED (Work in progress)
test_xfails.py::test_feature1 XFAIL (Bug #101)
test_xfails.py::test_feature2 XPASS (Bug #101)
test_xfails.py::test_feature3[1-2-3] PASSED
test_xfails.py::test_feature3[4-5-9] PASSED
test_xfails.py::test_feature3[1-5-8] FAILED
test_xfails.py::test_feature4 PASSED
test_xfails.py::test_feature5 FAILED
test_xfails.py::test_feature6 PASSED
test_xfails.py::test_feature7 FAILED
test_xfails.py::test_feature8 PASSED
test_xfails.py::test_feature9 FAILED
test_xfails.py::test_feature10 PASSED
test_xfails.py::test_feature11 FAILED
test_xfails.py::test_feature12 hello
PASSED
test_xfails.py::test_feature13 FAILED

============================================== FAILURES ==============================================
________________________________________ test_feature3[1-5-8] ________________________________________

a = 1, b = 5, result = 8

    @pytest.mark.parametrize("a, b, result", [(1, 2, 3), (4, 5, 9), (1, 5, 8)])
    def test_feature3(a, b, result):
>       assert a + b == result
E       assert (1 + 5) == 8

test_xfails.py:21: AssertionError
___________________________________________ test_feature5 ____________________________________________

    @pytest.mark.my_marker_1
    def test_feature5():
>       assert 1 == 2
E       assert 1 == 2

test_xfails.py:31: AssertionError
___________________________________________ test_feature7 ____________________________________________

    @pytest.mark.my_marker_2
    def test_feature7():
>       assert 1 == 2
E       assert 1 == 2

test_xfails.py:39: AssertionError
___________________________________________ test_feature9 ____________________________________________

data_list = [1, 2, 3]

    def test_feature9(data_list):
>       assert sum(data_list) == 5
E       assert 6 == 5
E        +  where 6 = sum([1, 2, 3])

test_xfails.py:52: AssertionError
___________________________________________ test_feature11 ___________________________________________

data_list2 = [2, 4, 6]

    def test_feature11(data_list2):
>       assert sum(data_list2) == 11
E       assert 12 == 11
E        +  where 12 = sum([2, 4, 6])

test_xfails.py:61: AssertionError
___________________________________________ test_feature13 ___________________________________________

data_list3 = [4, 5, 9]

    def test_feature13(data_list3):
>       assert sum(data_list3) == 20
E       assert 18 == 20
E        +  where 18 = sum([4, 5, 9])

test_xfails.py:71: AssertionError
====================================== short test summary info =======================================
FAILED test_xfails.py::test_feature3[1-5-8] - assert (1 + 5) == 8
FAILED test_xfails.py::test_feature5 - assert 1 == 2
FAILED test_xfails.py::test_feature7 - assert 1 == 2
FAILED test_xfails.py::test_feature9 - assert 6 == 5
FAILED test_xfails.py::test_feature11 - assert 12 == 11
FAILED test_xfails.py::test_feature13 - assert 18 == 20
==================== 6 failed, 7 passed, 1 skipped, 1 xfailed, 1 xpassed in 0.13s ====================
```

### References

- [pytest documentation](https://docs.pytest.org/en/stable/)
- [pytest fixtures](https://docs.pytest.org/en/stable/fixture.html)
- [pytest command-line options](https://docs.pytest.org/en/stable/reference.html#command-line-flags)
