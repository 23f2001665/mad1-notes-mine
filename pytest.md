# PYTEST: A Comprehensive Guide to Testing in Python

author: himanshu <br>
title: pytest

## Introduction
### What is Pytest?
Pytest is a popular testing framework for Python that makes it easy to write simple and scalable tests. It supports fixtures, parameterized testing, and a rich ecosystem of plugins.
### Why Use Pytest?
- Simple syntax
- Powerful features
- Extensive plugin ecosystem
- Easy to integrate with CI/CD pipelines
- Supports various types of testing (unit, functional, integration)

### Installation
You can install Pytest using pip:
```bash
pip install pytest
```
### Basic Usage
To run tests, simply navigate to your project directory and execute:
```bash
pytest
```
Pytest will automatically discover and run all test files and functions that follow the naming conventions (files starting with `test_` or ending with `_test.py`, and functions starting with `test` example `test_func` and `testfunc` both are valid test functions).

## Writing Tests
### Test Functions
A test function is a simple Python function that starts with the word `test`. Here’s an example:
```python
def test_addition():
    assert 1 + 1 == 2
```
### Test Classes
You can also group tests in classes. Test classes should start with the word `Test` and should not have an `__init__` method (just a suggestion, __init__ method won't have any effect on test cases). Though it is not mandatory, it is a good practice to use classes for better organization of related tests. Here’s an example:
```python
class TestMath:
    def test_subtraction(self):
        assert 2 - 1 == 1
    def test_multiplication(self):
        assert 2 * 3 == 6
```
### Assertions
Pytest uses simple `assert` statements to check for conditions. If the condition is `True`, the test passes; if `False`, the test fails.
```python
def test_division():
    assert 10 / 2 == 5
```
### Skipping Tests
You can skip tests using the `@pytest.mark.skip` decorator:
```python
@pytest.mark.skip(reason="Work in progress")
def test_feature0():
    assert False   # <-- This will be *skipped*, not executed
```
### Expected Failures
You can mark tests that are expected to fail using the `@pytest.mark.xfail` decorator:
```python
#xfail
@pytest.mark.xfail(reason="Bug #101")
def test_feature1():
    assert 1 == 2  # <-- Expected to fail

#xpass
@pytest.mark.xfail(reason="Bug #101")
def test_feature2():
    assert 1 == 1  # <-- Expected to fail, but will return XPASS
```
### Parameterized Tests
You can run a test function with different sets of parameters using the `@pytest.mark.parametrize` decorator:
```python
import pytest
@pytest.mark.parametrize("a, b, result", [(1, 2, 3), (4, 5, 9), (1, 5, 8)])
def test_feature3(a, b, result):
    assert a + b == result
```
this will run the `test_feature3` function three times with different values for `a`, `b`, and `result`.

### Marking Tests
You can categorize tests using custom markers. First, register the marker in `pytest.ini`:
```ini
[pytest]
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
```
Then, use the marker in your tests:
```python
import pytest
@pytest.mark.slow
def test_slow_feature():
    import time
    time.sleep(5)
    assert True
```
You can run tests with specific markers using the `-m` option:
```bash
pytest -m slow
```
Though it is not mandatory to register markers in `pytest.ini`, it is a good practice to avoid warnings. For example:
```python
#costum markers
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
```
You can run tests with specific custom markers using the `-m` option:
```bash
pytest -m my_marker_1
```
### Fixtures
Fixtures are a powerful feature in Pytest that allows you to set up and tear down test environments. You can define a fixture using the `@pytest.fixture` decorator:
```python
import pytest

#fixture and confest.py
# scope defines how often the fixture be running. For every function or class or module or session or package.

@pytest.fixture(scope='function')  # or it can be class, module or session or package
def data_list():
    return [1, 2, 3]

def test_feature8(data_list):
    assert sum(data_list) == 6

def test_feature9(data_list):
    assert sum(data_list) == 5

# we can import fixture from other files using file location.
from file2 import data_list2        # [2, 4, 6]

def test_feature10(data_list2):
    assert sum(data_list2) == 12

def test_feature11(data_list2):
    assert sum(data_list2) == 11

# we can also use conftest.py to import fixture in all files in the current directory and subdirectories.
# import not needed it is present in downward heirarchy scope.

def test_feature12(data_list3):     # [4, 5, 9]
    print("hello")                  # use -s flag `pytest -s` to see the output from print()
    assert sum(data_list3) == 18

def test_feature13(data_list3):      
    assert sum(data_list3) == 20
```
### Tmpdir and TmpPath Fixtures
Pytest provides built-in fixtures `tmpdir` and `tmp_path` for creating temporary directories and files during tests. These directories and files are automatically cleaned up after the test run. tmpdir is legacy feature, while tmp_path is the modern feature and it is recommended to use tmp_path. tmp_path provides a `pathlib.Path` object, which is more versatile and easier to work with.
```python
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
```
- Both are deleted automatically after the test.

## Advanced Features
### Customizing Test Runs
You can customize your test runs using command-line options. Some useful options include:
- `-v`: Verbose mode, shows more details
- `-q`: Quiet mode, less output
- `-k expr`: Run tests that match the expression `expr`
- `-m mark`: Run tests with the specified marker
- `-s`: Show print statements and other output
- `-x`: Stop after first failure
- `--maxfail=num`: Stop after `num` failures. More flexible than -x

**NOTE: All filtering will be done after collection phase. So, if any test doesn't follow the naming conventions, it won't be collected and hence won't be filtered.**

### Plugins
Pytest has a rich ecosystem of plugins that extend its functionality. Some popular plugins include:
- `pytest-cov`: For measuring code coverage
- `pytest-mock`: For easier mocking
- `pytest-xdist`: For parallel test execution
You can install plugins using pip:
```bash
pip install pytest-cov pytest-mock pytest-xdist
```
### Running Tests in Parallel
You can run tests in parallel using the `pytest-xdist` plugin. After installing it, you can use the `-n` option to specify the number of parallel workers:
```bash
pytest -n 4
```
This will run tests using 4 parallel workers.


### Grouping Tests
You can group tests in directories and files. Pytest will automatically discover tests in any subdirectorys as long as they follow the naming conventions.
```
project/
    tests/
        test_math.py
        test_string.py
```

# Example Test File
Here’s an example of a complete test file using various Pytest features discussed above. Save this as `test_example.py`:
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
    assert 1 == 1  # <-- Expected to fail, but will return XPASS

#parameterize
@pytest.mark.parametrize("a, b, result", [(1, 2, 3), (4, 5, 9), (1, 5, 8)])
def test_feature3(a, b, result):
    assert a + b == result


#costum markers
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


#fixture and confest.py
# scope defines how often the fixture be running. For every function or class or module or session or package.
@pytest.fixture(scope='function')  # or it can be class, module or session or package
def data_list():
    return [1, 2, 3]

def test_feature8(data_list):
    assert sum(data_list) == 6

def test_feature9(data_list):
    assert sum(data_list) == 5

# we can import fixture from other files using file location.
from file2 import data_list2        # [2, 4, 6]

def test_feature10(data_list2):
    assert sum(data_list2) == 12

def test_feature11(data_list2):
    assert sum(data_list2) == 11

# we can also use conftest.py to import fixture in all files in the current directory and subdirectories.
# import not needed it is present in downward heirarchy scope.

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

## Output
When you run this file with:
```bash
pytest -v -s
```
You will see output similar to this:
```
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