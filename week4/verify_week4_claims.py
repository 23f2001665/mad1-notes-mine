"""
Week 4 notes -- claim checker.

Every check takes one statement or code example from the week4 notes and runs it
for real:

    * the SQL recap ........ every query is run on an in-memory SQLite database that is built from the
                             tables shown in the note, and its result is compared with the output shown
    * Flask examples ....... the note's own code is exec'd and driven with Flask's test client / CLI
                             (routing, converters, trailing slashes, url_for, url_map, redirect, abort,
                             error handlers, templates, static files, request.*, get_json, file upload)
    * HTML forms ........... headless Chromium submits real forms and the captured requests are checked
                             (encoding, unchecked boxes, disabled/readonly/hidden, file inputs, method="put" ...)
    * the complete form .... is posted to the note's own Flask route (the form's action must exist)
    * every ```html snippet  is validated with the Nu HTML validator (optional)

and reports whether the notes are right:

    OK     -> the notes say what actually happens
    WRONG  -> the notes say something that does not happen (the evidence shows what does)

A check usually has two halves: the FACT (measured here) and the NOTE TEXT (the markdown contains the correct
statement and not the wrong one). The claims are written as the notes state them *after* the accuracy fixes, so
a clean run ends with "0 WRONG".  NOTES_DIR=<folder> runs the checker against another copy of the notes.

Run (from anywhere), in an environment that has Flask:
    pip install flask
    python week4/verify_week4_claims.py [-v]

Optional: node + playwright (browser form checks), VNU_JAR=.../vnu.jar + java (HTML validation).
A check whose tool is missing is skipped and listed at the end.
Checked against CPython 3.13, Flask 3.1, Werkzeug 3.1, SQLite 3.4x, Chromium (playwright 1.63).
"""
import contextlib
import logging
import importlib.util
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
NOTES = Path(os.environ.get("NOTES_DIR") or HERE)
ROOT = HERE.parent
VERBOSE = "-v" in sys.argv
PY = sys.executable
logging.disable(logging.CRITICAL)      # Flask logs the 500 errors that some checks provoke on purpose
RESULTS, SKIPPED = [], []
HAVE_FLASK = importlib.util.find_spec("flask") is not None


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
        ok, evidence = False, f"raised {type(e).__name__}: {str(e).splitlines()[0][:160] if str(e) else ''}"
    RESULTS.append((ok, file))
    print(f"[{'OK   ' if ok else 'WRONG'}] {file}\n        claim   : {claim}\n        actual  : {evidence}\n")


def has(text, pattern, flags=re.I | re.S):
    return re.search(pattern, text, flags) is not None


def unquote(text):
    """Drop the '> ' prefix of GitHub alerts so that code inside an alert can be parsed."""
    return re.sub(r"(?m)^> ?", "", text)


def blocks(text):
    """[(lang, body, start, end)] of every fenced block (code inside > alerts included)."""
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


def loose(s):
    return [l.strip() for l in s.strip().splitlines() if l.strip()]


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


PRELUDE = "from flask import Flask, url_for, request, redirect, abort, render_template, jsonify\napp = Flask(__name__)\n"


def build(code, files=None, prelude=""):
    """exec a note's code as a module (not as __main__) inside a scratch dir; returns (namespace, test client)."""
    import warnings
    warnings.simplefilter("ignore")
    ns = {"__name__": "note_app"}
    exec(compile(prelude + code, "note", "exec"), ns)
    app = ns["app"]
    app.config["PROPAGATE_EXCEPTIONS"] = False
    return ns, app.test_client()


def md_table(text):
    rows = []
    for line in text.splitlines():
        if line.startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if not all(set(c) <= set("-: ") for c in cells):
                rows.append(cells)
    return rows[1:], rows[0] if rows else []


# --------------------------------------------------------------------------- #
# 4-1 / 4-2 : MVC text and SQL
# --------------------------------------------------------------------------- #
def sqlite_facts():
    db = sqlite3.connect(":memory:")
    try:
        db.execute("CREATE PROCEDURE p() BEGIN SELECT 1; END")
        proc = "works"
    except sqlite3.OperationalError:
        proc = "syntax error"
    db.execute("CREATE TABLE t(x INTEGER)")
    db.execute("CREATE TRIGGER tr AFTER INSERT ON t BEGIN INSERT INTO t VALUES (99); END")
    db.execute("INSERT INTO t VALUES (1)")
    trig = db.execute("SELECT COUNT(*) FROM t").fetchone()[0]
    db.commit()
    try:
        with db:
            db.execute("INSERT INTO t VALUES (5)")
            db.execute("INSERT INTO nope VALUES (1)")
    except sqlite3.OperationalError:
        pass
    after = db.execute("SELECT COUNT(*) FROM t").fetchone()[0]
    t = note("4-1-database-layer-MODEL.md")
    good = (has(t, r"SQLite.{0,80}triggers but no stored procedures") and has(t, r"multi-document transactions since version 4\.0")
            and not has(t, r"Paypal, Visa, Oracle") and not has(t, r"Atomic at \*\*document level only\*\*") and not has(t, r"^-\s*$", re.M))
    return proc == "syntax error" and trig == 2 and after == 2 and good, (
        f"SQLite: CREATE PROCEDURE -> {proc}; CREATE TRIGGER works (insert fired the trigger: {trig} rows); a failed transaction is rolled back completely ({after} rows); "
        f"note says SQLite has triggers but no stored procedures, MongoDB multi-document transactions since 4.0 (documented, not run), no 'Oracle' bank, no stray '-': {good}")


