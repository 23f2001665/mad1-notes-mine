"""
Week 6 notes -- claim checker.

Every check takes one statement or code example from the week6 notes and runs it for real:

    * REST / idempotency app ........ the note's Flask app is exec'd and the "send the same request twice" table
                                      of the note is replayed against it
    * Flask-RESTful examples ........ every example app of 6-flask-restful-basics.md is exec'd and driven with
                                      Flask's test client (resources, reqparse, marshal, errors, database example, form)
    * Flask-RESTful claims .......... inspected on the installed package (what it does / does not provide)
    * data formats .................. the JSON / YAML / XML blocks of the note are parsed and compared; comments,
                                      size and parsing speed are measured with Python's json / PyYAML / xml.etree
    * OpenAPI ....................... every YAML snippet is parsed and the complete example is validated with
                                      openapi-spec-validator (3.0.3 and 3.1.0)
    * curl .......................... a local reference server is started and the note's curl commands are run
                                      exactly as written (line continuations included)

and reports whether the notes are right:

    OK     -> the notes say what actually happens
    WRONG  -> the notes say something that does not happen (the evidence shows what does)

A check usually has two halves: the FACT (measured here) and the NOTE TEXT (the markdown contains the correct
statement and not the wrong one). The claims are written as the notes state them *after* the accuracy fixes, so
a clean run ends with "0 WRONG".  NOTES_DIR=<folder> runs the checker against another copy of the notes.

Run (from anywhere):
    pip install flask flask-sqlalchemy flask-restful pyyaml openapi-spec-validator
    python week6/verify_week6_claims.py [-v]

A check whose library / tool is missing is skipped and listed at the end (MERMAID_JS=... enables the diagram check).
Checked against CPython 3.13, Flask 3.1, Flask-RESTful 0.3.10, Flask-SQLAlchemy 3.1, openapi-spec-validator 0.9, curl 8.
"""
import contextlib
import importlib.util
import io
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import timeit
import warnings
from pathlib import Path

HERE = Path(__file__).resolve().parent
NOTES = Path(os.environ.get("NOTES_DIR") or HERE)
logging.disable(logging.CRITICAL)
warnings.simplefilter("ignore")
RESULTS, SKIPPED = [], []
HAVE = {m: importlib.util.find_spec(m) is not None for m in ("flask", "flask_restful", "flask_sqlalchemy", "yaml", "openapi_spec_validator")}


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def note(name):
    return (NOTES / name).read_text(encoding="utf-8")


def md_files():
    return sorted(NOTES.glob("*.md"))


def check(file, claim, fn):
    try:
        ok, evidence = fn()
    except Exception as e:
        ok, evidence = False, f"raised {type(e).__name__}: {str(e).splitlines()[0][:170] if str(e) else ''}"
    RESULTS.append((ok, file))
    print(f"[{'OK   ' if ok else 'WRONG'}] {file}\n        claim   : {claim}\n        actual  : {evidence}\n")


def need(*libs):
    missing = [l for l in libs if not HAVE[l]]
    if missing:
        SKIPPED.append(f"checks needing {', '.join(missing)} skipped (pip install {' '.join(m.replace('_', '-') for m in missing)})")
    return not missing


def has(text, pattern, flags=re.I | re.S):
    return re.search(pattern, text, flags) is not None


def unquote(text):
    return re.sub(r"(?m)^> ?", "", text)


def blocks(text):
    t = unquote(text)
    return [(m.group(1).lower(), m.group(2), m.start(), m.end())
            for m in re.finditer(r"^[ \t]*```[ \t]*([\w+-]*)[^\n]*\n(.*?)^[ \t]*```[ \t]*$", t, re.S | re.M)]


def find(fname, needle, lang="python", nth=0):
    hits = [b for b in blocks(note(fname)) if b[0] == lang and needle in b[1]]
    if len(hits) <= nth:
        raise LookupError(f"{fname}: no ```{lang} block containing {needle!r}")
    return hits[nth][1]


def github_slug(heading):
    s = re.sub(r"[`*_]", "", re.sub(r"<[^>]+>", "", heading).strip().lower())
    return re.sub(r"[^\w\- ]", "", s, flags=re.UNICODE).replace(" ", "-")


def strip_fences(text):
    return re.sub(r"^[ \t]*```.*?^[ \t]*```", "", unquote(text), flags=re.S | re.M)


@contextlib.contextmanager
def workdir(files=None):
    d = tempfile.mkdtemp()
    old = os.getcwd()
    os.chdir(d)
    for rel, content in (files or {}).items():
        p = Path(d, rel)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
    try:
        yield Path(d)
    finally:
        os.chdir(old)
        shutil.rmtree(d, ignore_errors=True)


def build(code, prelude=""):
    """exec a note's code as a module (not __main__); database files are replaced by an in-memory SQLite."""
    code = re.sub(r"sqlite:///[\w./]+", "sqlite://", code)
    ns = {"__name__": "note_app"}
    exec(compile(prelude + code, "note", "exec"), ns)
    app = ns["app"]
    app.config["PROPAGATE_EXCEPTIONS"] = False
    return ns, app.test_client()


def create_tables(ns):
    with ns["app"].app_context():
        ns["db"].create_all()


def body(r):
    return r.get_data(as_text=True).strip()


def jb(r):
    return (r.status_code, r.get_json())


