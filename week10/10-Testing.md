# Levels of Testing

[list2card]
- Unit tests 
  → *1 or part of controller* to add course to student→ form working (dummy DB without entire system)→ valid course id-student id → student ❌ >1 → payment gateway regression if 1st test fails →
	- Test individual units of functionality in isolation.
	- clear defined input & output
- integration tests
  of set of units → combined system✅ (❌ dependency violation) → version control systems `CI/CD` each commit to Main branch → re-evaluate [[integration test]]s multiple times a day but ❌ every change)
	- may work independently but compatibility issues on integration with other functions
- System-Testing
   `black-box` includes server, environment (google app engine/aws), DB, persistent connections → all aspects of behaviour (automatic `selenium` + manual)
- Non-functional tests
	- cost
	- No. of instances
	- performance under load
- User Acceptance Testing
  deploy final system → limited `Beta` users → pre-production pilot → user Intelligent feedback
- Static Testing
  Involves reviewing code **without executing** it *Code reviews, correctness proofs*.
- Dynamic Testing
  Involves executing the application with different inputs. *Functional tests, performance tests*
### Test Generation


:::tabs

== API-based
  Using API specifications like Swagger / OpenAPI, the test generator knows:
	- Possible endpoints
	- Required request format
	- Possible error cases
  - It can generate tests for:
	- Input validation
	- Authentication failure
	- Edge cases
	- Incorrect API traffic

== Abstract Tests
  semi formal verbal description (❌ code)
  - apply to generic models