def sql_examples():
    t = note("4-2-SQL-Recap.md")
    bl = blocks(t)
    tables = {}
    for m in re.finditer(r"^#{4,6} `(\w+)`[^\n]*\n(.*?)(?=^#|\Z)", t, re.S | re.M):
        rows, header = md_table(m.group(2))
        tables[m.group(1)] = (header, rows)
    db = sqlite3.connect(":memory:")
    create = find("4-2-SQL-Recap.md", "CREATE TABLE Students", "sql")
    db.executescript(create)
    for r in tables["Students"][1]:
        db.execute("INSERT INTO Students VALUES (?,?,?)", r)
    for name in ("Books", "BorrowedBooks"):
        header, rows = tables[name]
        db.execute(f"CREATE TABLE {name} ({', '.join(header)})")
        db.executemany(f"INSERT INTO {name} VALUES ({','.join('?' * len(header))})", rows)
    problems, compared, ran = [], 0, 0
    for i, (lang, code, s, e) in enumerate(bl):
        if lang != "sql" or "CREATE TABLE" in code:
            continue
        ran += 1
        stmts = [x for x in re.split(r";\s*(?:\n|$)", re.sub(r"--[^\n]*", "", code)) if x.strip()]
        res = None
        for st in stmts:
            cur = db.execute(st)
            if cur.description:
                res = cur.fetchall()
        # the output block is the next block, or the block after an interposed 'sql' block that is only a variant
        nxt = bl[i + 1] if i + 1 < len(bl) else None
        if res is not None and nxt and nxt[0] in ("txt", "text"):
            got = [" ".join(map(str, r)).split() for r in res]
            want = [l.split() for l in nxt[1].strip().splitlines()]
            ordered = "ORDER BY" in code.upper()
            ok = got == want if ordered else sorted(got) == sorted(want)
            compared += 1
            if not ok:
                problems.append(f"query #{ran}: note shows {want}, SQLite returns {got}")
    good = has(t, r"WHERE dept IN \('CS', 'EE'\)") and not has(t, r"category IN") and not has(t, r"GROUP BY student_id;\s*\nORDER BY")
    return not problems and compared >= 6 and good, (
        f"{ran} queries run on SQLite (tables built from the note's own markdown tables), {compared} outputs compared with the note's; problems: {problems or 'none'}; "
        f"the old `GROUP BY ...; ORDER BY name` (a syntax error: ; ends the query and BorrowedBooks has no name column) and `category IN` are gone: {good}")


def er_wording():
    t = note("4-2-SQL-Recap.md")
    bad = has(t, r"Mandatory \(At least one\)") or has(t, r"Optional \(Zero or more participate\)")
    good = has(t, r"Circle `O` → \*\*Zero\*\*") and has(t, r"`\|O` zero or one") and has(t, r"`\|<` \(bar \+ crow's foot\) one or many")
    return good and not bad, f"crow's-foot notation: bar = one, circle = ZERO (not 'zero or more'), `||` = exactly one (not 'at least one'), combinations listed: {good}; old wording present: {bad}"


# --------------------------------------------------------------------------- #
# 4-3 flask basics
# --------------------------------------------------------------------------- #
def basics_apps():
    F = "4-3-flask-basics.md"
    out = []
    ns, c = build(find(F, "Hello, Flask!"))
    out.append(c.get("/").get_data(as_text=True) == "Hello, Flask!")
    ns, c = build(find(F, "Student not found"))
    out += [c.get("/").get_data(as_text=True) == "Welcome to the Student Portal!", c.get("/student/1").get_data(as_text=True) == "Student ID: 1, Name: Alice",
            c.get("/student/9").get_data(as_text=True) == "Student ID: 9, Name: Student not found", c.get("/student/abc").status_code == 404]
    ns, c = build(find(F, "fruits = ["))
    r = c.get("/fruits/")
    out += [r.get_json() == ["Apple", "Banana", "Cherry"], r.content_type == "application/json"]
    t = note(F)
    return all(out) and has(t, r"before 2\.2"), f"the note's own 'Hello', 'student portal' and 'fruits' apps behave as described ({out}); list -> JSON content type application/json (Flask 2.2+, note says 'before 2.2' for jsonify)"


def converters():
    F = "4-3-flask-basics.md"
    ns, c = build(find(F, "show_user_profile") + "\n" + find(F, "show_post") + "\n"
                  "@app.route('/product/<float:price>')\ndef prod(price): return str(price)\n"
                  "@app.route('/sub/<path:subpath>')\ndef sub(subpath): return subpath\n"
                  "@app.route('/task/<uuid:task_id>')\ndef task(task_id): return str(task_id)\n", prelude=PRELUDE)
    g = lambda p: c.get(p)
    ok = (g("/user/john").get_data(as_text=True) == "User: john" and g("/user/john/doe").status_code == 404
          and g("/post/123").get_data(as_text=True) == "Post ID: 123" and g("/post/abc").status_code == 404
          and g("/product/19.99").status_code == 200 and g("/product/19").status_code == 404 and g("/product/abc").status_code == 404
          and g("/sub/john/profile").get_data(as_text=True) == "john/profile"
          and g("/task/123e4567-e89b-12d3-a456-426614174000").status_code == 200 and g("/task/invalid").status_code == 404)
    return ok, "string rejects '/', int/float/uuid reject non-matching text with 404, float needs a decimal point (/product/19 is 404), path accepts '/'"


def overload_routes():
    F = "4-3-flask-basics.md"
    code = find(F, "get_item_by_id")
    with workdir():
        ns, c = build(code, prelude="from flask import Flask\napp = Flask(__name__)\n")
        res = {p: c.get(p).get_data(as_text=True) for p in ("/item/5", "/item/1.5", "/item/abc")}
        # definition order must not matter: put string first
        swapped = "\n".join(code.splitlines())
        first = re.search(r"@app\.route\('/item/<string:item_id>'\)", code)
        swapped = code.replace("@app.route('/item/<int:item_id>')\n@app.route('/item/<string:item_id>')", "@app.route('/item/<string:item_id>')\n@app.route('/item/<int:item_id>')")
        ns2, c2 = build(swapped, prelude="from flask import Flask\napp = Flask(__name__)\n")
        sw5 = c2.get("/item/5").get_data(as_text=True)
        Path("app.py").write_text("from flask import Flask\napp = Flask(__name__)\n" + code, encoding="utf-8")
        p = subprocess.run([PY, "-m", "flask", "--app", "app", "routes"], capture_output=True, text=True, timeout=60)
    real = {tuple(re.split(r"\s{2,}", l.strip())) for l in p.stdout.splitlines()[2:] if l.strip()}
    note_block = find(F, "Endpoint", "txt")
    shown = {tuple(re.split(r"\s{2,}", l.strip())) for l in note_block.splitlines()[2:] if l.strip()}
    t = note(F)
    good = has(t, r"more specific converters") and not has(t, r"in the order they are defined") and has(t, r"flask --app app routes")
    table = ("Item ID: 5 type of <class 'int'>" == res["/item/5"] and "Item ID: 1.5 type of <class 'float'>" == res["/item/1.5"] and "Item ID: abc type of <class 'str'>" == res["/item/abc"])
    return table and sw5 == res["/item/5"] and real == shown and len(real) == 4 and good, (
        f"/item/5 -> int, /item/1.5 -> float, /item/abc -> str ({table}); writing the string rule FIRST still gives {sw5!r} for /item/5, so definition order is not what decides; "
        f"`flask --app app routes` prints the same 4 rows as the note ({real == shown}): {sorted(real)}; note says 'more specific converters first', not 'order they are defined': {good}")