# --------------------------------------------------------------------------- #
# 6-Rest-APIs.md
# --------------------------------------------------------------------------- #
def rest_idempotency_table():
    if not (need("flask", "flask_sqlalchemy")):
        return None
    F = "6-Rest-APIs.md"
    code = find(F, "def update_user")
    ns, c = build(code)
    create_tables(ns)
    t = note(F)
    sec = t[t.index("Sending the same request twice"):]
    rows = [r for r in re.findall(r"^\|(.+)\|$", sec.split("\n\n")[1], re.M)][2:]
    problems, n = [], 0
    for r in rows:
        cells = [x.strip() for x in r.split("|")]
        m = re.match(r"`(PUT|POST|DELETE) (\S+)`(?: with `(\{.*\})`)?", cells[0])
        method, path, js = m.group(1), m.group(2), (json.loads(m.group(3)) if m.group(3) else None)
        want = [re.match(r"`(\d{3}) (\{.*?\})`", x) for x in cells[1:3]]
        for i, w in enumerate(want):
            got = c.open(path, method=method, json=js)
            n += 1
            if (got.status_code, got.get_json()) != (int(w.group(1)), json.loads(w.group(2))):
                problems.append(f"{method} {path} call {i + 1}: note {w.group(1)} {w.group(2)} / real {got.status_code} {got.get_json()}")
    with ns["app"].app_context():
        rows_left = [u.id for u in ns["User"].query.order_by(ns["User"].id)]
    # extra behaviours the text relies on
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        c.put("/users/50", json={"name": "Z"})
        c.delete("/users/50")
        legacy = [x for x in w if "Legacy" in x.category.__name__]
    nameless = (c.put("/users/51", json={}).status_code, c.post("/users").status_code, c.post("/users", json={"name": ""}).status_code)
    good = (not has(t, r"User\.query\.get") and has(t, r"db\.session\.get\(User") and has(t, r"name is required"))
    return (not problems and n == 6 and rows_left == [8, 9] and not legacy and nameless == (400, 400, 400) and good), (
        f"the 6 request/response cells of the note's table reproduce exactly ({problems or 'no differences'}); after PUT x2, POST x2, DELETE x2 the table holds ids {rows_left} (PUT: one row, POST: two new rows, DELETE: gone); "
        f"no LegacyAPIWarning ({len(legacy)}); PUT/POST without a name -> {nameless} (the old code crashed with a 500 KeyError on PUT); note uses db.session.get and validates the name: {good}")


def rest_concept_text():
    t = note("6-Rest-APIs.md")
    good = (has(t, r"only \*\*optional\*\* constraint") and has(t, r"PATCH \(not guaranteed to be idempotent\)") and has(t, r"\| PUT, DELETE \| No \| Yes \|") and has(t, r"does NOT keep any per-client state")
            and has(t, r"client cannot tell whether it is connected directly") and has(t, r"the server labels every response as cacheable") and has(t, r"four parts")
            and has(t, r"\| PATCH  \| Update part of a resource \|") and has(t, r"HATEOAS, part of the uniform interface but often left out")
            and not has(t, r"Divide app into view, controller and model\. \[MVC\]") and not has(t, r"HATEOAS – optional advanced concept") and not has(t, r"\| PUT    \| Update  \|"))
    return good, f"REST constraints text: layered system is about intermediaries (MVC is an internal split), code on demand is the only optional constraint, PATCH is not guaranteed idempotent, safe vs idempotent table, PATCH row, HATEOAS wording: {good}"


# --------------------------------------------------------------------------- #
# 6-flask-restful-basics.md
# --------------------------------------------------------------------------- #
F6 = "6-flask-restful-basics.md"


def plain_flask_and_basic():
    if not need("flask", "flask_restful"):
        return None
    ns, c = build(find(F6, "def items():"))
    plain = (jb(c.get("/items")), c.post("/items").status_code)
    from flask import Flask
    bad = Flask(__name__)
    bad.add_url_rule("/items", "items", lambda: "x", methods=["GET"])
    only_get = bad.test_client().post("/items").status_code
    ns2, c2 = build(find(F6, "class ItemList(Resource):\n    def get(self):\n        return {'items'"))
    r = c2.get("/items")
    shown = json.loads(find(F6, '"items"', "json"))
    t = note(F6)
    good = has(t, r"methods=\['GET', 'POST'\]") and has(t, r"405 Method Not Allowed") and has(t, r"`@app\.route` decorator") and not has(t, r"we have used `flask routes`") and not has(t, r"componenets")
    return (plain == ((200, {"items": ["item1", "item2", "item3"]}), 201) and only_get == 405 and r.get_json() == shown and r.content_type == "application/json" and good), (
        f"plain Flask route with methods GET+POST works ({plain}); with methods=['GET'] a POST is {only_get} (the POST branch of the old example was unreachable); Flask-RESTful ItemList returns the JSON shown ({r.get_json()}, {r.content_type}); note fixed ('flask routes' -> @app.route): {good}")


def resource_classes():
    if not need("flask", "flask_restful"):
        return None
    ns, c = build(find(F6, "class ItemList(Resource):          # the collection"))
    ok = (jb(c.get("/items")) == (200, {"items": ["item1", "item2", "item3"]}) and jb(c.post("/items")) == (201, {"message": "Item created successfully"})
          and jb(c.get("/items/5")) == (200, {"item": "item5"}) and c.put("/items/5").status_code == 200 and c.delete("/items/5").status_code == 200 and c.post("/items/5").status_code == 405)
    # the pitfall: one class, two URLs, methods with different signatures
    from flask import Flask
    from flask_restful import Api, Resource
    app = Flask(__name__)
    api = Api(app)

    class One(Resource):
        def get(self, item_id): return {"item": item_id}
        def post(self): return {"m": "created"}, 201

    api.add_resource(One, "/item/<int:item_id>", "/item")
    app.config["PROPAGATE_EXCEPTIONS"] = False
    cc = app.test_client()
    pit = (cc.get("/item/5").status_code, cc.post("/item").status_code, cc.get("/item").status_code, cc.post("/item/5").status_code)
    app2 = Flask(__name__)
    api2 = Api(app2)

    class Two(Resource):
        def get(self, item_id=None): return {"all": True} if item_id is None else {"item": item_id}
        def post(self, item_id=None): return {"m": "created"}, 201

    api2.add_resource(Two, "/item", "/item/<int:item_id>")
    c2 = app2.test_client()
    fixed = (c2.get("/item").status_code, c2.get("/item/5").status_code, c2.post("/item").status_code, c2.post("/item/5").status_code)
    t = note(F6)
    good = has(t, r"two kinds of URLs, the \*\*collection\*\*") and has(t, r"`GET /item` calls `get\(\)` without `item_id`") and has(t, r"\*\*500 Internal Server Error\*\*") and has(t, r"def get\(self, item_id=None\)") and not has(t, r"api\.add_resource\(Item, '/item/<int:item_id>', '/item'\)\n")
    return ok and pit == (200, 201, 500, 500) and fixed == (200, 200, 201, 201) and good, (
        f"ItemList (/items) + Item (/items/<id>) behave as described and POST /items/5 is 405 ({ok}); ONE class on both URLs: GET /item/5 {pit[0]}, POST /item {pit[1]}, but GET /item {pit[2]} and POST /item/5 {pit[3]} are 500 (TypeError); "
        f"with item_id=None defaults all work {fixed}; note explains the pitfall and the two-class design: {good}")