==  Model-based testing
  Scenarios: (Model generates test for each possible <span style="color:rgb(181, 118, 244)"> states &  transitions </span> )
	- abstract models → **executable tests** ![](https://www.einfochips.com/wp-content/uploads/2021/05/test-cases-generated-using-the-state-diagrams.png)
	```mermaid
	flowchart LR
	A["state1: User logged in"] --"Yes"--> AY["show page"]
	A--"No"--> AN["redirect to login page"]
	B["Forgot password"]--"Yes"--> BA["state2: pass reset"] --> BB[redirect to desired page]
	```
== (G)UI testing
  user interface
	- specific elements ✅ present on page
	- ✅ navigation links
	- what happens on random clicks on page ❌ corrupt DB, server crash
		- ❌ programmatic requests (captcha) ✅ browser
			- request gen: `capybara (ruby), py requests`
			- browser automate `selenium`

== Security testing
	- generate invalid inputs to test app behaviour (`SQL injection⚠️/server overload DoS)`
	- `black-box` assume attacker doesn't know implement(miss edge cases) `white-box` know code implementation (over-complicated, focus on less IMP parts)
	- `White-box`  designing test cases based on the **code detailed insights** but 
	- `black-box` only focus on the **expected functionality** & behavior of the application, system testing, acceptance testing, security testing, etc.
	- **Fuzzing** random/semi-random garbage inputs
	- `Grey-box=`Combination of `white-box` & `black-box`

== Regression Testing
	- make sure previous tests does ❌ start failing (modification → break existing features) → `series of tests for all features`
	- **Authentication** (identify & verify like username, password)+ **Authorisation**(role-based access control rights to edit/view)
	
:::

#### Coverage
**Code** coverage: Every line executed at least once.
**Branch** coverage: All decision branches tested.
**Condition** coverage: Each condition within decisions tested. (FTT, TFT, TTT, FFF, null etc)

## Pytest
```python
def func(x)
	return x**2
def test_ans():
	assert func(3)==5
def f():
	raise SystemExit(1)
def test*():
	with pytest.raises(SystemExit):
		f()
Fail: assert 0
```
- Running pytest without mentioning a filename will run all files of format `test_*.py or *_test.py` in the current directory and subdirectories. Pytest automatically identifies those files as test files, for other filenames by explicitly mentioning them.
- Pytest requires the test function names to start with test `test*`
- To execute the tests containing a string in its name: `file if not then fn name`
- **Test Fixtures**: setup some date b4 test & remove after test (Pytest  folder with dummy DB/users/files) <span style="color:rgb(98, 151, 208)">  defined, reliable and consistent context for the tests. </span> 


```python
import os
import tempfile
import pytest
import flaskr  # Added this import
from flaskr import create_app
from flaskr.db import init_db

@pytest.fixture
def client(): #provides a fresh Flask test client for every test, which simulates browser-like behavior.
	db_fd, db_path = tempfile.mkstemp()
	app = create_app({'TESTING': True, 'DATABASE': db_path})

	with app.test_client() as client:
		with app.app_context():
			init_db()
		yield client
	os.close(db_fd)
	os.unlink(db_path)

def test_empty_db(client):
	response = client.get('/') #simulates a GET request.
	assert b'No entries here so far' in response.data

def login(client, username, password):
	return client.post('/login', data=dict(
	username=username,
	password=password)
	, follow_redirects=True) #simulates a POST request.


def logout(client):
	return client.get('/logout', follow_redirects=True)

def test_login_logout(client):
	username = flaskr.app.config["USERNAME"]
	password = flaskr.app.config["PASSWORD"]

	# Test successful login
	response = login(client, username, password) #is in bytes, so compare using b'Text'.
	assert response.status_code == 200
	assert b'You were logged in' in response.data

	# Test successful logout
	response = logout(client)  # Corrected function call
	assert b'You were logged out' in response.data

	# Test invalid username
	response = login(client, f'{username}x', password) # Corrected function call
	assert b'Invalid username' in response.data

	# Test invalid password
	response = login(client, username, f'{password}x') # Corrected function call
	assert b'Invalid password' in response.data

@pytest.fixture
def setup_list():
	return ['Baskaran', 'Yashvi', 'Priya','Himanshu','Abhijeet', 'Gunavanthy', 'Preethi','Kanwal']
```
```bash
pytest -k <substring-v
```
 Markers are used to set various features/attributes to test functions. Pytest provides many inbuilt markers such as xfail, skip and parametrize. 
```bash
@pytest.mark.<markername>
pytest -m <markername> -v #verbose
```


#### Parameterization

Allows you to run the same test with different inputs.
```python
import pytest

@pytest.mark.parametrize("a,b,result", [(1, 2, 3), (3, 4, 7), (5, 5, 10)])
def test_addition(a, b, result):
    assert a + b == result
```

**Analogy:** Like giving a quiz to multiple students with the same question but different answers.

---

#### Skipping & Expected Failures

```python
import pytest

@pytest.mark.skip(reason="Work in progress")
def test_login():
    assert False

@pytest.mark.xfail(reason="Bug #101")
def test_feature():
    assert 1 == 2
```

* `@pytest.mark.skip`: Skip a test
* `@pytest.mark.xfail`: Expect it to fail (without breaking suite)

---

#### **Grouping with Markers & Filtering**

Markers allow grouping tests and selectively running them.
```python
import pytest

@pytest.mark.slow
def test_large_data():
    assert True
```

Run only slow tests: `pytest -m slow`


#### **Shared Fixtures with conftest.py**

To avoid duplicating fixtures across test files.

**Analogy:** Like placing shared utensils in a kitchen drawer (`conftest.py`) instead of repeating them at every table.


[list2node]

- Structure
	```
	project/
	├── tests/
	│   ├── test_1.py
	│   ├── test_2.py
	│   └── conftest.py
	```
	- conftest.py
		```python
		import pytest
		@pytest.fixture
		def fruit_basket():
		    return ["apple", "banana", "cherry"]
		```
	- reuse fruit_basket
		**test_1.py:**
		```python
		def test_banana_in_basket(fruit_basket):
		    assert "banana" in fruit_basket
		```

* Pytest automatically looks for fixtures in `conftest.py`
* No need to import `fruit_basket` manually

:::info Check the following links for more details:
1. https://flask-security-too.readthedocs.io/en/stable/configuration.html
2. https://dev.to/doabledanny/git-cheat-sheet-50-commands-free-pdf-and-poster-4gcn
:::