def slashes_and_plus():
    F = "4-3-flask-basics.md"
    ns, c = build(find(F, "@app.route('/about')\ndef about", nth=0) + "\n@app.route('/team/')\ndef team(): return 'team'\n"
                  "@app.route('/u/<username>')\ndef u(username): return username\n@app.route('/q')\ndef q(): return request.args.get('x')\n", prelude=PRELUDE)
    a = c.get("/about/").status_code
    r = c.get("/team")
    r3 = c.get("/team///")
    plus_path = c.get("/u/a+b").get_data(as_text=True)
    plus_q = c.get("/q?x=a+b").get_data(as_text=True)
    pct = c.get("/u/a%20b").get_data(as_text=True)
    t = note(F)
    good = (has(t, r"HTTP status 308") and has(t, r"merges repeated slashes") and has(t, r"`\?q=a\+b` gives `a b`") and has(t, r"`/user/a\+b` gives `a\+b`")
            and not has(t, r"Represents a space character in URL encoding"))
    return a == 404 and r.status_code == 308 and r.headers["Location"].endswith("/team/") and r3.status_code == 308 and plus_path == "a+b" and plus_q == "a b" and pct == "a b" and good, (
        f"'/about' route: '/about/' -> {a}; '/team/' route: '/team' -> {r.status_code} redirect to {r.headers['Location']}, '/team///' -> {r3.status_code}; "
        f"'+' is a space only in the QUERY ('?x=a+b' -> {plus_q!r}), in the path '/u/a+b' -> {plus_path!r}, %20 -> {pct!r}; note says 308, merging of slashes, and the + rule: {good}")


def response_types():
    ns, c = build("@app.route('/bad')\ndef bad(): return 5\n@app.route('/f')\ndef f(): return 1.5\n@app.route('/d')\ndef d(): return {'a': 1}\n", prelude=PRELUDE)
    t = note("4-3-flask-basics.md")
    good = has(t, r"raises a `TypeError`") and has(t, r"dict or list")
    return c.get("/bad").status_code == 500 and c.get("/f").status_code == 500 and c.get("/d").get_json() == {"a": 1} and good, (
        f"returning an int/float -> HTTP 500 (TypeError: 'The view function did not return a valid response'), a dict -> JSON; note says so: {good}")


# --------------------------------------------------------------------------- #
# 4-4 templating
# --------------------------------------------------------------------------- #
def template_files(fname):
    """{'templates/index.html': html} from '#### templates/NAME' headings followed by an html block."""
    t = note(fname)
    u = unquote(t)
    files = {}
    for m in re.finditer(r"^#{3,5} (templates/[\w./-]+)\s*\n+```html\n(.*?)^```", u, re.S | re.M):
        files[m.group(1)] = m.group(2)
    return files


def templating_examples():
    F = "4-4-flask-templating.md"
    files = template_files(F)
    app_blocks = [b[1] for b in blocks(note(F)) if b[0] == "python" and "render_template(" in b[1]]
    problems = []
    with workdir(files):
        ns, c = build(app_blocks[0])
        html = c.get("/").get_data(as_text=True)
        if not ("<title>Home Page</title>" in html and "<h1>Welcome to Flask!</h1>" in html and "<p>This is a simple Flask application using templates.</p>" in html):
            problems.append("index.html output")
    with workdir(files):
        ns, c = build(app_blocks[1])
        got = c.get("/").get_data(as_text=True)
        expected = find(F, "<h2>Welcome to My Website's Home Page!</h2>", "html")
        if loose(got) != loose(expected):
            problems.append(f"inheritance output differs: {loose(got)[:3]} vs {loose(expected)[:3]}")
    ts = find(F, "render_template_string(template")
    with workdir():
        ns, c = build(ts)
        html = c.get("/").get_data(as_text=True)
        if "<h1>Welcome to Flask!</h1>" not in html:
            problems.append("template string output")
    return not problems and len(files) >= 3, f"{len(files)} template files + 3 apps taken from the note render exactly what the note says; problems: {problems or 'none'}"


def static_and_folders():
    F = "4-4-flask-templating.md"
    with workdir({"my_templates/index.html": "<p>{{ x }}</p>", "static/styles.css": "p{}", "my_static/s.css": "p{}"}):
        a1 = build("from flask import Flask, render_template\napp = Flask(__name__, template_folder='my_templates')\n@app.route('/')\ndef i(): return render_template('index.html', x='hi')\n")[1]
        a2 = build("from flask import Flask\napp = Flask(__name__)\n")[1]
        a3 = build("from flask import Flask\napp = Flask(__name__, static_folder='my_static')\n")[1]
        a4 = build("from flask import Flask\napp = Flask(__name__, static_folder='my_static', static_url_path='/static')\n")[1]
        r = (a1.get("/").get_data(as_text=True), a2.get("/static/styles.css").status_code, a3.get("/my_static/s.css").status_code, a3.get("/static/s.css").status_code, a4.get("/static/s.css").status_code)
        ns, c = build("from flask import Flask, url_for\napp = Flask(__name__)\n")
        with ns["app"].test_request_context():
            u = ns["url_for"]("static", filename="styles.css")
    t = note(F)
    good = has(t, r"served under `/my_static/\.\.\.`") and has(t, r"static_url_path='/static'") and has(t, r"DictLoader") and not has(t, r"because of Environment setup constraints")
    return r == ("<p>hi</p>", 200, 200, 404, 200) and u == "/static/styles.css" and good, (
        f"template_folder='my_templates' works ({r[0]!r}); /static/styles.css is served (200); with static_folder='my_static' the URL becomes /my_static/... (200) and /static/... is 404; static_url_path='/static' restores it ({r[4]}); "
        f"url_for('static', filename='styles.css') = {u!r}; note says all this and no longer cites 'Environment setup constraints': {good}")