def reqparse_examples():
    if not need("flask", "flask_restful"):
        return None
    ns, c = build(find(F6, "class ItemList(Resource):\n    def post(self):\n        args = parser.parse_args()  # process"))
    r = {"ok": jb(c.post("/items", json={"name": "pen", "price": 1.5})), "no_name": jb(c.post("/items", json={"price": 1})),
         "abc": jb(c.post("/items", json={"name": "pen", "price": "abc"})), "form": c.post("/items", data={"name": "pen", "price": "1"}).status_code,
         "query": c.post("/items?name=pen&price=1").status_code, "nobody": c.post("/items").status_code}
    ns2, c2 = build(find(F6, "category = args['category']"))
    ch = (jb(c2.post("/items", json={"name": "x", "price": 1, "category": "toys"})), jb(c2.post("/items", json={"name": "x", "price": 1}))[1]["message"], jb(c2.post("/items", json={"name": "x", "price": 1, "category": "food"}))[0])
    from flask_restful import reqparse
    loc = reqparse.Argument("x").location
    t = note(F6)
    good = (has(t, r'`201 \{"message": "Item pen with price 1\.5 created successfully"\}`') and has(t, r'`400 \{"message": \{"name": "Name of the item is required"\}\}`')
            and has(t, r'`400 \{"message": \{"price": "Price of the item is required"\}\}`') and has(t, r"`415 Unsupported Media Type`") and has(t, r"The default is the JSON body")
            and has(t, r'`400 \{"message": \{"category": "Category must be one of: electronics, clothing, food"\}\}`'))
    ok = (r["ok"] == (201, {"message": "Item pen with price 1.5 created successfully"}) and r["no_name"] == (400, {"message": {"name": "Name of the item is required"}})
          and r["abc"] == (400, {"message": {"price": "Price of the item is required"}}) and r["form"] == r["query"] == r["nobody"] == 415
          and ch[0] == (400, {"message": {"category": "Category must be one of: electronics, clothing, food"}}) and "None" in ch[1] and ch[2] == 201 and loc == ("json", "values"))
    return ok and good, (f"reqparse: JSON ok {r['ok'][0]}, missing name -> {r['no_name']}, price 'abc' -> {r['abc'][1]['message']} (the help text), form / query string / no body -> {r['form']}, {r['query']}, {r['nobody']} (415: default location is JSON); "
                         f"choices -> {ch[0][0]}, optional category missing -> None, default location {loc}; every row of the note's table is stated in the note: {good}")


def frontend_form():
    if not need("flask", "flask_restful"):
        return None
    t = note(F6)
    form = find(F6, 'action="/items"', "html")
    code = find(F6, "def form():")
    with workdir({"templates/form.html": form}):
        ns, c = build(code)
        page = c.get("/").get_data(as_text=True)
        posted = jb(c.post("/items", data={"name": "pen", "price": "1.5"}))
        as_json = c.post("/items", json={"name": "pen", "price": 1.5}).status_code
        # the same app without location='form' (as the note used to be written)
        ns2, c2 = build(code.replace("location='form', ", ""))
        old = c2.post("/items", data={"name": "pen", "price": "1.5"}).status_code
        ns3, c3 = build(code.replace("location='form'", "location=['form', 'args']"))
        comb = (c3.post("/items?name=a&price=1").status_code, c3.post("/items", data={"name": "a", "price": "1"}).status_code)
    good = (has(t, r"location='form'") and has(t, r"415 Unsupported Media Type") and has(t, r"location=\['form', 'args'\]") and re.search(r"import [^\n]*reqparse", code) is not None and "render_template" in code)
    return ("<form" in page and posted == (201, {"message": "Item pen with price 1.5 created successfully"}) and as_json == 400 and old == 415 and comb == (201, 201) and good), (
        f"the form page is served by a normal route ({'<form' in page}); the form post is parsed with location='form' -> {posted[0]}; WITHOUT location the same form is answered {old} (the old example, which also forgot `import reqparse`); "
        f"a JSON body to a form parser -> {as_json}; location=['form','args'] reads both form and query ({comb}); note explains it: {good}")


def database_example():
    if not need("flask", "flask_restful", "flask_sqlalchemy"):
        return None
    ns, c = build(find(F6, "class UserItemApi(Resource):"))
    create_tables(ns)
    res = [jb(c.post("/user", json={"name": "Alice"})), jb(c.post("/user/1/item", json={"item_name": "pen"})), jb(c.get("/user/1")), jb(c.get("/item/1")),
           jb(c.patch("/user/1", json={"name": "Alicia"})), jb(c.delete("/item/1")), jb(c.get("/item/1")), jb(c.get("/user/99")), jb(c.post("/user/99/item", json={"item_name": "x"})),
           c.post("/user/1/item", json={}).status_code, c.post("/user", json={}).status_code, c.get("/user/1/foo").status_code]
    exp = [(201, {"message": "User Alice created successfully", "id": 1}), (201, {"message": "Item pen purchased by user Alice successfully"}), (200, {"user": "Alice", "purchases": ["pen"]}),
           (200, {"item": "pen", "user": "Alice"}), (200, {"message": "User Alicia updated successfully"}), (200, {"message": "Item deleted successfully"}), (404, {"message": "Item not found"}),
           (404, {"message": "User not found"}), (404, {"message": "User not found"}), 400, 400, 404]
    rules = sorted(r.rule for r in ns["app"].url_map.iter_rules() if r.endpoint != "static")
    t = note(F6)
    good = has(t, r"four resource classes") and has(t, r"`UserList` creates a user") and "UserItemApi" in find(F6, "api.add_resource(UserItemApi") and not has(t, r"User\.query\.get") and not has(t, r"request_data = \{'name': 'new_user'\}")
    return res + [] == exp and rules == ["/item/<int:item_id>", "/user", "/user/<int:user_id>", "/user/<int:user_id>/item"] and good, (
        f"the note's database example now runs: create user, buy item, read user + purchases, read item, patch, delete, 404s, 400s for missing fields; every response matches ({res == exp}); routes {rules}; "
        f"the old code registered a class `UserItemApi` that did not exist (NameError at import) and never registered `UserApi`; note describes 4 resource classes: {good}")


