# WSGI: How a Web Server Talks to Flask

A **web server** (Apache, Nginx, Gunicorn…) knows how to speak **HTTP**: accept connections, read requests, write responses. A **Flask or Django app** is Python code that knows how to decide *what* the response should be. Something has to connect the two. That something is **WSGI**, the **Web Server Gateway Interface** ([PEP 3333](https://peps.python.org/pep-3333/)).

> [!NOTE]
> WSGI stands for **Web Server Gateway Interface**. (It is sometimes mis-expanded as "Web-Services Gateway Interface", which is wrong.) It is a Python-specific standard, not a protocol on the network.

Without a standard, every framework would need its own code for every server. With WSGI, **any WSGI server can run any WSGI application**: Flask, Django and Pyramid all work behind Gunicorn, Apache (`mod_wsgi`), uWSGI, and so on.

## The contract

A WSGI application is simply **a callable that takes two arguments and returns an iterable of bytes**:

```python
def simple_app(environ, start_response):
    status = '200 OK'
    headers = [('Content-Type', 'text/plain')]
    start_response(status, headers)
    return [b"Hello, WSGI World!"]
```

| Piece | What it is |
| ----- | ---------- |
| `environ` | A dictionary the server fills in with everything about the request |
| `start_response` | A function the app calls **once** to send the status line and headers |
| return value | An iterable of **`bytes`** objects: the response body |

### Request flow

1. The client sends an HTTP request to the web server.
2. The server turns it into an `environ` dictionary and **calls** the application: `app(environ, start_response)`.
3. The application calls `start_response(status, headers)`, then returns the body.
4. The server writes the status, headers and body back to the client.

### What is in `environ`?

Running a real WSGI server (Python's built-in `wsgiref`) and sending `POST /a/b?x=1&y=2` with the body `name=Alice` and an extra header `X-Demo: hello`, the app received:

| Key | Value |
| --- | ----- |
| `REQUEST_METHOD` | `POST` |
| `PATH_INFO` | `/a/b` (the path **without** the query string) |
| `QUERY_STRING` | `x=1&y=2` |
| `SERVER_PROTOCOL` | `HTTP/1.1` |
| `CONTENT_TYPE` / `CONTENT_LENGTH` | `application/x-www-form-urlencoded` / `10` |
| `HTTP_X_DEMO` | `hello`: every request header `Name-Like-This` appears as `HTTP_NAME_LIKE_THIS` |
| `wsgi.input` | a file-like object; reading `CONTENT_LENGTH` bytes from it gives `name=Alice` |
| `wsgi.url_scheme` | `http` |

Flask hides all of this: `request.method`, `request.args`, `request.form` and `request.headers` are built from `environ`.

> [!WARNING]
> The body must be **bytes**, not `str`. Returning `["Hello"]` makes the response fail: the standard checker `wsgiref.validate` reports `Iterator yielded non-bytestring` and the server answers `500`. Flask encodes your strings for you, which is why you rarely notice.

## A Flask app *is* a WSGI application

`app = Flask(__name__)` creates an object that can be **called exactly like `simple_app`**:

```python
from flask import Flask
app = Flask(__name__)

@app.route("/hi")
def hi():
    return "hi"

# what a WSGI server does for each request:
#   body = app(environ, start_response)    # -> [b'hi'], with status '200 OK'
```

This was checked by calling `app(environ, start_response)` by hand: `start_response` received `200 OK`, and the returned body was `b'hi'`. `flask run` uses Werkzeug's development server, which is a WSGI server written for convenience; `gunicorn` is one built for production.

## Middleware

Because an application is just a callable, you can **wrap** one application in another. The wrapper sees the request before the app and the response after it. This is **middleware**.

```python
class AddHeader:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        def start_response_with_header(status, headers, exc_info=None):
            headers = list(headers) + [("X-Handled-By", "AddHeader-middleware")]
            return start_response(status, headers, exc_info)
        return self.app(environ, start_response_with_header)

# with Flask:  app.wsgi_app = AddHeader(app.wsgi_app)
```

With this wrapper installed on a Flask app, every response carried the extra `X-Handled-By` header, and the route code was untouched. Typical uses: authentication, logging, compression, sessions, measuring request time. (Flask extensions and Werkzeug's `ProxyFix` work this way.)

## Servers you will meet

| Component | Role | Examples |
| --------- | ---- | -------- |
| **WSGI server** | Speaks HTTP to clients, calls the app | Gunicorn, uWSGI, Waitress, Apache with `mod_wsgi`; Werkzeug's dev server |
| **Reverse proxy / front web server** | Terminates TLS, serves static files, forwards other requests to the WSGI server | Nginx, Apache |
| **WSGI application** | Your code | Flask, Django, Pyramid app |
| **Middleware** | Wraps the app | authentication, logging, compression |

A typical production layout: *browser → Nginx → Gunicorn → Flask*. Nginx is usually put *in front of* Gunicorn as a proxy instead of running the Python app itself.

Running the same trivial application under Gunicorn:

```bash
gunicorn -w 4 -b 127.0.0.1:8000 mymodule:application
```

answers `200` with the body from the app, and the response header `Server: gunicorn`. The `-w 4` starts 4 worker processes, so four requests can be handled at once, which is what the "scalability" claim of WSGI refers to: it comes from the server running many workers, not from WSGI itself.

> [!WARNING]
> Flask's built-in server (`flask run`, `app.run()`) is for **development only**. It is not designed for production traffic or security hardening. Deploy behind a production WSGI server.

> [!NOTE]
> WSGI is **synchronous**: one request in, one response out. Long-lived two-way connections such as the **WebSockets** of [Asynchronous Updates](8-async-dom.md#websockets) do not fit that model. Its asynchronous successor is **ASGI**, used by frameworks like FastAPI and by Django Channels.

## Practice questions

<details>
<summary>1. What two arguments does a WSGI application receive, and what must it return?</summary>

`environ` (dict with the request) and `start_response` (function for status and headers). It returns an iterable of **bytes**.
</details>

<details>
<summary>2. Why can Gunicorn run both a Flask and a Django app?</summary>

Both are WSGI applications, so both are callables with the same `(environ, start_response)` interface. The server only depends on that interface, not on the framework.
</details>

<details>
<summary>3. What is middleware in WSGI terms?</summary>

A WSGI application that wraps another one, so it can inspect or modify the request before the inner app and the response after it (authentication, logging, compression…).
</details>

<details>
<summary>4. Why should you not use <code>app.run()</code> in production?</summary>

It starts a development server meant for convenience (debugging, auto-reload), not for performance or security. Production uses a WSGI server such as Gunicorn, normally behind Nginx or Apache.
</details>