def template_string_safety():
    ns, c = build("from flask import Flask, render_template_string\napp = Flask(__name__)\n@app.route('/')\ndef i(): return render_template_string('<p>{{ x }}</p>', x='<b>')\n")
    t = note("4-4-flask-templating.md")
    good = has(t, r"render_template_string\(user_text\)") and has(t, r"autoescaping-html-safety")
    return c.get("/").get_data(as_text=True) == "<p>&lt;b&gt;</p>" and good, f"render_template_string escapes values ({c.get('/').get_data(as_text=True)!r}); note warns never to pass user text as the template and links the Jinja2 safety section: {good}"


# --------------------------------------------------------------------------- #
# 4-5 more features
# --------------------------------------------------------------------------- #
def url_for_examples():
    F = "4-5-more-flask-features.md"
    ns, c = build(find(F, "def links"))
    links = c.get("/links").get_data(as_text=True)
    ns2, c2 = build(find(F, "@app.route('/user/<username>')") + "\n" + "@app.route('/')\ndef home(): return 'h'\n", prelude=PRELUDE)
    ul = c2.get("/user_links").get_data(as_text=True)
    ns3, c3 = build(find(F, "static_example"))
    st = c3.get("/static_example").get_data(as_text=True)
    ok = ('href="/"' in links and 'href="/about"' in links and 'href="/contact"' in links and 'href="/user/alice"' in ul and 'href="/user/bob?age=23"' in ul
          and 'src="/static/images/logo.png"' in st and 'href="/static/styles/main.css"' in st and c2.get("/user/bob").get_data(as_text=True) == "Profile page of bob")
    return ok, f"the note's links / user_links / static_example views produce /, /about, /contact, /user/alice, /user/bob?age=23 (extra args become a query string), /static/images/logo.png: {ok}"


def url_for_contexts():
    from flask import Flask, url_for
    app = Flask(__name__)

    @app.route("/about")
    def about():
        return "x"

    def attempt(fn):
        try:
            return fn()
        except RuntimeError as e:
            return "RuntimeError"

    none = attempt(lambda: url_for("about"))

    def app_ctx():
        with app.app_context():
            return url_for("about")

    def req_ctx():
        with app.test_request_context():
            return url_for("about")

    def server_name():
        app.config["SERVER_NAME"] = "example.com"
        try:
            with app.app_context():
                return url_for("about")
        finally:
            app.config["SERVER_NAME"] = None

    r = (none, attempt(app_ctx), req_ctx(), server_name())
    t = note("4-5-more-flask-features.md")
    good = has(t, r"test_request_context") and has(t, r"SERVER_NAME") and has(t, r"is \*\*not\*\* enough") and not has(t, r"or use the `app\.app_context\(\)` context manager when needed")
    return r == ("RuntimeError", "RuntimeError", "/about", "http://example.com/about") and good, (
        f"url_for with no context -> {r[0]}; inside only `app.app_context()` -> {r[1]} (the old advice does NOT work); inside `app.test_request_context()` -> {r[2]!r}; "
        f"app_context + SERVER_NAME -> {r[3]!r}; note gives the working advice: {good}")


def url_map_and_cli():
    F = "4-5-more-flask-features.md"
    code = find(F, "print(app.url_map)")
    with workdir():
        ns, c = build(code)
        real = str(ns["app"].url_map)
        Path("app.py").write_text(code, encoding="utf-8")
        p = subprocess.run([PY, "-m", "flask", "--app", "app", "routes"], capture_output=True, text=True, timeout=60)
    parse = lambda s: {(m.group(1), frozenset(x.strip() for x in m.group(2).split(",")), m.group(3)) for m in re.finditer(r"<Rule '([^']+)' \(([^)]*)\) -> (\w+)>", s)}
    shown = parse(find(F, "<Rule '/'", "text"))
    cli = {tuple(re.split(r"\s{2,}", l.strip())) for l in p.stdout.splitlines()[2:] if l.strip()}
    t = note(F)
    good = has(t, r"order of the methods inside the brackets can differ") and has(t, r"flask --app app routes")
    return parse(real) == shown and len(shown) == 4 and ("static", "GET", "/static/<path:filename>") in cli and good, (
        f"str(app.url_map) has the same 4 rules and methods as the note (static rule included, method order varies); `flask --app app routes` lists them with only GET (HEAD/OPTIONS are automatic): {sorted(cli)}; note says so: {good}")


def redirect_and_abort():
    F = "4-5-more-flask-features.md"
    ns, c = build(find(F, "old_page"))
    r = c.get("/old-page")
    r301 = ns["redirect"]("/x", code=301).status_code
    followed = c.get("/old-page", follow_redirects=True).get_data(as_text=True)
    ns2, c2 = build(find(F, "def get_resource", nth=0))
    a = (c2.get("/resource/1").get_data(as_text=True), c2.get("/resource/2").status_code, c2.get("/admin/user_list").status_code)
    files = {"templates/404.html": "<h1>Custom 404</h1>", "templates/403.html": "<h1>Custom 403</h1>"}
    with workdir(files):
        ns3, c3 = build(find(F, "@app.errorhandler(404)"))
        h = (c3.get("/resource/2").status_code, c3.get("/resource/2").get_data(as_text=True), c3.get("/admin/user_list").status_code, c3.get("/admin/user_list").get_data(as_text=True))
    from werkzeug.exceptions import abort, default_exceptions
    try:
        abort(407)
        e407 = "no error"
    except LookupError:
        e407 = "LookupError"
    ns4, c4 = build("@app.route('/custom-error')\ndef custom_error():\n    return 'Custom Error Occurred', 407\n", prelude=PRELUDE)
    t = note(F)
    good = has(t, r"about 30, not every code") and has(t, r"the underlying \*\*Werkzeug\*\* library") and not has(t, r"defined by underlying \*\*Werkzeug\*\* server")
    return (r.status_code == 302 and r301 == 301 and followed == "This is the New Page!" and a == ("Resource 1 found!", 404, 403) and h == (404, "<h1>Custom 404</h1>", 403, "<h1>Custom 403</h1>")
            and e407 == "LookupError" and 25 <= len(default_exceptions) <= 40 and c4.get("/custom-error").status_code == 407 and good), (
        f"redirect() answers {r.status_code} (301 with code=301) and the browser lands on the new page; abort(404/403) work ({a}); the note's errorhandler example NOW runs and renders the custom pages ({h[0]}, {h[2]}) "
        f"(the old one used abort/user that were never defined); abort(407) -> {e407} (Werkzeug has {len(default_exceptions)} exception classes); returning ('...', 407) works; note: {good}")