def marshal_examples():
    if not need("flask", "flask_restful"):
        return None
    ns, c = build(find(F6, "@marshal_with(item_fields)"))
    a = (jb(c.get("/items/1")), jb(c.get("/items/2")))
    ns2, c2 = build(find(F6, "return marshal(item, item_fields)"))
    b = (jb(c2.get("/items/1")), jb(c2.get("/items/2")))
    # the trap: returning an error dict from a marshal_with method
    from flask import Flask
    from flask_restful import Api, Resource, fields, marshal_with
    app = Flask(__name__)
    api = Api(app)
    flds = {"id": fields.Integer, "name": fields.String(attribute="item_name"), "user": fields.String(attribute="user_name")}

    class Trap(Resource):
        @marshal_with(flds)
        def get(self): return {"message": "Item not found"}, 404

    api.add_resource(Trap, "/t")
    trap = jb(app.test_client().get("/t"))
    t = note(F6)
    good = (has(t, r'`GET /items/1` returns `\{"id": 1, "name": "pen", "user": "Alice"\}`') and has(t, r'`404 \{"message": "Item not found"\}`') and has(t, r'\{"id": 0, "name": null, "user": null\}')
            and has(t, r"attribute='item_name'") and re.search(r"from flask_restful import [^\n]*\bmarshal\b(?!_)", find(F6, "return marshal(item, item_fields)")) is not None)
    ok = (a == ((200, {"id": 1, "name": "pen", "user": "Alice"}), (404, {"message": "Item not found"})) and b == a and trap == (404, {"id": 0, "name": None, "user": None}))
    return ok and good, (f"marshal_with + abort(404, message=...) -> {a[1]}; manual marshal() -> {b[0][1]} and the error dict unchanged ({b[1][1]}); THE TRAP: returning ({{'message': ...}}, 404) from a marshal_with method gives {trap[1]} "
                         f"(status stays 404, the message is lost); the old marshal example imported only marshal_with but called marshal (NameError) and read attributes (name/price/category) that the Purchase model does not have; note explains it: {good}")


def error_examples():
    if not need("flask", "flask_restful"):
        return None
    ns, c = build(find(F6, "def not_found(error):"))
    e = (jb(c.get("/item/1")), jb(c.get("/item/9")), c.get("/nothing").get_json())
    # unexpected exception: JSON 500 only when not propagating
    from flask import Flask
    from flask_restful import Api, Resource, abort
    app = Flask(__name__)
    api = Api(app)

    class Boom(Resource):
        def get(self): raise RuntimeError("boom")

    class FlaskAbort(Resource):
        def get(self):
            from flask import abort as fabort
            fabort(404)

    api.add_resource(Boom, "/boom")
    api.add_resource(FlaskAbort, "/fa")
    app.errorhandler(404)(lambda err: ({"message": "custom 404"}, 404))
    app.config["PROPAGATE_EXCEPTIONS"] = False
    off = jb(app.test_client().get("/boom"))
    app.config["PROPAGATE_EXCEPTIONS"] = True
    try:
        app.test_client().get("/boom")
        on = "no error"
    except RuntimeError:
        on = "RuntimeError raised (debugger page)"
    app.config["PROPAGATE_EXCEPTIONS"] = False
    fa = jb(app.test_client().get("/fa"))
    # custom errors: errors= and handle_error
    ns2, c2 = build(find(F6, "errors = {"))
    c1 = jb(c2.get("/item/1"))
    ns3, c3 = build(find(F6, "class MyApi(Api):"))
    c3r = jb(c3.get("/item/1"))
    ns4, c4 = build("from werkzeug.exceptions import HTTPException\nfrom flask_restful import Resource, Api\n"
                    "class CustomError(HTTPException):\n    def __init__(self, message, status_code):\n        super().__init__(description=message)\n        self.code = status_code\n"
                    "@app.errorhandler(CustomError)\ndef handle_custom_error(error):\n    return {'message': error.description, 'status_code': error.code}, error.code\n"
                    "class R(Resource):\n    def get(self): raise CustomError('Item not found', 404)\napi = Api(app)\napi.add_resource(R, '/r')\n", prelude="from flask import Flask\napp = Flask(__name__)\n")
    wrong_way = jb(c4.get("/r"))
    t = note(F6)
    good = (has(t, r"`GET /item/9` \| `404 \{\"message\": \"Item not found\"\}`") and has(t, r"is sent as it is and never goes through an error handler") and has(t, r"only when debug mode is off")
            and has(t, r"is \*\*not\*\* used for exceptions raised inside Flask Restful resources") and has(t, r'`404 \{"message": "Item not found", "status": 404\}`') and has(t, r'`404 \{"message": "Item not found", "status_code": 404\}`')
            and has(t, r"abort\(status_code, message=\.\.\.\)"))
    ok = (e == ((200, {"name": "pen"}), (404, {"message": "Item not found"}), {"message": "The resource you are looking for was not found"}) and off == (500, {"message": "Internal Server Error"}) and on.startswith("RuntimeError")
          and fa == (404, {"message": "The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again."})
          and c1 == (404, {"message": "Item not found", "status": 404}) and c3r == (404, {"message": "Item not found", "status_code": 404}) and wrong_way == (404, {"message": "Item not found"}))
    return ok and good, (f"abort(404, message=) inside a resource -> {e[1][1]}; an unknown URL goes to the app's @app.errorhandler(404) -> {e[2]}; flask.abort(404) inside a resource does NOT -> Flask-RESTful's own default message ({fa[1]['message'][:30]}...); "
                         f"unexpected exception: JSON 500 when not propagating ({off[0]}), {on} when debug/propagate is on; custom HTTPException via Api(errors=...) -> {c1[1]}, via handle_error -> {c3r[1]}; "
                         f"the old way (@app.errorhandler(CustomError)) ignores our status_code field -> {wrong_way[1]}; note says all this: {good}")