def session_cookie():
    import base64
    ns, c = build("app.secret_key = 'k'\n@app.route('/s')\ndef s():\n    from flask import session\n    session['user'] = 'alice'\n    return 'ok'\n", prelude=PRELUDE)
    cookie = c.get("/s").headers["Set-Cookie"]
    payload = cookie.split("session=")[1].split(";")[0].split(".")[0]
    raw = base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4))
    t = note("4-5-more-flask-features.md")
    good = has(t, r"\*\*signed\*\*") and has(t, r"not encrypted")
    return raw == b'{"user":"alice"}' and good, f"the session cookie payload is just base64 JSON {raw!r}: signed (tamper-proof) but readable; note says 'signed ... not encrypted' instead of 'secure cookies': {good}"


# --------------------------------------------------------------------------- #
# 4-7 request
# --------------------------------------------------------------------------- #
def request_examples():
    F = "4-7-request.md"
    p = []
    ns, c = build(find(F, "def example()"))
    if (c.get("/example").get_data(as_text=True), c.post("/example").get_data(as_text=True)) != ("This is a GET request", "This is a POST request"):
        p.append("request.method")
    ns, c = build(find(F, "def search()"))
    if c.get("/search?q=flask").get_data(as_text=True) != "Search results for: flask":
        p.append("request.args")
    ns, c = build(find(F, "def user_profile"))
    if c.get("/user/john").get_data(as_text=True) != "User Profile for: john":
        p.append("view_args")
    ns, c = build(find(F, "def submit()"))
    if c.post("/submit", data={"name": "A", "email": "a@b.c"}).get_data(as_text=True) != "Submitted Name: A, Email: a@b.c":
        p.append("request.form")
    ns, c = build(find(F, "def multi()"))
    shown = find(F, "'fruits': ['apple', 'cherry']", "bash").strip()
    posted = c.post("/multi", data={"username": "john_doe", "fruits": ["apple", "cherry"]}).get_data(as_text=True)
    if posted != shown or c.get("/multi").status_code != 200:
        p.append(f"multi: {posted!r} vs {shown!r}")
    ns, c = build(find(F, "def headers()"))
    if c.get("/headers", headers={"User-Agent": "UA/1"}).get_data(as_text=True) != "User-Agent: UA/1":
        p.append("headers")
    ns, c = build(find(F, "def json_example"))
    j = (c.post("/json", json={"name": "Al", "age": 3}).get_data(as_text=True), c.post("/json", data="{bad", content_type="application/json").get_data(as_text=True),
         c.post("/json", data='{"name":"x"}', content_type="text/plain").get_data(as_text=True))
    if j != ("Name: Al, Age: 3", "Name: None, Age: None", "Name: None, Age: None"):
        p.append(f"json_example {j}")
    return not p, f"all 7 request examples of the note (method, args, view_args, form, MultiDict/getlist output block, headers, get_json with silent=True) behave and print what the note says; problems: {p or 'none'}"


def get_json_and_data():
    ns, c = build("@app.route('/j', methods=['POST'])\ndef j(): return jsonify(v=request.get_json())\n"
                  "@app.route('/e', methods=['POST'])\ndef e(): return jsonify(data=request.data.decode(), form=request.form.to_dict(flat=False))\n", prelude=PRELUDE)
    wrong_ct, malformed, lst = c.post("/j", data='{"a":1}', content_type="text/plain").status_code, c.post("/j", data="{bad", content_type="application/json").status_code, c.post("/j", json=[1, 2]).get_json()
    form = c.post("/e", data={"a": "1"}).get_json()
    raw = c.post("/e", data="hello", content_type="text/plain").get_json()
    t = note("4-7-request.md")
    good = (has(t, r"415 Unsupported Media Type") and has(t, r"400 Bad Request") and has(t, r"empty for form submissions") and not has(t, r"returns it as a Python dictionary\.")
            and has(t, r"a JSON list gives a list"))
    return (wrong_ct == 415 and malformed == 400 and lst == {"v": [1, 2]} and form == {"data": "", "form": {"a": ["1"]}} and raw["data"] == "hello" and good), (
        f"get_json(): wrong Content-Type -> {wrong_ct}, malformed JSON -> {malformed}, a JSON list comes back as a list ({lst}); request.data is EMPTY for a form post ({form['data']!r}) and holds the body for text/plain ({raw['data']!r}); note says so: {good}")


def file_upload_examples():
    p = []
    F7, F6 = "4-7-request.md", "4-6-html-forms.md"
    index7 = find(F7, 'name="profile_picture"', "html")
    for fname, code in ((F7, find(F7, "def home():", nth=0)), (F7, find(F7, "def home():", nth=1)), (F6, find(F6, "request.files"))):
        with workdir({"templates/index.html": index7}):
            ns, c = build(code)
            g = c.get("/")
            r = c.post("/", data={"username": "u", "profile_picture": (__import__("io").BytesIO(b"abc"), "../../evil name.txt"), "fruits": "apple"}, content_type="multipart/form-data")
            empty = c.post("/", data={"username": "u", "profile_picture": (__import__("io").BytesIO(b""), "")}, content_type="multipart/form-data")
            saved = sorted(os.listdir("uploads")) if os.path.isdir("uploads") else []
        if g.status_code != 200 or r.status_code != 200 or saved != ["evil_name.txt"] or empty.status_code != 200 or "'username': ['u']" not in r.get_data(as_text=True):
            p.append(f"{fname}: GET {g.status_code}, POST {r.status_code}, empty file {empty.status_code}, saved {saved}")
    t = note(F7)
    good = has(t, r"from flask import Flask, render_template, request") and has(t, r"if file\.filename")
    return not p and good, (f"the 3 upload examples: GET renders the form (the old request.files example forgot to import render_template -> NameError), a multipart POST saves '../../evil name.txt' as 'evil_name.txt' "
                            f"(secure_filename), an empty file field no longer crashes; problems: {p or 'none'}; note imports render_template and guards empty names: {good}")


# --------------------------------------------------------------------------- #
# 4-6 html forms in a real browser
# --------------------------------------------------------------------------- #
FORMS_JS = r"""
const { chromium } = require('playwright');
const fs = require('fs'); const path = require('path');
(async () => {
  const dir = process.argv[2];
  const b = await chromium.launch(); const ctx = await b.newContext(); const page = await ctx.newPage();
  let cur = '', last = null;
  await ctx.route('http://t.test/**', route => {
    const r = route.request();
    if (r.url().endsWith('/page')) return route.fulfill({ contentType: 'text/html', body: cur });
    last = { method: r.method(), url: r.url(), ct: r.headers()['content-type'] || '', body: (r.postData() || '').slice(0, 4000) };
    return route.fulfill({ contentType: 'text/html', body: 'done' });
  });
  const run = async (html, act) => { cur = `<!DOCTYPE html><html lang=en><head><meta charset=utf-8><title>t</title></head><body>${html}</body></html>`; last = null; await page.goto('http://t.test/page'); if (act) await act(); await page.waitForTimeout(120); return last; };
  const go = () => page.click('button');
  const R = {};
  R.simple = await run('<form action="/submit" method="post"><input type="text" id="name1" name="name" required><input type="email" id="email1" name="email" required><button type="submit">Submit</button></form>',
    async () => { await page.fill('#name1', 'John Doe'); await page.fill('#email1', 'john.doe@example.com'); await go(); });
  R.noname = await run('<form action="/submit" method="post"><input name="a" value="1"><input value="2" id="x"><button>Go</button></form>', go);
  R.checks = await run('<form action="/submit" method="post"><input type="checkbox" name="fruit" value="Mango" checked><input type="checkbox" name="fruit" value="Apple"><input type="checkbox" name="fruit" value="Banana" checked><input type="radio" name="g" value="M"><input type="radio" name="g" value="F" checked><button>Go</button></form>', go);
  R.attrs = await run('<form action="/submit" method="post"><input name="dis" value="d" disabled><input name="ro" value="r" readonly><input name="hid" value="h" hidden><input type="hidden" name="hid2" value="h2"><button>Go</button></form>', go);
  R.selblank = await run('<form action="/submit" method="post"><select name="cars"><option value="" disabled selected>Select a car</option><option value="volvo">Volvo</option></select><button>Go</button></form>', go);
  R.selreq = await run('<form action="/submit" method="post"><select name="cars" required><option value="" disabled selected>Select a car</option><option value="volvo">Volvo</option></select><button>Go</button></form>', go);
  R.selmulti = await run('<form action="/submit" method="post"><select name="cars" multiple><option value="volvo">Volvo</option><option value="saab">Saab</option><option value="fiat">Fiat</option></select><button>Go</button></form>', async () => { await page.selectOption('select', ['volvo', 'fiat']); await go(); });
  fs.writeFileSync(path.join(dir, 'note.txt'), 'hello');
  R.file_plain = await run('<form action="/submit" method="post"><input type="file" name="f"><button>Go</button></form>', async () => { await page.setInputFiles('input', path.join(dir, 'note.txt')); await go(); });
  R.file_multi = await run('<form action="/submit" method="post" enctype="multipart/form-data"><input type="file" name="f"><button>Go</button></form>', async () => { await page.setInputFiles('input', path.join(dir, 'note.txt')); await go(); });
  R.method_put = await run('<form action="/submit" method="put"><input name="a" value="1"><button>Go</button></form>', go);
  R.btn_default = await run('<form action="/submit" method="post"><input name="a" value="1"><button>Go</button></form>', go);
  R.btn_button = await run('<form action="/submit" method="post"><input name="a" value="1"><button type="button">Go</button></form>', go);
  R.dt = await run('<form action="/submit" method="post"><input type="datetime-local" name="appointment" id="d"><button>Go</button></form>', async () => { await page.fill('#d', '2024-06-01T14:30'); await go(); });
  R.textarea = await run('<form action="/submit" method="post"><textarea name="m">line1\nline2</textarea><button>Go</button></form>', go);
  await run('<form><input type="email" id="e"></form>', async () => { await page.fill('#e', 'not-an-email'); });
  R.email = await page.evaluate(() => { const e = document.getElementById('e'); const bad = e.checkValidity(); e.value = 'a@b.co'; return [bad, e.checkValidity()]; });
  await run('<form><input type="file" id="f" accept="image/*"></form>', async () => { await page.setInputFiles('#f', path.join(dir, 'note.txt')); });
  R.accept = await page.evaluate(() => document.getElementById('f').files.length);
  await run('<form><input type="checkbox" id="k" readonly></form>', async () => { await page.click('#k'); });
  R.readonly_checkbox = await page.evaluate(() => document.getElementById('k').checked);
  // the note's complete example form, filled and submitted
  if (fs.existsSync(path.join(dir, 'complete.html'))) {
    cur = fs.readFileSync(path.join(dir, 'complete.html'), 'utf8'); last = null;
    await page.goto('http://t.test/page');
    await page.fill('#username_id', 'alice'); await page.fill('#user_email_id', 'a@b.co'); await page.fill('#user_password_id', 'pw');
    await page.check('#female_id'); await page.check('#apple_id'); await page.check('#banana_id'); await page.selectOption('#cars_id', 'saab');
    await page.fill('#message_id', 'hi'); await page.setInputFiles('#file_upload_id', path.join(dir, 'note.txt'));
    await page.click('button[type=submit]'); await page.waitForTimeout(150);
    R.complete = last;
  }
  console.log(JSON.stringify(R)); await b.close();
})();
"""


def run_forms_browser():
    node = shutil.which("node")
    if not node:
        return None
    with tempfile.TemporaryDirectory() as d:
        Path(d, "forms.js").write_text(FORMS_JS)
        complete = [b[1] for b in blocks(note("4-6-html-forms.md")) if b[0] == "html" and 'id="user_info_section"' in b[1]]
        if complete:
            Path(d, "complete.html").write_text(complete[0])
        env = dict(os.environ, NODE_PATH=subprocess.run(["npm", "root", "-g"], capture_output=True, text=True).stdout.strip())
        p = subprocess.run([node, str(Path(d, "forms.js")), d], capture_output=True, text=True, env=env, timeout=240)
        if p.returncode:
            raise RuntimeError(p.stderr.strip().splitlines()[-1][:200])
        return json.loads(p.stdout.strip().splitlines()[-1])