def features_claims():
    if not need("flask_restful"):
        return None
    import flask_restful
    import pkgutil
    from flask.views import MethodView
    subs = sorted(m.name for m in pkgutil.iter_modules(flask_restful.__path__) if not m.name.startswith("_"))
    names = [n.lower() for n in dir(flask_restful)] + subs
    missing_features = not any(k in n for n in names for k in ("pagina", "swagger", "openapi", "authent", "login", "token"))
    t = note(F6)
    good = (has(t, r"What it does not provide") and has(t, r"\*\*Authentication\*\*: not built in") and has(t, r"\*\*Pagination\*\*: not built in") and has(t, r"not generated by Flask Restful")
            and has(t, r"Testing tools\*\*: none of its own") and has(t, r"`method_decorators = \[\.\.\.\]`") and not has(t, r"Flask Restful can help us implement pagination") and not has(t, r"Flask Restful provides tools for testing")
            and not has(t, r"integrated with tools like Swagger to automatically generate"))
    return (subs == ["fields", "inputs", "representations", "reqparse", "utils"] and issubclass(flask_restful.Resource, MethodView) and missing_features
            and hasattr(flask_restful.Resource, "method_decorators") and any(m == "application/json" for m, _ in flask_restful.DEFAULT_REPRESENTATIONS)) and good, (
        f"flask_restful contains only the modules {subs}; nothing named pagination / auth / swagger / openapi exists in it ({missing_features}); Resource is a Flask MethodView and supports method_decorators; "
        f"the note's feature list now separates what it provides from what it does not (the old list claimed pagination, authentication, testing tools and automatic Swagger docs): {good}")


# --------------------------------------------------------------------------- #
# 6-openapi-specification.md : formats
# --------------------------------------------------------------------------- #
F7 = "6-openapi-specification.md"


def format_blocks():
    import xml.etree.ElementTree as ET
    import yaml
    js, ym, xm = find(F7, '"courses"', "json"), find(F7, "courses:", "yaml"), find(F7, "<student", "xml")
    return js, ym, xm, json, yaml, ET


def formats_equivalent_and_measured():
    if not need("yaml"):
        return None
    js, ym, xm, json_, yaml, ET = format_blocks()
    a = json_.loads(js)
    b = yaml.safe_load(ym)
    root = ET.fromstring(xm)
    c = {"id": root.get("id"), "name": root.findtext("name"), "email": root.findtext("email"), "courses": [x.text for x in root.find("courses")]}
    same = a == b and {**c, "id": int(c["id"])} == a
    xml_text_only = isinstance(c["id"], str)
    sizes = (len(ym), len(js), len(xm))
    t_json = min(timeit.repeat(lambda: json_.loads(js), number=2000, repeat=3))
    t_xml = min(timeit.repeat(lambda: ET.fromstring(xm), number=2000, repeat=3))
    t_yaml = min(timeit.repeat(lambda: yaml.safe_load(ym), number=200, repeat=3)) * 10
    fails = {}
    for label, text in (("comment", '{"a": 1 /* c */}'), ("single quotes", "{'a': 1}"), ("unquoted key", "{a: 1}"), ("trailing comma", '{"a": 1,}')):
        try:
            json_.loads(text)
            fails[label] = "accepted"
        except json_.JSONDecodeError:
            fails[label] = "error"
    try:
        yaml.safe_load("a:\n\t- 1")
        tabs = "accepted"
    except yaml.YAMLError:
        tabs = "error"
    yaml_comment = yaml.safe_load("a: 1  # c") == {"a": 1}
    yaml_reads_json = yaml.safe_load('{"a": [1, 2], "b": null, "c": true}') == {"a": [1, 2], "b": None, "c": True}
    xml_comment = ET.fromstring("<a><!-- c --><b>1</b></a>").findtext("b") == "1"
    t = note(F7)
    good = (has(t, r"YAML Ain't Markup Language") and not has(t, r"Yet Another Markup Language") and has(t, r"Most compact") and has(t, r"\*\*Parsing Speed\*\* \(Python's libraries\)\s*\|\s*Fastest\s*\|\s*Slowest\s*\|\s*In between")
            and has(t, r"Not supported\s*\|\s*Supported `#`") and has(t, r"tabs are not allowed") and has(t, r"Everything is text") and has(t, r"No comments and no trailing commas") and not has(t, r"Language-independent, with built-in support in most programming languages like"))
    ok = (same and xml_text_only and sizes[0] < sizes[1] < sizes[2] and t_json < t_xml < t_yaml and set(fails.values()) == {"error"} and tabs == "error" and yaml_comment and yaml_reads_json and xml_comment)
    return ok and good, (f"the JSON, YAML and XML blocks of the note describe the SAME record ({same}); XML gives text only (id -> {c['id']!r}); sizes of the blocks: YAML {sizes[0]} < JSON {sizes[1]} < XML {sizes[2]}; "
                         f"parse time per document: json {t_json / 2000 * 1e6:.1f} us < xml.etree {t_xml / 2000 * 1e6:.1f} us < PyYAML {t_yaml / 2000 * 1e6:.0f} us (so XML is NOT slower than YAML in Python); "
                         f"JSON rejects comments / single quotes / unquoted keys / trailing commas ({fails}); YAML rejects tab indentation ({tabs}), accepts # comments and JSON text; XML has comments; "
                         f"note: acronym 'YAML Ain't Markup Language', size/speed rows and key points fixed: {good}")