def forms_facts(B):
    F = "4-6-html-forms.md"
    t = note(F)
    ok = (B["simple"]["body"] == "name=John+Doe&email=john.doe%40example.com" and B["simple"]["method"] == "POST" and B["noname"]["body"] == "a=1"
          and B["checks"]["body"] == "fruit=Mango&fruit=Banana&g=F" and B["attrs"]["body"] == "ro=r&hid=h&hid2=h2" and B["selblank"]["body"] == "" and B["selreq"] is None
          and B["selmulti"]["body"] == "cars=volvo&cars=fiat" and B["file_plain"]["body"] == "f=note.txt" and B["file_multi"]["ct"].startswith("multipart/form-data")
          and 'filename="note.txt"' in B["file_multi"]["body"] and B["method_put"]["method"] == "GET" and B["btn_default"]["method"] == "POST" and B["btn_button"] is None
          and B["dt"]["body"] == "appointment=2024-06-01T14%3A30" and "line1%0D%0Aline2" in B["textarea"]["body"] and B["email"] == [False, True]
          and B["accept"] == 1 and B["readonly_checkbox"] is True)
    good = (has(t, r"A field without a `name` is not submitted") and has(t, r"an unchecked checkbox sends nothing at all") and has(t, r"a read-only field \*\*is\*\* submitted")
            and has(t, r"nothing is sent for `cars`") and has(t, r"add the `required` attribute to the `<select>`") and has(t, r"only the file \*\*name\*\*") and has(t, r"hint for the browser's file chooser")
            and has(t, r"A form with `method=\"put\"` is sent as a `GET` request") and has(t, r"`readonly` has no effect on checkboxes") and has(t, r"\\r\\n") and has(t, r"HTTPS")
            and not has(t, r"which is not visible in the URL\. It is more secure for sensitive data") and not has(t, r"should have `name` and `value` attributes"))
    return ok and good, (
        f"Chromium sent: {B['simple']['body']!r}; field without name omitted ({B['noname']['body']!r}); unchecked checkbox/radio omitted ({B['checks']['body']!r}); disabled omitted, readonly + hidden sent ({B['attrs']['body']!r}); "
        f"`disabled selected` placeholder sends nothing ({B['selblank']['body']!r}) and with `required` the browser blocks the submit ({B['selreq']}); multiple select ({B['selmulti']['body']!r}); file without multipart sends only the name ({B['file_plain']['body']!r}); "
        f"method=put became {B['method_put']['method']}; <button> defaults to submit, type=button does not; datetime-local {B['dt']['body']!r}; textarea newline is %0D%0A; email check {B['email']}; accept is only a hint (files={B['accept']}); "
        f"readonly does not stop a checkbox ({B['readonly_checkbox']}); note says all of this and no longer calls POST 'more secure': {good}")


def complete_form_matches_route(B):
    F = "4-6-html-forms.md"
    form = [b[1] for b in blocks(note(F)) if b[0] == "html" and 'id="user_info_section"' in b[1]][0]
    action = re.search(r'<form[^>]*action="([^"]+)"', form).group(1)
    code = find(F, "request.files")
    with workdir({"templates/index.html": form}):
        ns, c = build(code)
        routes = {r.rule for r in ns["app"].url_map.iter_rules()}
        r = c.post(action, data={"username": "alice", "user_email": "a@b.co", "gender": "Female", "fruit": ["Apple", "Banana"], "cars": "saab", "message": "hi",
                                 "file_upload": (__import__("io").BytesIO(b"x"), "n.txt")}, content_type="multipart/form-data")
        saved = os.listdir("uploads") if os.path.isdir("uploads") else []
    c_req = B["complete"]
    dup = len(re.findall(r"</label>\s*<input[^>]*>\s*(Female|Apple|Banana)\s*$", form, re.M))
    ok = action in routes and r.status_code == 200 and saved == ["n.txt"] and "'fruit': ['Apple', 'Banana']" in r.get_data(as_text=True) and dup == 0 and "</body>" in form
    browser = c_req and c_req["url"].endswith(action) and 'name="fruit"' in c_req["body"] and "Apple" in c_req["body"] and 'filename="note.txt"' in c_req["body"]
    return ok and bool(browser), (
        f"the form's action {action!r} is a route of the note's Flask app ({action in routes}; the old form posted to /submit, which the app did not have -> 404); a POST to it returns the form data and saves the upload ({saved}); "
        f"Chromium submits the filled form as multipart to {c_req['url'] if c_req else None}; no duplicated labels ({dup}) and the document has </body>: {'</body>' in form}")


# --------------------------------------------------------------------------- #
# HTML validity (optional)
# --------------------------------------------------------------------------- #
def nu_validate():
    jar, java = os.environ.get("VNU_JAR"), shutil.which("java")
    if not (jar and Path(jar).exists() and java):
        SKIPPED.append("Nu HTML validator skipped (set VNU_JAR=.../vnu.jar, needs java; `npm install vnu-jar`)")
        return None
    tpl = '<!DOCTYPE html>\n<html lang="en">\n<head><meta charset="utf-8"><title>t</title></head>\n<body>\n%s\n</body>\n</html>\n'
    with tempfile.TemporaryDirectory() as d:
        index, n = {}, 0
        for f in md_files():
            t = f.read_text(encoding="utf-8")
            for lang, body, s, e in blocks(t):
                if lang != "html" or re.search(r"\{%|\{\{", body) or body.lstrip().startswith("<option"):
                    continue                                  # template tags / a lone <option> (shown on its own on purpose)
                full = re.match(r"\s*<!DOCTYPE", body, re.I) is not None
                if not full and re.search(r"<html|<head|<body", body):
                    continue
                n += 1
                name = f"{f.name[:5]}_{n}.html"
                Path(d, name).write_text(body if full else tpl % body, encoding="utf-8")
                index[name] = (f.name, unquote(t)[:s].count("\n") + 2)
        p = subprocess.run([java, "-jar", jar, "--format", "json", "--skip-non-html", *sorted(Path(d).glob("*.html"))], capture_output=True, text=True)
        msgs = json.loads(p.stderr[p.stderr.index("{"):])["messages"]
    errors = [f"{index[m['url'].split('/')[-1]][0]}:{index[m['url'].split('/')[-1]][1]} {m['message'][:80]}" for m in msgs if m["type"] == "error"]
    return not errors, f"{len(index)} ```html snippets (without template tags) validated against the HTML standard; errors: {errors or 'none'}"


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
                if "[" in m.group(2) or m.group(2).startswith(" ") or (m.group(2) == "" and False):
                    bad.append(f"{f.name}:{i} {line!r}")
            else:
                open_ = False
                if m.group(2).strip():
                    bad.append(f"{f.name}:{i} closing fence {line!r}")
        if open_:
            bad.append(f"{f.name}: unclosed fence")
    return not bad, f"labelled / badly closed / unclosed fences: {bad or 'none'}"