# --------------------------------------------------------------------------- #
# OpenAPI snippets
# --------------------------------------------------------------------------- #
def openapi_valid():
    if not need("yaml", "openapi_spec_validator"):
        return None
    import yaml
    from openapi_spec_validator import validate
    t = note(F7)
    snippets = [(b[1], t[:0]) for b in blocks(t) if b[0] == "yaml"]
    problems, parsed, docs = [], 0, 0
    for code, _ in snippets:
        try:
            data = yaml.safe_load(code)
            parsed += 1
        except yaml.YAMLError as e:
            problems.append(f"does not parse: {code[:30]!r} {e}")
            continue
        if isinstance(data, dict) and "openapi" in data:
            docs += 1
            try:
                validate(data)
            except Exception as e:
                problems.append(f"invalid OpenAPI document starting {code[:30]!r}: {str(e).splitlines()[0][:80]}")
    full = [c for c, _ in snippets if "securitySchemes" in c][0]
    v31 = yaml.safe_load(full.replace("openapi: 3.0.3", "openapi: 3.1.0"))
    try:
        validate(v31)
        v31ok = True
    except Exception:
        v31ok = False
    # facts the text states
    def invalid(text):
        try:
            validate(yaml.safe_load(text))
            return False
        except Exception:
            return True
    base = "openapi: 3.0.3\ninfo: {title: t, version: '1'}\npaths:\n  /u:\n    get:\n      responses:\n"
    unquoted = invalid(base + "        200:\n          description: ok\n")
    quoted = not invalid(base + "        '200':\n          description: ok\n")
    no_info = invalid("openapi: 3.0.3\npaths: {}\n")
    no_responses = invalid("openapi: 3.0.3\ninfo: {title: t, version: '1'}\npaths:\n  /u:\n    get:\n      summary: s\n")
    path_not_required = invalid(full.replace("          required: true\n", "", 1)) if "required: true" in full else True
    good = (has(t, r"unquoted `200:` is read by YAML as a number") and has(t, r"path parameters must be `required: true`") and has(t, r"`openapi`, `info` \(with `title` and `version`\) and `paths` are required")
            and has(t, r"formerly|old name of the specification") and has(t, r"RFC 9457") and not has(t, r"<SwaggerUI") and not has(t, r"\n  200:\n"))
    return (not problems and docs >= 2 and v31ok and unquoted and quoted and no_info and no_responses and path_not_required and good), (
        f"{parsed} YAML snippets parse, {docs} OpenAPI documents validate with openapi-spec-validator (the complete example also as 3.1.0: {v31ok}); problems: {problems or 'none'}; "
        f"facts stated in the note: an unquoted `200:` makes the document invalid ({unquoted}), '200' is fine ({quoted}), `info` is required ({no_info}), every operation needs `responses` ({no_responses}), path parameters must be required ({path_not_required}); "
        f"the old first snippet (openapi + paths only) was invalid; the <SwaggerUI/> component is replaced by a real document; note text: {good}")


def tooling_text():
    t = note(F7)
    good = (has(t, r"flask_pydantic` validates requests with pydantic models, not with the OpenAPI file") and has(t, r"connexion or flask-smorest") and has(t, r"`type: apiKey`") and has(t, r"`scheme: bearer`")
            and has(t, r"POST` is not idempotent \(and `PATCH` is not guaranteed to be\)") and not has(t, r"all are idempotent except `POST`") and not has(t, r"Standard error format"))
    return good, f"tooling / idempotency / error-format wording corrected (flask_pydantic is not OpenAPI validation, PATCH is not guaranteed idempotent, error format is a convention): {good}"


# --------------------------------------------------------------------------- #
# curl against a real server
# --------------------------------------------------------------------------- #
def curl_commands():
    if not (need("flask") and shutil.which("curl")):
        if not shutil.which("curl"):
            SKIPPED.append("curl checks skipped (curl not installed)")
        return None
    from flask import Flask, jsonify, request
    from werkzeug.serving import make_server
    app = Flask(__name__)
    users = {1: {"id": 1, "name": "Priya Shah", "email": "priya@example.com"}}

    @app.route("/user", methods=["POST"])
    def add():
        data = request.get_json()
        return jsonify(message="User added", data=data), 201

    @app.route("/user/<int:i>", methods=["GET", "PUT", "DELETE"])
    def one(i):
        if request.method == "GET":
            return jsonify(users[1])
        if request.method == "PUT":
            return jsonify(message="User updated", data=request.get_json())
        return jsonify(message="User deleted")

    srv = make_server("127.0.0.1", 0, app, threaded=True)
    port = srv.server_port
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        t = note(F7)
        sec = t[t.index("## Testing the API with curl"):t.index("## Idempotency")]
        cmds = [b[1].strip() for b in blocks(sec) if b[0] == "bash"]
        out = []
        for cmd in cmds:
            p = subprocess.run(["bash", "-c", cmd.replace("127.0.0.1:5000", f"127.0.0.1:{port}")], capture_output=True, text=True, timeout=30)
            out.append((p.returncode, p.stdout.strip()))
        # shown responses of the Thunder Client section
        tc = t[t.index("## Testing with Thunder Client"):t.index("## Testing the API with curl")]
        shown = [json.loads(b[1]) for b in blocks(tc) if b[0] == "json"]
        shown_resp = [shown[0], shown[2], shown[4], shown[5]]            # GET, POST, PUT, DELETE responses (the others are request bodies)
        got = [json.loads(o[1]) if o[1].startswith("{") else None for o in out]
        # the commands as the note used to write them (no line continuation)
        old = subprocess.run(["bash", "-c", f'curl -sS -X POST http://127.0.0.1:{port}/user \n-H "Content-Type: application/json" \n-d \'{{"name": "R"}}\''], capture_output=True, text=True, timeout=30)
        nojson_header = subprocess.run(["curl", "-sS", "-o", "/dev/null", "-w", "%{http_code}", f"http://127.0.0.1:{port}/user", "-d", '{"name":"x"}'], capture_output=True, text=True, timeout=30).stdout
    finally:
        srv.shutdown()
    ok = (len(cmds) == 4 and all(o[0] == 0 for o in out) and got == shown_resp and "415" in old.stdout and nojson_header == "415")
    good = (has(t, r"line continuation\*\* at the end of every line") and has(t, r"curl.exe") and has(t, r"requires|is required for Flask's `request\.get_json\(\)`") and has(t, r"user 3 remains \*\*deleted\*\*")
            and all(re.search(r"\\\n", c) for c in cmds[1:3]) and not has(t, r"ensures user 1 remains"))
    return ok and good, (f"the note's 4 curl commands run against a local reference server exactly as written (bash line continuations): exit codes {[o[0] for o in out]}, and their JSON equals the responses shown in the Thunder Client section ({got == shown_resp}); "
                         f"the OLD multi-line form without backslashes sends only the first line -> {old.stdout[:60].strip()!r} (415 page); `-d` without the JSON Content-Type header -> {nojson_header}; note: continuation + header + Windows hints + 'user 3' fixed: {good}")


# --------------------------------------------------------------------------- #
# mermaid (optional)
# --------------------------------------------------------------------------- #
def mermaid_renders():
    js, node = os.environ.get("MERMAID_JS"), shutil.which("node")
    if not (js and Path(js).exists() and node):
        SKIPPED.append("mermaid render check skipped (set MERMAID_JS=.../mermaid.min.js, needs node + playwright)")
        return None
    diagrams = []
    for f in md_files():
        for m in re.finditer(r"^\s*```mermaid\n(.*?)^\s*```", f.read_text(encoding="utf-8"), re.S | re.M):
            diagrams.append((f.name, m.group(1)))
    with tempfile.TemporaryDirectory() as d:
        Path(d, "in.json").write_text(json.dumps([x[1] for x in diagrams]))
        Path(d, "r.js").write_text(r"""
const { chromium } = require('playwright'); const fs = require('fs');
(async () => { const [js, input] = process.argv.slice(2); const ds = JSON.parse(fs.readFileSync(input, 'utf8'));
  const b = await chromium.launch(); const p = await b.newPage(); await p.setContent('<html><body></body></html>'); await p.addScriptTag({ path: js });
  const out = await p.evaluate(async (ds) => { mermaid.initialize({ startOnLoad: false }); const res = [];
    for (let i = 0; i < ds.length; i++) { try { const { svg } = await mermaid.render('d' + i, ds[i]);
      const doc = new DOMParser().parseFromString(svg, 'image/svg+xml');
      res.push({ ok: true, text: [...doc.querySelectorAll('text, foreignObject')].map(n => n.textContent.trim()).filter(Boolean) });
    } catch (e) { res.push({ ok: false, err: String(e.message || e).split('\n')[0] }); } } return res; }, ds);
  console.log(JSON.stringify(out)); await b.close(); })();
""")
        env = dict(os.environ, NODE_PATH=subprocess.run(["npm", "root", "-g"], capture_output=True, text=True).stdout.strip())
        p = subprocess.run([node, str(Path(d, "r.js")), js, str(Path(d, "in.json"))], capture_output=True, text=True, env=env)
        res = json.loads(p.stdout.strip().splitlines()[-1])
    bad = [f"{n}: {r['err']}" for (n, _), r in zip(diagrams, res) if not r["ok"]] + [f"{n}: literal markup {t}" for (n, _), r in zip(diagrams, res) if r["ok"] for t in r["text"] if "**" in t]
    return not bad, f"{len(diagrams)} mermaid diagrams rendered with real mermaid; errors / literal markup: {bad or 'none'}"


# --------------------------------------------------------------------------- #
# markdown / GitHub hygiene
# --------------------------------------------------------------------------- #
def no_vitepress_syntax():
    found = []
    for f in md_files():
        for i, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if re.match(r"^\s*:::|^\s*== ?\S|^\s*```\s*\w+\s*\[", line) or re.search(r"<[A-Z][\w-]*[^>]*/>", re.sub(r"`[^`]*`", "", line)):
                found.append(f"{f.name}:{i}")
    return not found, f"VitePress-only syntax (::: / == / ```lang [Label] / Vue components): {found or 'none'}"


def no_stripped_html():
    found = []
    for f in md_files():
        t = re.sub(r"<!--.*?-->", "", strip_fences(f.read_text(encoding="utf-8")), flags=re.S)
        t = re.sub(r"`[^`\n]*`", "", t)
        for m in re.finditer(r"<(?!/)[^>]*(\sstyle\s*=|\sclass\s*=)[^>]*>|&emsp;", t):
            found.append(f"{f.name}: {m.group(0)[:50]}")
    return not found, f"HTML that GitHub strips (style=, class=, &emsp;) outside code blocks: {found or 'none'}"


def alerts_valid():
    bad = []
    for f in md_files():
        for i, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            m = re.match(r"^> \[!(\w+)\]\s*$", line)
            if m and m.group(1) not in {"NOTE", "TIP", "IMPORTANT", "WARNING", "CAUTION"}:
                bad.append(f"{f.name}:{i}")
            if re.match(r"^>\s*\[!\w+\]\S", line):
                bad.append(f"{f.name}:{i} text after [!TYPE]")
    return not bad, f"invalid GitHub alert syntax: {bad or 'none'}"


def details_balanced():
    bad = []
    for f in md_files():
        t = f.read_text(encoding="utf-8")
        o, c = len(re.findall(r"<details>", t)), len(re.findall(r"</details>", t))
        if o != c:
            bad.append(f"{f.name}: {o} <details> vs {c} </details>")
        for m in re.finditer(r"<summary>(.*?)</summary>", t, re.S):
            if "`" in m.group(1):
                bad.append(f"{f.name}: backticks in <summary>")
    return not bad, f"unbalanced <details> / backticks in <summary>: {bad or 'none'}"