def tree_diagrams():
    bad = [f.name for f in md_files() if re.search(r"│├|││|^\|-[A-Za-z]", f.read_text(encoding="utf-8"), re.M)]
    return not bad, f"folder trees with broken box-drawing characters (│├──, |-): {bad or 'none'}"


# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    M, R, B3, B4, B5, B6, B7 = ("4-1-database-layer-MODEL.md", "4-2-SQL-Recap.md", "4-3-flask-basics.md", "4-4-flask-templating.md",
                                "4-5-more-flask-features.md", "4-6-html-forms.md", "4-7-request.md")
    print("=" * 78 + "\nWeek 4 claim checker\n" + "=" * 78 + "\n")
    check(M, "SQLite: triggers yes, stored procedures no, atomic rollback; NoSQL/RDBMS table wording", sqlite_facts)
    check(R, "every SQL query of the recap runs and gives the output shown (tables built from the note's own markdown tables)", sql_examples)
    check(R, "crow's-foot ER notation described correctly", er_wording)
    if HAVE_FLASK:
        for c, claim, fn in ((B3, "the note's Hello / student-portal / fruits apps behave as described", basics_apps),
                             (B3, "path converters: string/int/float/path/uuid (float needs a decimal point)", converters),
                             (B3, "same function on 3 converter types: more specific converter first (not definition order); `flask routes` output", overload_routes),
                             (B3, "trailing slashes (404 / 308) and '+' (space only in the query string)", slashes_and_plus),
                             (B3, "valid return types: int/float -> 500, dict/list -> JSON", response_types),
                             (B4, "the note's templates + 3 apps render exactly what the note shows (index, inheritance, template string)", templating_examples),
                             (B4, "template_folder / static folder / static_folder changes the URL / static_url_path", static_and_folders),
                             (B4, "render_template_string escapes values; never pass user text as the template", template_string_safety),
                             (B5, "url_for examples (/links, /user_links, static files)", url_for_examples),
                             (B5, "url_for needs a request context (an app_context alone is not enough)", url_for_contexts),
                             (B5, "app.url_map output and `flask routes`", url_map_and_cli),
                             (B5, "redirect 302/301, abort, custom error handlers (runnable), abort(407) LookupError", redirect_and_abort),
                             (B5, "the session cookie is signed, not encrypted", session_cookie),
                             (B7, "all request.* examples of the note", request_examples),
                             (B7, "get_json(): 415 / 400 / silent=True; request.data is empty for forms", get_json_and_data),
                             (B7 + ", " + B6, "file upload examples run (render_template imported, secure_filename, empty file field)", file_upload_examples)):
            check(c, claim, fn)
    else:
        SKIPPED.append("all Flask checks skipped (pip install flask)")
    try:
        FB = run_forms_browser() if HAVE_FLASK else None
    except Exception as e:
        FB = None
        print(f"[browser] could not run: {e}\n")
    if FB is None:
        SKIPPED.append("browser form checks skipped (needs node + playwright)")
    else:
        check(B6, "form submission rules measured in Chromium (names, encoding, unchecked, disabled/readonly/hidden, select, file, method=put, buttons)", lambda: forms_facts(FB))
        check(B6, "the complete example form posts to a route the note's Flask app really has, and the upload works", lambda: complete_form_matches_route(FB))
    nu = nu_validate()
    if nu is not None:
        check("week4/*.md", "every plain ```html snippet is valid HTML (Nu validator)", lambda: nu)
    check("week4/*.md", "no VitePress-only syntax (:::, ==, ```lang[label], Vue components)", no_vitepress_syntax)
    check("week4/*.md", "no HTML that GitHub strips (style=, class=, &emsp;) outside code blocks", no_stripped_html)
    check("week4/*.md", "GitHub alerts written correctly", alerts_valid)
    check("week4/*.md", "<details> balanced, no backticks in <summary>", details_balanced)
    check("week4/*.md", "every local link, #anchor and image resolves", links_resolve)
    check("week4/*.md", "code fences are labelled/closed cleanly", fences_clean)
    check("week4/*.md", "folder trees use proper box-drawing characters", tree_diagrams)

    wrong = [f for ok, f in RESULTS if not ok]
    print("=" * 78)
    print(f"{len(RESULTS)} checks, {len(RESULTS) - len(wrong)} OK, {len(wrong)} WRONG")
    if wrong:
        print("files with WRONG statements:", ", ".join(sorted(set(wrong))))
    print("\nNOT VERIFIABLE HERE (kept because they are standard, but not executed):")
    for s in sorted(set(SKIPPED)) + [
        "crow's-foot ER notation (a drawing convention), MongoDB 4.0 multi-document transactions, which companies use NoSQL (Instagram, Netflix, ...), and the spreadsheet / NoSQL comparison table rows",
        "'a #fragment is not sent to the server' (browser behaviour not visible to the test client), and the macOS port-5000/AirPlay clash",
        "Windows commands (flask-env\\Scripts\\activate, set FLASK_APP) and the screenshots (static/4-*.png) of terminal / browser output",
        "docs links (flask / werkzeug / jinja palletsprojects.com, MDN) - blocked from this sandbox",
    ]:
        print("  -", s)
    sys.exit(1 if wrong else 0)