def links_resolve():
    bad = []
    for f in md_files():
        text = re.sub(r"```.*?```", "", f.read_text(encoding="utf-8"), flags=re.S)
        for m in list(re.finditer(r"!?\[[^\]]*\]\(([^)\s]+)\)", text)) + list(re.finditer(r'<a href="([^"]+)"', text)):
            url = m.group(1)
            if re.match(r"(https?:|mailto:|#)", url):
                continue
            path, _, anchor = url.partition("#")
            target = (f.parent / path).resolve()
            if not target.exists():
                bad.append(f"{f.name}: {url} (file not found)")
            elif anchor and target.suffix == ".md":
                tt = target.read_text(encoding="utf-8")
                slugs = {github_slug(h) for h in re.findall(r"^#{1,6}\s+(.*)$", tt, re.M)} | set(re.findall(r'<a id="([^"]+)"', tt))
                if anchor not in slugs:
                    bad.append(f"{f.name}: {url} (no such heading / anchor)")
    return not bad, f"local links / anchors / images that do not resolve: {bad or 'none'}"


def fences_clean():
    bad = []
    for f in md_files():
        open_ = False
        for i, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            line = re.sub(r"^>\s?", "", line)
            m = re.match(r"^(\s*)```(.*)$", line)
            if not m:
                continue
            if not open_:
                open_ = True
                if "[" in m.group(2) or m.group(2).startswith(" "):
                    bad.append(f"{f.name}:{i} {line!r}")
            else:
                open_ = False
                if m.group(2).strip():
                    bad.append(f"{f.name}:{i} closing fence {line!r}")
        if open_:
            bad.append(f"{f.name}: unclosed fence")
    return not bad, f"labelled / badly closed / unclosed fences: {bad or 'none'}"


def typos():
    t = note(F6) + note("6-Rest-APIs.md") + note(F7)
    bad = [p for p in (r"componenets", r"Deprication", r"Marshall and Marshal_with", r"which format use choose", r"Which format use choose") if has(t, p)]
    return not bad, f"typos still present: {bad or 'none'}"


# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    R, F, O = "6-Rest-APIs.md", F6, F7
    print("=" * 78 + "\nWeek 6 claim checker\n" + "=" * 78 + "\n")
    for c, claim, fn in ((R, "the idempotency app: PUT x2 = one row, POST x2 = two rows, DELETE x2 = gone; every cell of the note's table is reproduced", rest_idempotency_table),
                         (F, "plain Flask route (methods must include POST) and the basic Flask-RESTful resource", plain_flask_and_basic),
                         (F, "ItemList + Item resource classes; one class on two URLs gives 500 for the other signature", resource_classes),
                         (F, "reqparse: JSON by default (415 for form / query / no body), 400 messages, choices, default location", reqparse_examples),
                         (F, "the HTML-form example needs location='form' (and the page must be served)", frontend_form),
                         (F, "the database example runs end to end (UserList / UserApi / UserItemApi / ItemApi)", database_example),
                         (F, "marshal_with / marshal: attribute=, abort inside marshal_with, the error-dict trap", marshal_examples),
                         (F, "error handling: abort(message=), app.errorhandler only for unrouted URLs, debug vs 500, Api(errors=), handle_error", error_examples),
                         (F, "what Flask-RESTful does and does NOT provide (pagination, authentication, docs, testing)", features_claims),
                         (O, "JSON / YAML / XML blocks are the same record; comments, size, parsing speed, key rules measured", formats_equivalent_and_measured),
                         (O, "every YAML snippet parses, the complete example is a valid OpenAPI 3.0.3 / 3.1.0 document, quoting of '200', required parts", openapi_valid),
                         (O, "the note's curl commands run as written against a real server; the old form without backslashes does not", curl_commands),
                         ("week6/*.md", "mermaid diagrams render", mermaid_renders)):
        try:
            r = fn()
        except Exception as e:                       # e.g. the section the check needs does not exist in the notes
            r = (False, f"raised {type(e).__name__}: {str(e).splitlines()[0][:170] if str(e) else ''}")
        if r is not None:
            check(c, claim, lambda r=r: r)
    check(R, "REST constraints wording (layered system, code on demand, PATCH, safe vs idempotent, HATEOAS)", rest_concept_text)
    check(O, "tooling / idempotency / error-format wording", tooling_text)
    check("week6/*.md", "no typos", typos)
    check("week6/*.md", "no VitePress-only syntax (:::, ==, ```lang[label], Vue components)", no_vitepress_syntax)
    check("week6/*.md", "no HTML that GitHub strips (style=, class=, &emsp;) outside code blocks", no_stripped_html)
    check("week6/*.md", "GitHub alerts written correctly", alerts_valid)
    check("week6/*.md", "<details> balanced, no backticks in <summary>", details_balanced)
    check("week6/*.md", "every local link, #anchor and image resolves", links_resolve)
    check("week6/*.md", "code fences are labelled/closed cleanly", fences_clean)

    wrong = [f for ok, f in RESULTS if not ok]
    print("=" * 78)
    print(f"{len(RESULTS)} checks, {len(RESULTS) - len(wrong)} OK, {len(wrong)} WRONG")
    if wrong:
        print("files with WRONG statements:", ", ".join(sorted(set(wrong))))
    print("\nNOT VERIFIABLE HERE (kept because they are standard, but not executed):")
    for s in sorted(set(SKIPPED)) + [
        "HTTP method properties (safe / idempotent: RFC 9110), RFC 9457 (problem+json), 'reqparse is slated for removal' (Flask-RESTful documentation), the existence of Flask-RESTX / flask-smorest / apispec / connexion",
        "Windows quoting for curl (^ continuation, escaped quotes, curl.exe in PowerShell) and the Thunder Client / Postman screenshots (static/week6/*.png)",
        "REST constraints are Roy Fielding's dissertation (2000) - terminology, not executable; external links (swagger, TDS, Google, StackOverflow) are blocked from this sandbox",
    ]:
        print("  -", s)
    sys.exit(1 if wrong else 0)
