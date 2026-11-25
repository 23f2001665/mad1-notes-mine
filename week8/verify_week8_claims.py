"""
Week 8 notes -- claim checker.

Every check takes statements, numbers or code from the week8 notes, runs them for real and reports
whether the notes are right:

    OK     -> the notes say what actually happens
    WRONG  -> the notes say something that does not happen (the evidence shows what does)

What is executed:

    8-frontend.md .............. the SSR / CSR Flask app of the note (curl vs a real Chromium), the machine-client POST,
                                 HTTP caching (ETag / 304), lazy loading, minify + gzip
    8-wsgi.md .................. the WSGI code of the note under wsgiref (+ wsgiref.validate), the environ table, the
                                 Flask app called as a WSGI callable, the middleware, Gunicorn
    8-javascript-basics.md ..... every ```js block is run in Node and every `console.log(...) // expected` comment is
                                 compared with what is printed; typeof / == / falsy tables; prompt / alert; where the
                                 <script> goes (head / end of body / defer / DOMContentLoaded) in Chromium
    8-basic-dom-manipulation.md  every snippet on the page of the note, in Chromium: selectors (live vs static),
                                 innerHTML / textContent / innerText, XSS via innerHTML, attributes, styles, add / remove,
                                 events, document.write, console, the complete example
    8-async-dom.md ............. fetch without await, async / await order, event-loop order, busy loop vs async wait,
                                 Web Worker, response.ok, the WebSocket server + client of the note, the 101 handshake,
                                 canvas, web storage, drag and drop
    8-client-validation.md ..... every validity state of the table in Chromium, the form, setCustomValidity,
                                 novalidate / formnovalidate, :invalid CSS, curl bypassing the form, the server-side check
    8-wasm-and-browser-security  the 41-byte WebAssembly module of the note (Node + Chromium), sandbox, same-origin / CORS,
                                 permissions, Subresource Integrity (good / tampered / absent), the rate limiter
    all files .................. GitHub-markdown hygiene, links and anchors, tables, mermaid (MERMAID_JS=...)

Run (from anywhere):
    pip install flask websockets gunicorn
    npm install -g playwright      (Chromium must be installed for playwright)
    npm install wabt               (optional; used for WAT -> bytes and the memory-trap checks)
    python week8/verify_week8_claims.py [-v]

Conventions of the notes that the checker relies on: a ```js block is meant to run unchanged in Node and its
`console.log(...)  // expected` comments are checked (a trailing "(explanation)" is ignored); a ```javascript block
needs a browser and is run in Chromium.  A check whose tool is missing is skipped and listed at the end.
Checked against CPython 3.13, Flask 3.1, Node 22 (V8 12.4), Chromium (Playwright), Gunicorn 27, websockets 17, curl 8.
"""
import hashlib
import json
import base64
import gzip
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import textwrap
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
NOTES = Path(os.environ.get("NOTES_DIR", HERE))
RESULTS, SKIPPED = [], []
VERBOSE = "-v" in sys.argv


def check(file, claim, fn):
    try:
        out = fn()
        if out is None:
            return
        ok, evidence = out
    except Exception as e:                         # a crash is a WRONG result, with the reason
        ok, evidence = False, f"raised {type(e).__name__}: {str(e).splitlines()[0][:300] if str(e) else ''}"
    RESULTS.append((ok, file))
    print(f"[{'OK   ' if ok else 'WRONG'}] {file}\n        claim   : {claim}\n        actual  : {evidence}\n")


def note(name):
    return (NOTES / name).read_text(encoding="utf-8")


def has(t, pattern):
    return re.search(pattern, t, re.S) is not None


def fenced(text, lang=None):
    out = []
    for m in re.finditer(r"^[ \t]*```(\w*)[^\n]*\n(.*?)^[ \t]*```[ \t]*$", text, re.S | re.M):
        if lang is None or m.group(1) == lang:
            out.append(textwrap.dedent(m.group(2)))
    return out


def block_with(text, *needles, lang="python"):
    for b in fenced(text, lang):
        if all(n in b for n in needles):
            return b
    raise LookupError(f"no ```{lang} block containing {needles} in the note")


def free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


def http(url, data=None, headers=None, method=None, timeout=10):
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, data=data, headers=headers or {}, method=method), timeout=timeout)
        return r.status, dict(r.headers), r.read()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read()


def serve(app, host="127.0.0.1"):
    from werkzeug.serving import make_server
    port = free_port()
    srv = make_server(host, port, app, threaded=True)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return port, srv


# ------------------------------------------------------------------------------------------------------------------ #
# tools
# ------------------------------------------------------------------------------------------------------------------ #
NODE = shutil.which("node")
NPM_ROOT = subprocess.run(["npm", "root", "-g"], capture_output=True, text=True).stdout.strip() if shutil.which("npm") else ""
NODE_ENV = dict(os.environ, NODE_PATH=NPM_ROOT)


def have_playwright():
    if not NODE:
        return False
    p = subprocess.run([NODE, "-e", "require('playwright')"], capture_output=True, text=True, env=NODE_ENV)
    return p.returncode == 0


def find_wabt():
    """a string usable as require(...) for the `wabt` npm package (WABT_DIR, next to the notes, cwd, or global), or None"""
    if not NODE:
        return None
    cands = [os.path.join(d, "node_modules", "wabt") for d in (os.environ.get("WABT_DIR"), str(HERE), os.getcwd()) if d] + ["wabt"]
    for c in cands:
        if subprocess.run([NODE, "-e", f"require({json.dumps(c)})"], capture_output=True, env=NODE_ENV).returncode == 0:
            return c
    return None


HAVE_PW = have_playwright()
WABT_DIR = find_wabt()


def node_run(code, *args, timeout=60):
    d = Path(tempfile.mkdtemp(prefix="w8n"))
    (d / "t.js").write_text(code)
    p = subprocess.run([NODE, "t.js", *map(str, args)], cwd=d, capture_output=True, text=True, env=NODE_ENV, timeout=timeout)
    return p


# ------------------------------------------------------------------------------------------------------------------ #
# the servers the browser tests talk to
# ------------------------------------------------------------------------------------------------------------------ #
STATE = {"hits": {"nocors": 0}}
SRI_JS = "window.sriLoaded = (window.sriLoaded||0) + 1;"


def lab_app():
    from flask import Flask, jsonify, request
    app = Flask("lab")

    @app.route("/blank")
    def blank():
        return "<!DOCTYPE html><html><body><h1>x</h1></body></html>"

    @app.route("/data")
    def data():
        time.sleep(0.3)
        return jsonify(items=["a", "b"]), 200, {"Access-Control-Allow-Origin": "*"}

    @app.route("/nocors")
    def nocors():
        STATE["hits"]["nocors"] += 1
        return jsonify(secret=1)

    @app.route("/missing")
    def missing():
        return jsonify(error="no such thing"), 404

    @app.route("/img<int:n>.gif")
    def img(n):
        return base64.b64decode("R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"), 200, {"Content-Type": "image/gif"}

    @app.route("/lib.js")
    def lib():
        return SRI_JS, 200, {"Content-Type": "application/javascript", "Access-Control-Allow-Origin": "*"}

    @app.route("/lib-tampered.js")
    def lib_t():
        return SRI_JS + " /* evil */", 200, {"Content-Type": "application/javascript", "Access-Control-Allow-Origin": "*"}

    @app.route("/script.js")
    def script():
        return 'document.getElementById("h").textContent = "changed";', 200, {"Content-Type": "application/javascript"}

    @app.route("/defer")
    def defer():
        return '<!DOCTYPE html><html><head><script src="/script.js" defer></script></head><body><h1 id="h">Hello</h1></body></html>'

    @app.route("/nodefer")
    def nodefer():
        return '<!DOCTYPE html><html><head><script src="/script.js"></script></head><body><h1 id="h">Hello</h1></body></html>'

    return app


def load_note_app(code, name="noteapp"):
    ns = {"__name__": name}
    exec(compile(code, name, "exec"), ns)
    return ns["app"]


# ------------------------------------------------------------------------------------------------------------------ #
# 8-frontend.md
# ------------------------------------------------------------------------------------------------------------------ #
F, W, J, D, A, V, S, IX = ("8-frontend.md", "8-wsgi.md", "8-javascript-basics.md", "8-basic-dom-manipulation.md",
                           "8-async-dom.md", "8-client-validation.md", "8-wasm-and-browser-security.md", "week8-index.md")


def ssr_csr_machine_client():
    t = note(F)
    app = load_note_app(block_with(t, "/csr"), "fe_note_app")
    from flask import jsonify, request

    @app.route("/sensor", methods=["POST"])
    def sensor():
        return jsonify(received=request.get_json(), type=request.content_type)

    port, srv = serve(app)
    base = f"http://127.0.0.1:{port}"
    ssr = http(base + "/ssr")[2].decode()
    csr = http(base + "/csr")[2].decode()
    s, _, b = http(base + "/sensor", json.dumps({"sensor": "t1", "celsius": 24.5}).encode(), {"Content-Type": "application/json"})
    sensor_json = json.loads(b)
    br = run_browser_suite().get("fe", {})
    srv.shutdown()
    note_json = re.search(r'`(\{"received".*?\}, "type": "[^"]+"\})`', t).group(1)
    ok = (
        "<li>apple</li>" in ssr and "apple" not in csr
        and sensor_json == json.loads(note_json)
        and br.get("ssr") == [["/ssr"], 3] and br.get("csr") == [["/csr", "/api/items"], ["apple", "banana", "cherry"]]
        and br.get("csrSource") is False and br.get("csrDom") is True
        and has(t, r"1 \(`/ssr`\) \| \*\*2\*\* \(`/csr`, then `/api/items`\)")
        and has(t, r"\| 3 \| 3 \(`apple`, `banana`, `cherry`\)")
        and "`curl /ssr`" in t
    )
    return ok, f"curl /ssr has <li>apple</li>: {'<li>apple</li>' in ssr}; curl /csr mentions apple: {'apple' in csr}; sensor POST -> {sensor_json}; browser: {br}"


def http_caching():
    from flask import Flask
    d = Path(tempfile.mkdtemp(prefix="w8s"))
    (d / "style.css").write_text("body { color: navy; }\n" * 50)
    app = Flask("cache", static_folder=str(d), static_url_path="/static")
    port, srv = serve(app)
    s1, h1, b1 = http(f"http://127.0.0.1:{port}/static/style.css")
    etag = h1.get("ETag")
    s2, h2, b2 = http(f"http://127.0.0.1:{port}/static/style.css", headers={"If-None-Match": etag})
    srv.shutdown()
    t = note(F)
    ok = (s1 == 200 and etag and h1.get("Last-Modified") and h1.get("Cache-Control") == "no-cache" and len(b1) > 0
          and s2 == 304 and b2 == b""
          and "`no-cache` does *not* mean \"do not store\"" in t and "# HTTP/1.1 304 NOT MODIFIED" in t and "# Cache-Control: no-cache" in t
          and 'curl -i -H \'If-None-Match: "1700000000.0-1000-123456789"\'' in t)
    return ok, f"first: {s1}, ETag {bool(etag)}, Last-Modified {bool(h1.get('Last-Modified'))}, Cache-Control {h1.get('Cache-Control')!r}, body {len(b1)} bytes; conditional request: {s2}, body {len(b2)} bytes"


def minify_and_lazy():
    css = ".card {\n    background-color: #ffffff;\n    border: 1px solid #dddddd;\n    padding: 16px;\n}\n/* title */\n.card h2 {\n    color: #333333;\n}\n" * 5
    mini = re.sub(r"\s*([{}:;,])\s*", r"\1", re.sub(r"\s+", " ", re.sub(r"/\*.*?\*/", "", css, flags=re.S)))
    gz = len(gzip.compress(mini.encode()))
    br = run_browser_suite().get("lazy", {})
    t = note(F)
    ok = (len(mini) < len(css) and gz < len(mini)
          and br.get("eager") == 3 and br.get("lazyBefore") < 3 and br.get("lazyAfter") == 3
          and "fetched all 3 immediately without the attribute" in t and 'loading="lazy"' in t)
    return ok, f"minified {len(css)} -> {len(mini)} bytes, gzip {gz}; Chromium: images requested eager={br.get('eager')}, lazy before scroll={br.get('lazyBefore')}, after scroll={br.get('lazyAfter')}"


# ------------------------------------------------------------------------------------------------------------------ #
# 8-wsgi.md
# ------------------------------------------------------------------------------------------------------------------ #
def wsgi_claims():
    from wsgiref.simple_server import make_server
    from wsgiref.validate import validator
    t = note(W)
    ns = {}
    exec(block_with(t, "def simple_app"), ns)
    simple_app = ns["simple_app"]
    out = {}

    def run(app):
        port = free_port()
        srv = make_server("127.0.0.1", port, app)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        return port, srv

    port, srv = run(validator(simple_app))
    s, h, b = http(f"http://127.0.0.1:{port}/")
    srv.shutdown()
    out["simple"] = (s, h.get("Content-Type"), b)

    seen = {}

    def spy(environ, start_response):
        for k in ("REQUEST_METHOD", "PATH_INFO", "QUERY_STRING", "SERVER_PROTOCOL", "CONTENT_TYPE", "CONTENT_LENGTH", "HTTP_X_DEMO", "wsgi.url_scheme"):
            seen[k] = environ.get(k)
        seen["body"] = environ["wsgi.input"].read(int(environ.get("CONTENT_LENGTH") or 0)).decode()
        start_response("200 OK", [("Content-Type", "text/plain")])
        return [b"ok"]
    port, srv = run(spy)
    http(f"http://127.0.0.1:{port}/a/b?x=1&y=2", b"name=Alice", {"X-Demo": "hello", "Content-Type": "application/x-www-form-urlencoded"}, "POST")
    srv.shutdown()
    environ_ok = (seen == {"REQUEST_METHOD": "POST", "PATH_INFO": "/a/b", "QUERY_STRING": "x=1&y=2", "SERVER_PROTOCOL": "HTTP/1.1",
                           "CONTENT_TYPE": "application/x-www-form-urlencoded", "CONTENT_LENGTH": "10", "HTTP_X_DEMO": "hello",
                           "wsgi.url_scheme": "http", "body": "name=Alice"}
                  and all(re.search(rf"\| `{re.escape(k)}`[^|]*\| [^|]*{re.escape(v)}", t) for k, v in
                          {"REQUEST_METHOD": "POST", "PATH_INFO": "/a/b", "QUERY_STRING": "x=1&y=2", "SERVER_PROTOCOL": "HTTP/1.1", "HTTP_X_DEMO": "hello", "wsgi.url_scheme": "http"}.items())
                  and "| `CONTENT_TYPE` / `CONTENT_LENGTH` | `application/x-www-form-urlencoded` / `10` |" in t)

    def bad_app(environ, start_response):
        start_response("200 OK", [("Content-Type", "text/plain")])
        return ["Hello as str"]
    import io, contextlib
    port, srv = run(validator(bad_app))
    with contextlib.redirect_stderr(io.StringIO()) as err:
        s, h, b = http(f"http://127.0.0.1:{port}/")
    srv.shutdown()
    str_ok = s == 500 and "Iterator yielded non-bytestring" in err.getvalue() and "Iterator yielded non-bytestring" in t and "answers `500`" in t

    from flask import Flask
    ns2 = {"__name__": "wsgi_note_app"}
    exec(block_with(t, "from flask import Flask", "def hi"), ns2)
    flask_app = ns2["app"]
    from wsgiref.util import setup_testing_defaults
    env = {}
    setup_testing_defaults(env)
    env.update(PATH_INFO="/hi", REQUEST_METHOD="GET")
    cap = {}
    body = b"".join(flask_app(env, lambda st, hd, exc=None: cap.update(status=st, headers=hd)))
    flask_ok = cap["status"] == "200 OK" and body == b"hi" and "`start_response` received `200 OK`, and the returned body was `b'hi'`" in t

    cls = {}
    exec(block_with(t, "class AddHeader"), {}, cls)
    AddHeader = cls["AddHeader"]
    flask_app.wsgi_app = AddHeader(flask_app.wsgi_app)
    port, srv = run(flask_app)
    s, h, b = http(f"http://127.0.0.1:{port}/hi")
    srv.shutdown()
    mw_ok = s == 200 and h.get("X-Handled-By") == "AddHeader-middleware" and b == b"hi" and "AddHeader-middleware" in t

    d = Path(tempfile.mkdtemp(prefix="w8g"))
    (d / "mymodule.py").write_text("def application(environ, start_response):\n    start_response('200 OK', [('Content-Type', 'text/plain')])\n    return [b'Hello from gunicorn']\n")
    gport = free_port()
    cmd = re.search(r"^gunicorn (.*)$", block_with(t, "gunicorn -w 4", lang="bash"), re.M).group(1)
    assert cmd == "-w 4 -b 127.0.0.1:8000 mymodule:application", cmd
    gu = subprocess.Popen([sys.executable, "-m", "gunicorn", "-w", "4", "-b", f"127.0.0.1:{gport}", "--chdir", str(d), "mymodule:application"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    gres, workers = None, None
    for _ in range(60):
        try:
            gres = http(f"http://127.0.0.1:{gport}/")
            break
        except Exception:
            time.sleep(0.25)
    time.sleep(1.5)
    kids = subprocess.run(["pgrep", "-P", str(gu.pid)], capture_output=True, text=True).stdout.split()
    workers = len(kids)
    gu.terminate()
    gu.wait(10)
    gun_ok = gres and gres[0] == 200 and gres[1].get("Server") == "gunicorn" and gres[2] == b"Hello from gunicorn" and workers == 4
    expansion_ok = has(t, r"stands for \*\*Web Server Gateway Interface\*\*") and has(t, r"\"Web-Services Gateway Interface\", which is wrong")
    ok = (out["simple"] == (200, "text/plain", b"Hello, WSGI World!") and environ_ok and str_ok and flask_ok and mw_ok and gun_ok and expansion_ok)
    return ok, (f"simple_app under wsgiref+validator: {out['simple']}; environ table matches: {environ_ok}; str body -> 500 + validator error: {str_ok}; "
                f"Flask called as WSGI: {flask_ok}; middleware header: {mw_ok}; gunicorn: {gres and gres[:2]} with {workers} worker processes; expansion text: {expansion_ok}")


# ------------------------------------------------------------------------------------------------------------------ #
# 8-javascript-basics.md : Node
# ------------------------------------------------------------------------------------------------------------------ #
HARNESS = r"""
const util = require('util'); const out = [];
console.log = (...a) => out.push(util.format(...a));
process.on('exit', () => require('fs').writeFileSync(process.argv[3], JSON.stringify(out)));
require(process.argv[2]);
"""


def run_js_block(code):
    d = Path(tempfile.mkdtemp(prefix="w8j"))
    (d / "blk.js").write_text(code)
    (d / "h.js").write_text(HARNESS)
    p = subprocess.run([NODE, "h.js", str(d / "blk.js"), str(d / "out.json")], cwd=d, capture_output=True, text=True, timeout=30)
    if p.returncode != 0:
        raise RuntimeError(f"node failed: {p.stderr.strip().splitlines()[-1] if p.stderr.strip() else p.returncode}")
    return json.loads((d / "out.json").read_text())


def expected_comments(code):
    exp = []
    for line in code.splitlines():
        m = re.match(r"^(?!\s*//).*console\.log\(.*\)[;\s}]*//\s*(.*?)\s*$", line)
        if m:
            exp.append(re.sub(r"\s+\(.*\)$", "", m.group(1)))
    return exp


def in_order(exp, got):
    i = 0
    for g in got:
        if i < len(exp) and g == exp[i]:
            i += 1
    return i == len(exp)


def js_blocks_print_what_they_say():
    t = note(J)
    blocks = [b for b in fenced(t, "js") if "prompt(" not in b]
    bad, n = [], 0
    for b in blocks:
        exp, got = expected_comments(b), run_js_block(b)
        n += len(exp)
        if not in_order(exp, got):
            bad.append(f"{b.strip().splitlines()[0][:40]!r}: expected {exp} but printed {got}")
    loops = run_js_block(block_with(t, "for (const key in", lang="js"))
    loops_ok = loops == ["0", "1", "2", "apple", "banana", "0 is a string", "1 is a string"]
    return not bad and loops_ok and n > 50, f"{len(blocks)} ```js blocks run in Node, {n} `console.log // expected` comments compared; mismatches: {bad or 'none'}; loop outputs {loops}"


def js_tables_and_traps():
    t = note(J)
    exprs = r"""
const q = (f) => { try { return f(); } catch (e) { return e.name; } };
const r = {};
r.typeof = ["hello", 10, 3.5, true, undefined, null, [1, 2], {}, () => 1, 10n].map(v => typeof v);
r.arrayIsArray = [Array.isArray([]), Array.isArray({})];
r.eq = [5 == "5", 5 === "5", 0 == false, 0 === false, null == undefined, null === undefined, "" == false, [] == false, null == 0, NaN == NaN];
r.concat = ["5" + 3, 5 + 3, "5" - 3, "3" * "4", "a" + null];
r.falsy = [false, 0, -0, 0n, "", null, undefined, NaN].map(v => !v);
r.truthy = ["0", "false", [], {}].map(v => !!v);
r.float = [0.1 + 0.2, 0.1 + 0.2 === 0.3];
r.undefinedIndex = [1, 2][5] === undefined;
r.varBlock = q(() => { if (true) { var a = 10; let b = 20; } return [a, typeof b]; });
r.tdz = q(() => { z; let z = 1; });
r.constAssign = q(() => { const P = 3.14; P = 3; });
r.arrowObj = [(() => { a: 1 })(), (() => ({ a: 1 }))().a];
r.retNewline = (function () { return
  42; })() === undefined;
r.forIn = (() => { Array.prototype.extra = 1; const k = []; for (const i in ["a"]) k.push(i); delete Array.prototype.extra; return k; })();
r.forOfObj = q(() => { for (const x of { a: 1 }) { } });
r.lost = (() => { const p = { name: "Alice", greet() { return "Hi " + this.name; } }; const g = p.greet; return [p.greet(), g()]; })();
r.promptType = [typeof prompt, typeof alert];
r.practice = [typeof null, typeof [], "5" + 3, "5" - 3, 5 == "5", 5 === "5"];
r.hoistFn = hoisted(); function hoisted() { return "ok"; }
r.arrowHoist = q(() => { early(); const early = () => 1; });
r.defaults = ((n = "guest") => n)(null);
console.log(JSON.stringify(r));
"""
    p = node_run(exprs)
    r = json.loads(p.stdout)
    checks = {
        "typeof": r["typeof"] == ["string", "number", "number", "boolean", "undefined", "object", "object", "object", "function", "bigint"],
        "arrayIsArray": r["arrayIsArray"] == [True, False],
        "==": r["eq"] == [True, False, True, False, True, False, True, True, False, False],
        "concat": r["concat"] == ["53", 8, 2, 12, "anull"],
        "falsy": all(r["falsy"]), "truthy": all(r["truthy"]),
        "float": r["float"] == [0.30000000000000004, False], "undef": r["undefinedIndex"] is True,
        "var": r["varBlock"] == [10, "undefined"], "tdz": r["tdz"] == "ReferenceError", "const": r["constAssign"] == "TypeError",
        "arrowObj": r["arrowObj"] == [None, 1], "retNewline": r["retNewline"] is True,
        "forIn": r["forIn"] == ["0", "extra"], "forOfObj": r["forOfObj"] == "TypeError",
        "lost this": r["lost"] == ["Hi Alice", "Hi undefined"], "node has no prompt": r["promptType"] == ["undefined", "undefined"],
        "practice": r["practice"] == ["object", "object", "53", 2, True, False], "hoist": r["hoistFn"] == "ok", "arrow": r["arrowHoist"] == "ReferenceError",
        "default null": r["defaults"] is None,
    }
    rows = {  # table of typeof values in the note
        "`\"hello\"` | `\"string\"`": "string", "`undefined` | `\"undefined\"`": "undefined", "`null` | **`\"object\"`**": "object",
        "| `[1, 2]` | **`\"object\"`**": "object", "| `10n` (BigInt) | `\"bigint\"`": "bigint"}
    text_ok = all(k in t for k in rows) and "Falsy** values are exactly these eight: `false`, `0`, `-0`, `0n`, `\"\"`, `null`, `undefined`, `NaN`" in t
    text_ok = text_ok and "`0.30000000000000004`" in t and 'In Node it gives "Hi undefined"' in t
    text_ok = text_ok and has(t, r"`\"object\"`, `\"object\"`, `\"53\"`, `2`, `true`, `false`")
    return all(checks.values()) and text_ok, f"failed: {[k for k, v in checks.items() if not v] or 'none'}; note text matches: {text_ok}; value of `{{}}` forms checked in Node {process_version()}"


def process_version():
    return subprocess.run([NODE, "-p", "process.versions.v8"], capture_output=True, text=True).stdout.strip()


# ------------------------------------------------------------------------------------------------------------------ #
# the browser suite (JavaScript -- Chromium through playwright)
# ------------------------------------------------------------------------------------------------------------------ #
BROWSER_JS = r"""
const { chromium } = require('playwright');
const fs = require('fs');
const crypto = require('crypto');
const cfg = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const R = {};
const sec = async (name, fn) => { try { R[name] = await fn(); } catch (e) { R[name] = { error: String(e.stack || e).slice(0, 700) }; } };
const LAB = `http://localhost:${cfg.lab}`, LAB2 = `http://127.0.0.1:${cfg.lab}`;
const wrap = (body, head = '') => `<!DOCTYPE html><html><head><meta charset="utf-8">${head}</head>${/<body/.test(body) ? body : '<body>' + body + '</body>'}</html>`;
const q = (b) => b;

(async () => {
  const browser = await chromium.launch();
  const ctx = await browser.newContext();
  async function fresh(html, opts = {}) {
    const page = await ctx.newPage(); const h = { page, logs: [], errors: [], dialogs: [] };
    page.on('console', m => h.logs.push([m.type(), m.text()]));
    page.on('pageerror', e => h.errors.push(e.message));
    page.on('dialog', async d => { h.dialogs.push([d.type(), d.message()]); if (d.type() === 'prompt') await d.accept(opts.promptAnswer ?? 'Alice'); else await d.accept(); });
    if (html !== null) await page.setContent(html);
    return h;
  }
  async function run(h, code) { await h.page.addScriptTag({ content: code }); }

  // ---------- 8-frontend: SSR vs CSR ----------
  await sec('fe', async () => {
    const base = `http://127.0.0.1:${cfg.fe}`; const o = {};
    const h = await fresh(null); const reqs = []; h.page.on('request', r => { const p = new URL(r.url()).pathname; if (/^\/(ssr|csr|api)/.test(p)) reqs.push(p); });
    await h.page.goto(base + '/ssr'); o.ssr = [[...reqs], await h.page.evaluate(() => document.querySelectorAll('li').length)]; reqs.length = 0;
    await h.page.goto(base + '/csr'); await h.page.waitForSelector('li');
    o.csr = [[...reqs], await h.page.evaluate(() => [...document.querySelectorAll('li')].map(l => l.textContent))];
    o.csrSource = await h.page.evaluate(async () => (await (await fetch('/csr')).text()).includes('apple'));
    o.csrDom = await h.page.evaluate(() => document.body.innerText.includes('apple'));
    return o;
  });

  // ---------- lazy loading ----------
  await sec('lazy', async () => {
    const o = {};
    const imgs = (lazy) => Array.from({ length: 3 }, (_, i) => `<div style="height:2500px">spacer</div><img src="${LAB}/img${i}.gif" width="10" height="10" ${lazy ? 'loading="lazy"' : ''}>`).join('');
    const reqs = []; const p = await ctx.newPage(); p.on('request', r => { if (r.url().includes('/img')) reqs.push(r.url()); });
    await p.setContent(wrap(imgs(true))); await p.waitForTimeout(600); o.lazyBefore = reqs.length;
    await p.evaluate(() => window.scrollTo(0, document.body.scrollHeight)); await p.waitForTimeout(900); o.lazyAfter = reqs.length;
    const reqs2 = []; const e = await ctx.newPage(); e.on('request', r => { if (r.url().includes('/img')) reqs2.push(r.url()); });
    await e.setContent(wrap(imgs(false))); await e.waitForTimeout(600); o.eager = reqs2.length;
    return o;
  });

  // ---------- 8-javascript-basics: script placement, prompt ----------
  await sec('placement', async () => {
    const o = {};
    let h = await fresh(wrap('<h1 id="h">Hello</h1>', '<script>document.getElementById("h").textContent = "changed"<\/script>'));
    o.headError = h.errors; o.headText = await h.page.evaluate(() => document.getElementById('h').textContent);
    h = await fresh(wrap('<h1 id="h">Hello</h1><script>document.getElementById("h").textContent = "changed"<\/script>'));
    o.endErrors = h.errors; o.endText = await h.page.evaluate(() => document.getElementById('h').textContent);
    h = await fresh(wrap('<h1 id="h">Hello</h1>', '<script>document.addEventListener("DOMContentLoaded", () => { document.getElementById("h").textContent = "changed" })<\/script>'));
    o.dclText = await h.page.evaluate(() => document.getElementById('h').textContent);
    h = await fresh(null); await h.page.goto(LAB + '/defer'); o.deferText = await h.page.evaluate(() => document.getElementById('h').textContent); o.deferErrors = h.errors;
    h = await fresh(null); await h.page.goto(LAB + '/nodefer'); o.nodeferErrors = h.errors;
    // prompt block
    h = await fresh(wrap(''), { promptAnswer: 'Alice' });
    await run(h, cfg.blocks.prompt); o.promptDialogs = h.dialogs;
    const h2 = await fresh(wrap('')); h2.page.removeAllListeners('dialog'); const seen = []; h2.page.on('dialog', d => { seen.push(d.type()); d.dismiss(); });
    await h2.page.addScriptTag({ content: cfg.blocks.prompt }); o.cancelDialogs = seen;
    return o;
  });

  // ---------- 8-basic-dom-manipulation ----------
  await sec('dom', async () => {
    const o = {}; const B = cfg.blocks; const start = wrap(B.dom_start);
    async function blockOn(code, html = start) { const h = await fresh(html); await run(h, code); return h; }
    let h = await blockOn(B.dom_select); o.selectLogs = h.logs.map(l => l[1]); o.selectErrors = h.errors;
    h = await fresh(start); o.types = await h.page.evaluate(() => ({ byId: document.getElementById('title').constructor.name, byClass: document.getElementsByClassName('highlight').constructor.name, byTag: document.getElementsByTagName('p').constructor.name, qsa: document.querySelectorAll('p').constructor.name, missId: document.getElementById('nope'), missQs: document.querySelector('.nope'), missQsa: document.querySelectorAll('.nope').length }));
    o.live = await h.page.evaluate(() => { const live = document.getElementsByClassName('highlight'), st = document.querySelectorAll('.highlight'); const b = [live.length, st.length]; const p = document.createElement('p'); p.className = 'highlight'; document.body.appendChild(p); return [b, [live.length, st.length]]; });
    h = await fresh(wrap('<div id="d">old <b>bold</b> <span style="display:none">hidden</span></div>'));
    o.props = await h.page.evaluate(() => { const d = document.getElementById('d'); const r = { html: d.innerHTML, text: d.textContent, inner: d.innerText }; d.textContent = '<i>x</i>'; r.afterText = [d.innerHTML, d.children.length]; d.innerHTML = '<i>x</i>'; r.afterHtml = d.children.length; return r; });
    h = await fresh(wrap('<div id="d"></div>'));
    await h.page.evaluate(() => { window.pwned = 0; document.getElementById('d').innerHTML = '<img src="x" onerror="window.pwned = 1">'; }); await h.page.waitForTimeout(300); o.xssHtml = await h.page.evaluate(() => window.pwned);
    await h.page.evaluate(() => { window.pwned = 0; document.getElementById('d').innerHTML = '<script>window.pwned = 2<\/script>'; }); o.xssScript = await h.page.evaluate(() => window.pwned);
    await h.page.evaluate(() => { window.pwned = 0; document.getElementById('d').textContent = '<img src="x" onerror="window.pwned = 3">'; }); await h.page.waitForTimeout(300); o.xssText = await h.page.evaluate(() => [window.pwned, document.getElementById('d').children.length]);
    h = await blockOn(B.dom_content); o.content = await h.page.evaluate(() => [document.getElementById('myElement').innerHTML]); o.contentErrors = h.errors;
    h = await blockOn(B.dom_attr); o.attr = await h.page.evaluate(() => { const e = document.getElementById('newId'); return [e && e.className, document.getElementById('myElement')]; }); o.attrErrors = h.errors;
    h = await blockOn(B.dom_classlist); o.classlist = await h.page.evaluate(() => document.querySelector('p').className); o.classlistErrors = h.errors;
    h = await fresh(wrap('<div id="e" class="x" data-x="1"></div>'));
    o.attrs = await h.page.evaluate(() => { const e = document.getElementById('e'); e.setAttribute('data-x', 5); return [e.getAttribute('data-x'), typeof e.getAttribute('data-x'), e.dataset.x, e.getAttribute('nope')]; });
    h = await blockOn(B.dom_style); o.style = await h.page.evaluate(() => { const e = document.getElementById('myElement'); const r = [e.style.color, e.style.backgroundColor, getComputedStyle(e).color]; e.style['background-color'] = 'blue'; r.push(e.style.backgroundColor); return r; }); o.styleErrors = h.errors;
    h = await blockOn(B.dom_addremove); o.addremove = await h.page.evaluate(() => [...document.getElementById('list').children].map(c => c.textContent)); o.addremoveErrors = h.errors;
    o.ws = await h.page.evaluate(() => [document.getElementById('list').firstChild.nodeType, document.getElementById('list').firstElementChild.textContent]);
    h = await blockOn(B.dom_remove); o.removed = await h.page.evaluate(() => document.getElementById('oldElement')); o.removeErrors = h.errors;
    h = await fresh(wrap('<div id="holder"><p id="p">x</p></div><div id="other"></div>'));
    o.removeNotChild = await h.page.evaluate(() => { try { document.body.removeChild(document.getElementById('p')); return 'no error'; } catch (e) { return e.name; } });
    o.move = await h.page.evaluate(() => { const a = document.createElement('div'), b = document.createElement('div'), x = document.createElement('p'); a.appendChild(x); b.appendChild(x); return [a.children.length, b.children.length]; });
    h = await blockOn(B.dom_event); await h.page.click('#myButton'); o.eventLogs = h.logs.map(l => l[1]); o.eventErrors = h.errors;
    h = await fresh(wrap('<button id="b">Click</button><p id="out"></p>'));
    await h.page.evaluate(() => { const out = document.getElementById('out'), b = document.getElementById('b'); b.addEventListener('click', () => { out.textContent += 'L1 '; }); b.addEventListener('click', () => { out.textContent += 'L2 '; }); b.onclick = () => { out.textContent += 'A '; }; b.onclick = () => { out.textContent += 'B '; }; });
    await h.page.click('#b'); o.listeners = await h.page.evaluate(() => document.getElementById('out').textContent);
    h = await fresh(wrap('<h1>Title</h1>')); await run(h, B.dom_write); o.write = await h.page.evaluate(() => [document.body.innerText.trim(), document.querySelector('h1')]);
    h = await fresh(wrap('')); await h.page.evaluate(`(() => { ${B.dom_log} })()`); o.consoleTypes = h.logs.map(l => l[0]); o.afterDebugger = await h.page.evaluate(() => 1);
    h = await fresh(wrap('')); await h.page.evaluate(() => { console.log('a'); console.info('b'); console.warn('c'); console.error('d'); console.table([1]); window.reached = false; debugger; window.reached = true; });
    o.allConsole = h.logs.map(l => l[0]); o.reached = await h.page.evaluate(() => window.reached);
    h = await fresh(B.dom_complete); o.complete = await h.page.evaluate(() => [document.getElementById('myElement').textContent, getComputedStyle(document.getElementById('myElement')).color]);
    await h.page.click('#myButton'); o.completeClick = [h.dialogs, h.logs.map(l => l[0] + ':' + l[1]), h.errors];
    return o;
  });

  // ---------- 8-async-dom ----------
  await sec('async', async () => {
    const o = {}; const B = cfg.blocks;
    const withUrl = (c) => c.replaceAll('https://example.com/data', LAB + '/data').replaceAll('"/data"', `"${LAB}/data"`);
    let h = await fresh(null); await h.page.goto(LAB + '/blank');
    await run(h, withUrl(B.async_noawait)); await h.page.waitForTimeout(500); o.noawaitLogs = h.logs.map(l => l[1]);
    h = await fresh(null); await h.page.goto(LAB + '/blank'); await run(h, withUrl(B.async_fetch)); await h.page.waitForTimeout(900); o.fetchLogs = h.logs.map(l => l[1]); o.fetchErrors = h.errors;
    // ticks
    o.ticks = await h.page.evaluate(async () => { let ticks = 0; const iv = setInterval(() => ticks++, 50); await new Promise(r => setTimeout(r, 500)); const a = ticks; ticks = 0; const end = performance.now() + 500; while (performance.now() < end) { } const b = ticks; clearInterval(iv); return [a, b]; });
    o.order = await h.page.evaluate(async () => { const a = []; setTimeout(() => a.push('timeout 0'), 0); Promise.resolve().then(() => a.push('promise')); a.push('sync'); await new Promise(r => setTimeout(r, 20)); return a; });
    o.awaitOrder = await h.page.evaluate(async () => { const a = []; async function f() { a.push('f start'); await null; a.push('f resumed'); } f(); a.push('caller continues'); await null; await null; return a; });
    // response.ok
    o.ok = await h.page.evaluate(async ([code, url]) => { const run = new Function('url', 'return (async () => { ' + code.replaceAll('"/api/items"', 'url') + ' return items; })()'); try { return await run(url); } catch (e) { return e.message; } }, [B.async_ok, LAB + '/missing']);
    o.fetch404 = await h.page.evaluate(async (u) => { const r = await fetch(u); return [r.ok, r.status]; }, LAB + '/missing');
    // worker
    o.worker = await h.page.evaluate(async () => { const src = 'onmessage = () => { let s = 0; for (let i = 0; i < 3e8; i++) s += i; postMessage(typeof document + "," + typeof window + "," + typeof self); }'; const w = new Worker(URL.createObjectURL(new Blob([src], { type: 'text/javascript' }))); let ticks = 0; const iv = setInterval(() => ticks++, 20); const res = await new Promise(r => { w.onmessage = e => r(e.data); w.postMessage(1); }); clearInterval(iv); return [res, ticks >= 3]; });
    // websocket
    if (cfg.ws) {
      const h2 = await fresh(null); await h2.page.goto(LAB + '/blank');
      await h2.page.evaluate(B.ws_js.replace('ws://localhost:8765', `ws://localhost:${cfg.ws}`)); await h2.page.waitForTimeout(800); o.wsLogs = h2.logs.map(l => l[1]);
      o.wsConversation = await h2.page.evaluate((port) => new Promise((res) => { const log = []; const s = new WebSocket(`ws://localhost:${port}`); s.onmessage = (ev) => { log.push(ev.data); if (log.length === 1) s.send('hi'); else if (log.length === 2) s.send('again'); else { s.close(); res(log); } }; }), cfg.ws);
    }
    // canvas
    h = await fresh(wrap(B.canvas)); o.canvas = await h.page.evaluate(() => { const c = document.getElementById('c').getContext('2d'); return [[...c.getImageData(20, 20, 1, 1).data], [...c.getImageData(60, 20, 1, 1).data]]; }); o.canvasErrors = h.errors;
    // web storage
    const sctx = await browser.newContext(); const s1 = await sctx.newPage(); await s1.goto(LAB + '/blank');
    const storageLogs = []; s1.on('console', m => storageLogs.push(m.text()));
    await s1.addScriptTag({ content: B.storage }); await s1.evaluate(() => sessionStorage.setItem('tab', '1'));
    await s1.reload(); o.afterReload = await s1.evaluate(() => [localStorage.getItem('theme'), sessionStorage.getItem('tab')]);
    const s2 = await sctx.newPage(); await s2.goto(LAB + '/blank'); o.newTab = await s2.evaluate(() => [localStorage.getItem('theme'), sessionStorage.getItem('tab')]);
    const nctx = await browser.newContext(); const s3 = await nctx.newPage(); await s3.goto(LAB + '/blank'); o.newProfile = await s3.evaluate(() => [localStorage.getItem('theme'), sessionStorage.getItem('tab')]);
    o.storageLogs = storageLogs;
    // drag and drop
    h = await fresh(wrap(B.dnd)); await h.page.dragAndDrop('#item', '#zone'); o.dnd = await h.page.evaluate(() => document.getElementById('zone').contains(document.getElementById('item'))); o.dndErrors = h.errors;
    return o;
  });

  // ---------- 8-client-validation ----------
  await sec('val', async () => {
    const o = {}; const B = cfg.blocks;
    const h = await fresh(wrap(B.val_form + '<style>input:invalid{border:2px solid red} input:valid{border:2px solid green}</style>'));
    const page = h.page;
    const st = (id) => page.evaluate((id) => { const v = document.getElementById(id).validity; const r = []; for (const k of ['valueMissing', 'typeMismatch', 'patternMismatch', 'tooShort', 'tooLong', 'rangeUnderflow', 'rangeOverflow', 'stepMismatch', 'badInput', 'customError']) if (v[k]) r.push(k); return r.length ? r : ['valid']; }, id);
    const set = (id, v) => page.evaluate(([id, v]) => { document.getElementById(id).value = v; }, [id, v]);
    const row = async (id, v) => { await set(id, v); return st(id); };
    o.mailEmpty = await st('mail'); o.mailBad = await row('mail', 'not-an-email'); o.mailAB = await row('mail', 'a@b'); o.mailOk = await row('mail', 'a@b.com');
    o.phoneAbc = await row('phone', 'abc'); o.phone10 = await row('phone', '1234567890'); o.phone11 = await row('phone', '12345678901'); o.phoneEmpty = await row('phone', '');
    o.minScript = await row('user', 'abc');
    await page.fill('#user', ''); await page.focus('#user'); await page.keyboard.type('abcd'); o.minTyped = await st('user');
    await page.fill('#user', ''); await page.keyboard.type('abcdefghij'); o.maxTyped = await page.evaluate(() => document.getElementById('user').value.length);
    o.age10 = await row('age', '10'); o.age99 = await row('age', '99'); o.age255 = await row('age', '25.5'); o.age30 = await row('age', '30');
    o.dateBefore = await row('date', '2025-12-31'); o.urlBare = await row('site', 'example.com'); o.urlOk = await row('site', 'https://example.com');
    // custom validity block
    await run(h, B.val_custom);
    o.custom = await page.evaluate(() => { const e = document.getElementById('mail'); const r = {}; e.value = 'oops'; e.dispatchEvent(new Event('input')); r.bad = [e.validity.valid, e.validity.customError, e.validationMessage]; e.value = 'ok@x.com'; e.dispatchEvent(new Event('input')); r.fixed = [e.validity.valid, e.validationMessage]; e.setCustomValidity('stuck'); r.stuck = [e.validity.valid, e.validity.customError]; e.setCustomValidity(''); r.cleared = e.validity.valid; return r; });
    // form level
    await page.evaluate(() => { document.getElementById('mail').value = ''; document.getElementById('f').addEventListener('submit', (e) => { e.preventDefault(); window.submitted = (window.submitted || 0) + 1; }); window.submitted = 0; window.invalidIds = []; document.getElementById('f').addEventListener('invalid', e => window.invalidIds.push(e.target.id), true); });
    o.formCheck = await page.evaluate(() => [document.getElementById('f').checkValidity(), window.invalidIds.slice()]);
    await page.click('button:has-text("Send")'); o.submitInvalid = await page.evaluate(() => window.submitted);
    await page.evaluate(() => { for (const [id, v] of Object.entries({ mail: 'a@b.com', user: 'abcdef', phone: '', age: '', date: '', site: '' })) document.getElementById(id).value = v; });
    await page.click('button:has-text("Send")'); o.submitValid = await page.evaluate(() => window.submitted);
    await page.evaluate(() => { document.getElementById('mail').value = ''; document.getElementById('f').noValidate = true; window.submitted = 0; });
    await page.click('button:has-text("Send")'); o.submitNoValidate = await page.evaluate(() => window.submitted);
    await page.evaluate(() => { document.getElementById('f').noValidate = false; window.submitted = 0; const b = document.createElement('button'); b.id = 'skip'; b.setAttribute('formnovalidate', ''); b.textContent = 'Skip'; document.getElementById('f').appendChild(b); });
    await page.click('#skip'); o.submitFormNoValidate = await page.evaluate(() => window.submitted);
    await page.evaluate(() => { document.getElementById('mail').value = 'a@b.com'; }); const good = await page.evaluate(() => getComputedStyle(document.getElementById('mail')).borderTopColor);
    await page.evaluate(() => { document.getElementById('mail').value = ''; }); const bad = await page.evaluate(() => getComputedStyle(document.getElementById('mail')).borderTopColor); o.css = [bad, good];
    // tampering
    await page.evaluate(() => { const m = document.getElementById('mail'); m.removeAttribute('required'); m.type = 'text'; m.value = 'garbage'; }); o.tamper = await st('mail');
    o.maxScript = await page.evaluate(() => { const u = document.getElementById('user'); u.value = 'x'.repeat(50); return [u.value.length, u.validity.tooLong]; });
    // passwords block
    const h2 = await fresh(wrap('<form><input id="pw" type="password"><input id="pw2" type="password"></form>')); await run(h2, B.val_pw);
    o.pw = await h2.page.evaluate(() => { const a = document.getElementById('pw'), b = document.getElementById('pw2'); const r = {}; a.value = 'secret'; a.dispatchEvent(new Event('input')); b.value = 'sekret'; b.dispatchEvent(new Event('input')); r.diff = [b.validity.valid, b.validationMessage]; b.value = 'secret'; b.dispatchEvent(new Event('input')); r.same = b.validity.valid; a.value = 'other'; a.dispatchEvent(new Event('input')); r.afterChange = b.validity.valid; return r; });
    o.pwErrors = h2.errors;
    return o;
  });

  // ---------- 8-wasm-and-browser-security ----------
  await sec('sec', async () => {
    const o = {}; const B = cfg.blocks;
    let h = await fresh(null); await h.page.goto(LAB + '/blank');
    await run(h, B.wasm_js); await h.page.waitForTimeout(300); o.wasmLogs = h.logs.map(l => l[1]); o.wasmErrors = h.errors;
    o.sandbox = await h.page.evaluate(async () => { const r = { require: typeof require, process: typeof process }; try { await fetch('file:///etc/passwd'); r.file = 'allowed'; } catch (e) { r.file = e.name; } return r; });
    // permissions
    o.perm = await h.page.evaluate(async () => ({ state: (await navigator.permissions.query({ name: 'geolocation' })).state, secure: isSecureContext, result: await new Promise(res => navigator.geolocation.getCurrentPosition(() => res('granted'), e => res('denied:' + e.code), { timeout: 3000 })) }));
    const gctx = await browser.newContext({ permissions: ['geolocation'], geolocation: { latitude: 12.9, longitude: 77.5 } }); const g = await gctx.newPage(); await g.goto(LAB + '/blank');
    o.granted = await g.evaluate(() => new Promise(res => navigator.geolocation.getCurrentPosition(p => res([p.coords.latitude, p.coords.longitude]), e => res('denied:' + e.code))));
    // cors
    const a = await fresh(null); await a.page.goto(LAB + '/blank'); const b = await fresh(null); await b.page.goto(LAB2 + '/blank');
    o.sameOrigin = await a.page.evaluate(async (u) => { try { await fetch(u + '/nocors'); return 'ok'; } catch (e) { return e.name + ': ' + e.message; } }, LAB);
    o.crossNoHeader = await b.page.evaluate(async (u) => { try { await fetch(u + '/nocors'); return 'ok'; } catch (e) { return e.name + ': ' + e.message; } }, LAB);
    o.crossWithHeader = await b.page.evaluate(async (u) => { try { return (await (await fetch(u + '/data')).json()).items; } catch (e) { return e.name + ': ' + e.message; } }, LAB);
    // busy loop
    o.busy = await h.page.evaluate(async () => { let t = 0; const iv = setInterval(() => t++, 10); const end = performance.now() + 300; while (performance.now() < end) { } const n = t; clearInterval(iv); return n; });
    // SRI
    const sha = (s) => 'sha384-' + crypto.createHash('sha384').update(s).digest('base64');
    const SRI_JS = cfg.sri_js;
    const sri = async (src, integrity) => { const p = await fresh(null); await p.page.goto(LAB + '/blank'); const r = await p.page.evaluate(async ([src, integrity]) => new Promise(res => { const s = document.createElement('script'); s.src = src; s.crossOrigin = 'anonymous'; if (integrity) s.integrity = integrity; s.onload = () => res('loaded'); s.onerror = () => res('blocked'); document.head.appendChild(s); }), [src, integrity]); return [r, p.logs.some(l => /integrity/i.test(l[1]))]; };
    o.sriGood = await sri(LAB + '/lib.js', sha(SRI_JS)); o.sriTampered = await sri(LAB + '/lib-tampered.js', sha(SRI_JS)); o.sriNone = await sri(LAB + '/lib-tampered.js', null); o.sriValue = sha(SRI_JS);
    return o;
  });

  await browser.close();
  console.log(JSON.stringify(R));
})().catch(e => { console.error(e); process.exit(1); });
"""

_BROWSER = {}
HANDSHAKE = []


def run_browser_suite():
    """run the Chromium suite once (needs node + playwright); returns {} (and skips) when it cannot run"""
    if _BROWSER:
        return _BROWSER.get("r", {})
    _BROWSER["r"] = {}
    if not HAVE_PW:
        SKIPPED.append("every Chromium check was skipped: node + `npm install -g playwright` (with a Chromium) are needed")
        return {}
    ft, jt, dt, at, vt, st_ = (note(x) for x in (F, J, D, A, V, S))
    blocks = {
        "prompt": block_with(jt, "prompt(", lang="js"),
        "dom_start": block_with(dt, 'id="oldElement"', lang="html"),
        "dom_select": block_with(dt, "querySelectorAll(\".highlight\")", lang="javascript"),
        "dom_content": block_with(dt, "box.innerHTML", lang="javascript"),
        "dom_attr": block_with(dt, 'setAttribute("class"', lang="javascript"),
        "dom_classlist": block_with(dt, "classList.add", lang="javascript"),
        "dom_style": block_with(dt, "backgroundColor", lang="javascript"),
        "dom_addremove": block_with(dt, "insertBefore", lang="javascript"),
        "dom_remove": block_with(dt, "oldElement.remove()", lang="javascript"),
        "dom_event": block_with(dt, 'addEventListener("click"', lang="javascript"),
        "dom_write": block_with(dt, "document.write(", lang="javascript"),
        "dom_log": block_with(dt, 'console.warn("This is a warning message")', lang="javascript"),
        "dom_complete": block_with(dt, "DOM Manipulation Example", lang="html"),
        "async_noawait": block_with(at, "fetchDataNoAwait", lang="javascript"),
        "async_fetch": block_with(at, "async function fetchData", lang="javascript"),
        "async_ok": block_with(at, "response.ok", lang="javascript"),
        "ws_js": block_with(at, "new WebSocket", lang="javascript"),
        "canvas": block_with(at, "<canvas", lang="html"),
        "storage": block_with(at, 'localStorage.setItem("theme"', lang="javascript"),
        "dnd": block_with(at, 'draggable="true"', lang="html"),
        "val_form": block_with(vt, 'id="mail"', lang="html"),
        "val_custom": block_with(vt, 'setCustomValidity("Please', lang="javascript"),
        "val_pw": block_with(vt, "checkMatch", lang="javascript"),
        "wasm_js": block_with(st_, "new Uint8Array", lang="javascript"),
    }
    cfg = {"blocks": blocks, "sri_js": SRI_JS}
    lab_port, lab_srv = serve(lab_app(), "0.0.0.0")
    cfg["lab"] = lab_port
    fe_app = load_note_app(block_with(ft, "/csr"), "fe_note_app2")
    cfg["fe"], fe_srv = serve(fe_app)
    ws_proc = None
    try:
        import websockets  # noqa: F401
        ws_port = free_port()
        code = block_with(at, "import websockets").replace("8765", str(ws_port))
        d = Path(tempfile.mkdtemp(prefix="w8w"))
        (d / "ws.py").write_text(code)
        ws_proc = subprocess.Popen([sys.executable, str(d / "ws.py")], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(50):
            try:
                socket.create_connection(("127.0.0.1", ws_port), 0.2).close()
                break
            except OSError:
                time.sleep(0.1)
        cfg["ws"] = ws_port
    except ImportError:
        SKIPPED.append("WebSocket checks skipped: pip install websockets")
        cfg["ws"] = None
    d = Path(tempfile.mkdtemp(prefix="w8b"))
    (d / "cfg.json").write_text(json.dumps(cfg))
    (d / "suite.js").write_text(BROWSER_JS)
    p = subprocess.run([NODE, "suite.js", "cfg.json"], cwd=d, capture_output=True, text=True, env=NODE_ENV, timeout=300)
    if ws_proc:
        hs = subprocess.run(["curl", "-s", "-i", "--max-time", "2", "-H", "Connection: Upgrade", "-H", "Upgrade: websocket", "-H", "Sec-WebSocket-Version: 13",
                             "-H", "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==", f"http://127.0.0.1:{cfg['ws']}/"], capture_output=True)
        HANDSHAKE.extend(hs.stdout.decode("latin-1").split("\r\n")[:4])      # the body after the headers is a binary WebSocket frame
        ws_proc.terminate()
    fe_srv.shutdown()
    lab_srv.shutdown()
    if p.returncode != 0:
        raise RuntimeError("browser suite crashed: " + p.stderr[-400:])
    _BROWSER["r"] = json.loads(p.stdout.strip().splitlines()[-1])
    _BROWSER["r"]["_nocors_hits"] = STATE["hits"]["nocors"]
    _BROWSER["r"]["_ws_port"] = cfg["ws"]
    return _BROWSER["r"]


def section(name):
    r = run_browser_suite()
    if not r:
        return None
    s = r.get(name)
    if isinstance(s, dict) and "error" in s:
        raise RuntimeError(f"browser section {name!r} failed: {s['error'][:400]}")
    return s


def js_placement_and_prompt():
    s = section("placement")
    if s is None:
        return None
    t = note(J)
    ok = (s["headError"] == ["Cannot set properties of null (setting 'textContent')"] and s["headText"] == "Hello"
          and s["endErrors"] == [] and s["endText"] == "changed" and s["dclText"] == "changed"
          and s["deferText"] == "changed" and s["deferErrors"] == [] and len(s["nodeferErrors"]) == 1
          and s["promptDialogs"] == [["prompt", "Enter your name:"], ["alert", "Hello Alice!"]] and s["cancelDialogs"] == ["prompt"]
          and "This fails with `Cannot set properties of null (setting 'textContent')`" in t
          and has(t, r"`prompt` returns a \*\*string\*\*.*or \*\*`null`\*\* if the user presses \*Cancel\*"))
    return ok, f"script in head -> {s['headError']}; end of body -> {s['endText']!r}; DOMContentLoaded -> {s['dclText']!r}; defer -> {s['deferText']!r}, no-defer errors {len(s['nodeferErrors'])}; prompt block dialogs {s['promptDialogs']}, on Cancel only {s['cancelDialogs']}"


def dom_claims():
    s = section("dom")
    if s is None:
        return None
    t = note(D)
    try:
        ok = (
            s["selectLogs"] == ["2"] and not s["selectErrors"]
            and s["types"] == {"byId": "HTMLHeadingElement", "byClass": "HTMLCollection", "byTag": "HTMLCollection", "qsa": "NodeList", "missId": None, "missQs": None, "missQsa": 0}
            and s["live"] == [[2, 2], [3, 2]]
            and s["props"] == {"html": 'old <b>bold</b> <span style="display:none">hidden</span>', "text": "old bold hidden", "inner": "old bold", "afterText": ["&lt;i&gt;x&lt;/i&gt;", 0], "afterHtml": 1}
            and s["xssHtml"] == 1 and s["xssScript"] == 0 and s["xssText"] == [0, 0]
            and s["content"] == ["<b>This is bold</b>"] and s["attr"] == ["newClass", None] and s["classlist"] == "highlight" and not (s["contentErrors"] or s["attrErrors"] or s["classlistErrors"])
            and s["attrs"] == ["5", "string", "5", None]
            and s["style"][:2] == ["red", "yellow"] and s["style"][2] == "rgb(255, 0, 0)" and s["style"][3] == "blue" and not s["styleErrors"]
            and s["addremove"] == ["zero", "one", "TWO"] and not s["addremoveErrors"] and s["ws"] == [3, "zero"]
            and s["removed"] is None and not s["removeErrors"] and s["removeNotChild"] == "NotFoundError" and s["move"] == [0, 1]
            and s["eventLogs"] == ["Clicked! type: click, target id: myButton"] and not s["eventErrors"]
            and s["listeners"] == "L1 L2 B " and s["write"] == ["This replaces the whole page if run after loading", None]
            and s["consoleTypes"] == ["log", "warning", "error"] and s["allConsole"] == ["log", "info", "warning", "error", "table"] and s["reached"] is True
            and s["complete"] == ["Hello, DOM Manipulation!", "rgb(0, 0, 255)"]
            and s["completeClick"][0] == [["alert", "Button was clicked!"]] and s["completeClick"][1] == ["log:Button click event logged", "warning:This is a warning message", "error:This is an error message"] and not s["completeClick"][2]
        )
    except KeyError as e:
        return False, f"missing result {e}: {s}"
    text_ok = all(x in t for x in (
        "the live collection reported 3 but the earlier `querySelectorAll` result still said 2",
        "`innerHTML` is `old <b>bold</b> <span style=\"display:none\">hidden</span>`, `textContent` is `old bold hidden`, and `innerText` is `old bold`",
        "**ran the `onerror` code**", "(A `<script>` tag inserted through `innerHTML` is not run, but handlers like `onerror` are.)",
        "Starting from `one, two` this produces: `zero, one, TWO`.", "the first parent had 0 children and the second had 1",
        "a click ran both listeners and only the *last* `onclick`", "left the `<h1>` gone and the body containing only the written text",
        "`debugger;` was simply skipped and the code after it ran", "returns `rgb(255, 0, 0)` after the code above", "throws `NotFoundError`"))
    return ok and text_ok, f"every snippet of the page was run on the starting page of the note; results: {json.dumps({k: s[k] for k in ('live', 'props', 'xssHtml', 'xssScript', 'xssText', 'addremove', 'move', 'listeners', 'write', 'consoleTypes', 'complete')})}; note statements present: {text_ok}"


def async_claims():
    s = section("async")
    if s is None:
        return None
    t = note(A)
    ws_ok = True
    if section_ws_enabled():
        ws_ok = s["wsLogs"] == ["welcome", "echo:hi"] and s["wsConversation"] == ["welcome", "echo:hi", "echo:again"]
    ok = (
        s["noawaitLogs"] == ["Data fetched! response is: [object Promise]", "after the call"]
        and s["fetchLogs"][:2] == ["Fetching data...", "This runs before data is received"] and s["fetchLogs"][2].startswith("Data received:") and not s["fetchErrors"]
        and 8 <= s["ticks"][0] <= 11 and s["ticks"][1] == 0
        and s["order"] == ["sync", "promise", "timeout 0"] and s["awaitOrder"] == ["f start", "caller continues", "f resumed"]
        and s["fetch404"] == [False, 404] and s["ok"] == "HTTP 404"
        and s["worker"] == ["undefined,undefined,object", True]
        and ws_ok
        and s["canvas"] == [[255, 0, 0, 255], [0, 0, 0, 0]] and not s["canvasErrors"]
        and s["afterReload"] == ["dark", "1"] and s["newTab"] == ["dark", None] and s["newProfile"] == [None, None]
        and s["storageLogs"] == ["dark", "string", "16"] and in_order(expected_comments(block_with(t, 'localStorage.setItem("theme"', lang="javascript")), s["storageLogs"])
        and expected_comments(block_with(t, 'localStorage.setItem("theme"', lang="javascript")) == ["dark", "string", "16"]
        and s["dnd"] is True and not s["dndErrors"]
    )
    text_ok = all(x in t for x in (
        "ticked about **10 times** during a 500 ms asynchronous wait, but **0 times** during a 500 ms busy loop",
        "printed `sync`, `promise`, `timeout 0` in that order", "inside the worker `document` and `window` were `undefined`",
        "`HTTP/1.1 101 Switching Protocols`, `Upgrade: websocket`, `Connection: Upgrade`",
        "the client received `welcome`, then (after sending `hi` and `again`) `echo:hi` and `echo:again`",
        "confirmed the rectangle is red at (20, 20) and untouched (transparent) at (60, 20)",
        "a *new tab* of the same site saw `localStorage` (`dark`) but an empty `sessionStorage`; a *different browser profile* saw neither",
        "Dragging `item` onto `zone` in a browser test moved it inside `zone`.",
        "Data received: (the parsed JSON object, shown in the browser's own format)"))
    return ok and text_ok, f"noawait logs {s['noawaitLogs']}; fetch logs {s['fetchLogs']}; ticks (async, busy) {s['ticks']}; order {s['order']}; await {s['awaitOrder']}; 404 -> {s['fetch404']}; worker {s['worker']}; websocket {s.get('wsLogs')} / {s.get('wsConversation')}; canvas {s['canvas']}; storage {s['afterReload']} {s['newTab']} {s['newProfile']} {s['storageLogs']}; dnd {s['dnd']}; note statements present: {text_ok}"


def section_ws_enabled():
    return bool(run_browser_suite().get("_ws_port"))


def websocket_handshake():
    if not run_browser_suite().get("_ws_port"):
        SKIPPED.append("WebSocket handshake check skipped (websockets not installed or no browser suite)")
        return None
    head = HANDSHAKE
    ok = bool(head) and head[0] == "HTTP/1.1 101 Switching Protocols" and "Upgrade: websocket" in head and "Connection: Upgrade" in head
    return ok, f"curl with an Upgrade request to the WebSocket server of the note answered {head}"


def validation_claims():
    s = section("val")
    if s is None:
        return None
    t = note(V)
    ok = (
        s["mailEmpty"] == ["valueMissing"] and s["mailBad"] == ["typeMismatch"] and s["mailAB"] == ["valid"] and s["mailOk"] == ["valid"]
        and s["phoneAbc"] == ["patternMismatch"] and s["phone10"] == ["valid"] and s["phone11"] == ["patternMismatch"] and s["phoneEmpty"] == ["valid"]
        and s["minScript"] == ["valid"] and s["minTyped"] == ["tooShort"] and s["maxTyped"] == 8
        and s["age10"] == ["rangeUnderflow"] and s["age99"] == ["rangeOverflow"] and s["age255"] == ["stepMismatch"] and s["age30"] == ["valid"]
        and s["dateBefore"] == ["rangeUnderflow"] and s["urlBare"] == ["typeMismatch"] and s["urlOk"] == ["valid"]
        and s["custom"] == {"bad": [False, True, "Please enter a valid email address"], "fixed": [True, ""], "stuck": [False, True], "cleared": True}
        and s["formCheck"][0] is False and "mail" in s["formCheck"][1] and "date" in s["formCheck"][1]
        and s["submitInvalid"] == 0 and s["submitValid"] == 1 and s["submitNoValidate"] == 1 and s["submitFormNoValidate"] == 1
        and s["css"] == ["rgb(255, 0, 0)", "rgb(0, 128, 0)"]
        and s["tamper"] == ["valid"] and s["maxScript"] == [50, False]
        and s["pw"] == {"diff": [False, "Passwords do not match"], "same": True, "afterChange": False} and not s["pwErrors"]
    )
    rows = ("| empty `required` field | `valueMissing` |", "| `type=\"email\"`, value `not-an-email` | `typeMismatch` |", "| `type=\"email\"`, value **`a@b`** | **valid**",
            "| `pattern=\"[0-9]{10}\"`, value `abc` | `patternMismatch` |", "| same pattern, value `12345678901` (11 digits) | `patternMismatch`", "| same pattern, **empty** (not `required`) | valid",
            "| `minlength=\"5\"`, user types `abcd` | `tooShort` |", "| `minlength=\"5\"`, value `abc` set **by a script** | **valid**", "| `maxlength=\"8\"`, user types 10 characters | only 8 are accepted |",
            "| `type=\"number\" min=\"18\"`, value 10 | `rangeUnderflow` |", "| `max=\"60\"`, value 99 | `rangeOverflow` |", "| number `25.5` with the default `step` of 1 | `stepMismatch` |",
            "| `type=\"date\"` before `min` | `rangeUnderflow` |", "| `type=\"url\"`, value `example.com` | `typeMismatch`")
    text_ok = all(r in t for r in rows) and "clicking a normal button on an invalid form did not run the `submit` handler at all" in t \
        and "a leftover `setCustomValidity(\"stuck\")` kept `valid` false" in t and "was not stopped (`maxlength` limits *typing*, not values assigned by code)" in t
    return ok and text_ok, f"states: {json.dumps({k: s[k] for k in ('mailEmpty', 'mailBad', 'mailAB', 'phone11', 'minScript', 'minTyped', 'age255', 'urlBare')})}; custom validity {s['custom']}; submit counts invalid/valid/novalidate/formnovalidate = {s['submitInvalid']}/{s['submitValid']}/{s['submitNoValidate']}/{s['submitFormNoValidate']}; css {s['css']}; tamper {s['tamper']}; passwords {s['pw']}; note rows present: {text_ok}"


def server_side_validation():
    from flask import Flask, jsonify, request
    t = note(V)
    app = load_note_app(block_with(t, '"/signup"'), "val_note_app")
    naive = Flask("naive")

    @naive.route("/signup", methods=["POST"])
    def naive_signup():
        return jsonify(email=request.form.get("email", ""), phone=request.form.get("phone", ""))
    p1, s1 = serve(naive)
    p2, s2 = serve(app)
    bypass = json.loads(http(f"http://127.0.0.1:{p1}/signup", b"email=not-an-email&phone=abc", {"Content-Type": "application/x-www-form-urlencoded"}, "POST")[2])
    st_bad, _, b_bad = http(f"http://127.0.0.1:{p2}/signup", b"email=not-an-email&phone=abc", {"Content-Type": "application/x-www-form-urlencoded"}, "POST")
    st_ok, _, b_ok = http(f"http://127.0.0.1:{p2}/signup", b"email=a%40b.com&phone=1234567890", {"Content-Type": "application/x-www-form-urlencoded"}, "POST")
    st_ab, _, _ = http(f"http://127.0.0.1:{p2}/signup", b"email=a%40b&phone=1234567890", {"Content-Type": "application/x-www-form-urlencoded"}, "POST")
    st_len = [http(f"http://127.0.0.1:{p2}/signup", f"email=a%40b.com&phone={ph}".encode(), {"Content-Type": "application/x-www-form-urlencoded"}, "POST")[0] for ph in ("12345", "12345678901", "12345abcde")]
    s1.shutdown()
    s2.shutdown()
    bad = json.loads(b_bad)
    ok = (bypass == {"email": "not-an-email", "phone": "abc"} and st_bad == 400 and set(bad["errors"]) == {"email", "phone"} and st_ok == 200 and st_ab == 400 and st_len == [400, 400, 400]
          and 'the server stored exactly `email = "not-an-email"`, `phone = "abc"`' in t and "gets status `400` with both messages" in t)
    return ok, f"a server that trusts the form accepted {bypass}; the note's route answers {st_bad} {bad}, valid input {st_ok}, `a@b` {st_ab} (the note's own regex wants a dot, unlike the HTML5 email rule)"


# ------------------------------------------------------------------------------------------------------------------ #
# 8-wasm-and-browser-security.md
# ------------------------------------------------------------------------------------------------------------------ #
def wasm_claims():
    t = note(S)
    js = block_with(t, "new Uint8Array", lang="javascript")
    # the promise resolves after the synchronous script: wait for it
    d = Path(tempfile.mkdtemp(prefix="w8wasm"))
    (d / "m.js").write_text(js + "\nsetTimeout(() => {}, 200);")
    node = subprocess.run([NODE, "-e", "const util=require('util');const out=[];console.log=(...a)=>out.push(util.format(...a));require(process.argv[1]);setTimeout(()=>process.stdout.write(JSON.stringify(out)),100)", str(d / "m.js")], capture_output=True, text=True, timeout=30)
    node_out = json.loads(node.stdout)
    hexdump = " ".join(f"{int(x, 16):02x}" for x in re.findall(r"0x([0-9a-f]{2})", js))
    byte_list = [int(x, 16) for x in re.findall(r"0x([0-9a-f]{2})", js)]
    layout = "".join(re.findall(r"^([0-9a-f]{2}(?: {1,2}[0-9a-f]{2})*)", block_with(t, "magic number", lang="text"), re.M)).replace(" ", "")
    layout_bytes = bytes.fromhex(layout + "20 00 20 01 6a 0b".replace(" ", ""))
    props = node_run(r"""
const bytes = new Uint8Array(JSON.parse(process.argv[2]));
(async () => {
  const mod = await WebAssembly.compile(bytes); const { exports } = await WebAssembly.instantiate(mod, {});
  let bad; try { new WebAssembly.Module(new Uint8Array([0, 0x61, 0x73, 0x6d, 1, 0, 0, 0, 1, 2])); } catch (e) { bad = e.constructor.name; }
  console.log(JSON.stringify({ imports: WebAssembly.Module.imports(mod), exports: WebAssembly.Module.exports(mod), add: exports.add(2, 3), wrap: exports.add(2147483647, 1), bad }));
})();
""", json.dumps(byte_list))
    pr = json.loads(props.stdout)
    extra, extra_note = True, "memory-trap / fac checks skipped (no wabt)"
    if WABT_DIR:
        wat = block_with(t, "(module", lang="wat")
        r = node_run(r"""
(async () => {
  const wabt = await require(process.argv[2])();
  const wat = process.argv[3]; const m = wabt.parseWat('a.wat', wat); const { buffer } = m.toBinary({});
  const big = wabt.parseWat('b.wat', `(module (memory (export "mem") 1) (func (export "load") (param i32) (result i32) local.get 0 i32.load)
    (func $fac (export "fac") (param i32) (result i32) (if (result i32) (i32.le_s (local.get 0) (i32.const 1)) (then (i32.const 1)) (else (i32.mul (local.get 0) (call $fac (i32.sub (local.get 0) (i32.const 1))))))))`).toBinary({}).buffer;
  const { instance } = await WebAssembly.instantiate(big, {}); let trap; try { instance.exports.load(70000); } catch (e) { trap = e.constructor.name + ': ' + e.message; }
  console.log(JSON.stringify({ bytes: [...buffer], memBytes: instance.exports.mem.buffer.byteLength, trap, fac: instance.exports.fac(10) }));
})();
""", WABT_DIR, wat)
        rr = json.loads(r.stdout)
        extra = (rr["bytes"] == byte_list and rr["memBytes"] == 65536 and rr["trap"] == "RuntimeError: memory access out of bounds" and rr["fac"] == 3628800)
        extra_note = f"wat2wasm of the note's text gives the same {len(rr['bytes'])} bytes: {rr['bytes'] == byte_list}; trap {rr['trap']!r}; fac(10)={rr['fac']}; memory {rr['memBytes']} bytes"
    else:
        SKIPPED.append("WebAssembly memory-trap / recursion / WAT-assembly checks skipped (npm install wabt next to the notes, or globally)")
    s = section("sec")
    browser_ok = True if s is None else (s["wasmLogs"] == ["5"] and not s["wasmErrors"])
    ok = (node_out == ["5"] and len(byte_list) == 41 and layout_bytes == bytes(byte_list) and pr["imports"] == [] and pr["exports"] == [{"name": "add", "kind": "function"}]
          and pr["add"] == 5 and pr["wrap"] == -2147483648 and pr["bad"] == "CompileError" and extra and browser_ok
          and "this module is **41 bytes**" in t)
    return ok, f"the 41-byte module of the note ({len(byte_list)} bytes; the annotated layout is the same bytes: {layout_bytes == bytes(byte_list)}) prints {node_out} in Node and {s and s['wasmLogs']} in Chromium; imports {pr['imports']}; 2147483647+1 = {pr['wrap']}; corrupt module -> {pr['bad']}; {extra_note}"


def sandbox_cors_permissions():
    s = section("sec")
    if s is None:
        return None
    t = note(S)
    hits = run_browser_suite().get("_nocors_hits")
    ok = (s["sandbox"] == {"require": "undefined", "process": "undefined", "file": "TypeError"}
          and s["sameOrigin"] == "ok" and s["crossNoHeader"] == "TypeError: Failed to fetch" and s["crossWithHeader"] == ["a", "b"] and hits >= 2
          and s["perm"] == {"state": "prompt", "secure": True, "result": "denied:1"} and s["granted"] == [12.9, 77.5] and s["busy"] == 0
          and "failed with a `TypeError`" in t and "`TypeError: Failed to fetch`" in t and "error code 1 (*permission denied*)" in t
          and "a 10 ms timer ticked **0 times**" in t and "The request is still *sent* and the server still *runs* the handler" in t)
    return ok, f"sandbox {s['sandbox']}; same origin {s['sameOrigin']}; cross origin without header {s['crossNoHeader']}, with header {s['crossWithHeader']}; the server handled {hits} requests to /nocors (same-origin + the blocked cross-origin one); geolocation {s['perm']}, granted -> {s['granted']}; ticks of a 10 ms timer during a 300 ms busy loop: {s['busy']}"


def sri_claims():
    s = section("sec")
    if s is None:
        return None
    t = note(S)
    cmd = block_with(t, "openssl dgst", lang="bash")
    d = Path(tempfile.mkdtemp(prefix="w8sri"))
    (d / "lib.js").write_bytes(SRI_JS.encode())
    out = subprocess.run(["bash", "-c", cmd.strip()], cwd=d, capture_output=True, text=True).stdout.strip() if shutil.which("openssl") else None
    ok = (s["sriGood"] == ["loaded", False] and s["sriTampered"] == ["blocked", True] and s["sriNone"] == ["loaded", False]
          and (out is None or out == s["sriValue"]) and "with the **same URL after the file was tampered with**, the browser **blocked** it" in t
          and 'integrity="sha384-BASE64HASH"' in t and "with no `integrity` attribute the tampered script ran without complaint" in t)
    return ok, f"correct hash -> {s['sriGood']}; tampered file -> {s['sriTampered']} (blocked, integrity error in the console); no integrity attribute -> {s['sriNone']}; the note's openssl command prints {out} == the hash the browser expects {s['sriValue']}"


def rate_limiter():
    t = note(S)
    app = load_note_app(block_with(t, "Retry-After"), "rl_note_app")
    port, srv = serve(app)
    codes = [http(f"http://127.0.0.1:{port}/api")[0] for _ in range(8)]
    s, h, b = http(f"http://127.0.0.1:{port}/api")
    time.sleep(1.1)
    after = http(f"http://127.0.0.1:{port}/api")[0]
    srv.shutdown()
    ok = codes == [200] * 5 + [429] * 3 and s == 429 and h.get("Retry-After") == "1" and after == 200 and "`200, 200, 200, 200, 200, 429, 429, 429`" in t
    return ok, f"8 quick requests -> {codes}; the next one -> {s} with Retry-After {h.get('Retry-After')!r}; after the 1 s window -> {after}"


def dos_arithmetic():
    t = note(S)
    ok = 10_000 * 1 == 10_000 and 10_000 / 100 == 100 and "10,000 browsers each send one request per second, the target receives 10,000 requests per second" in t
    return ok, "10,000 browsers x 1 request/s = 10,000 requests/s, 100x the 100 requests/s capacity used as the illustration (arithmetic only)"


# ------------------------------------------------------------------------------------------------------------------ #
# structure and hygiene
# ------------------------------------------------------------------------------------------------------------------ #
def md_files():
    return sorted(NOTES.glob("*.md"))


def index_lists_everything():
    t = note(IX)
    files = sorted(f.name for f in NOTES.glob("*.md") if f.name != IX)
    linked = set(re.findall(r"\]\(([^)#]+\.md)\)", t))
    missing = [f for f in files if f not in linked]
    broken = [f for f in linked if not (NOTES / f).exists()]
    dup = [f.name for f in NOTES.iterdir() if f.name.lower() == "8-frontend.md" and f.name != "8-frontend.md"]
    return not missing and not broken and not dup and "<SessionResources" not in t, \
        f"the index links all {len(files)} topic files ({files}); not linked: {missing or 'none'}; broken: {broken or 'none'}; case-duplicate 8-Frontend.md: {dup or 'none'}; VitePress component removed: {'<SessionResources' not in t}"


def github_slug(heading):
    s = re.sub(r"[`*]", "", heading.strip().lower())
    s = re.sub(r"[^\w\- ]", "", s, flags=re.UNICODE)
    return s.replace(" ", "-")


def no_vitepress_syntax():
    found = []
    for f in md_files():
        in_code = False
        for i, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if line.lstrip().startswith("```"):
                in_code = not in_code
                if re.match(r"^```\w+ \[", line):
                    found.append(f"{f.name}:{i}")
                continue
            if in_code:
                continue
            if re.match(r"^\s*:::|^== |</?[A-Z]\w+[^>]*/?>", line) or "SessionResources" in line or "DOMNotice" in line:
                found.append(f"{f.name}:{i}")
    return not found, f"VitePress-only syntax (::: / == tabs / <Component/>): {found or 'none'}"


def no_stripped_html():
    found = []
    for f in md_files():
        in_code = False
        for i, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if line.lstrip().startswith("```"):
                in_code = not in_code
            if in_code:
                continue
            clean = re.sub(r"`[^`]*`", "", line)
            if re.search(r"style\s*=|class\s*=|&emsp;|<font|<center|<div|<pre|<table|<ul>|<li>|<h[1-6]>|<span", clean):
                found.append(f"{f.name}:{i}")
    return not found, f"HTML that GitHub removes or ignores (style=, class=, <div>, <pre>, <table> ...): {found or 'none'}"


def alerts_and_details():
    bad = []
    for f in md_files():
        t = f.read_text(encoding="utf-8")
        for i, line in enumerate(t.splitlines(), 1):
            m = re.match(r"^> \[!(\w+)\]\s*$", line)
            if m and m.group(1) not in {"NOTE", "TIP", "IMPORTANT", "WARNING", "CAUTION"}:
                bad.append(f"{f.name}:{i} alert type")
            if re.match(r"^>\s*\[!\w+\]\S", line):
                bad.append(f"{f.name}:{i} text after [!TYPE]")
        if t.count("<details>") != t.count("</details>"):
            bad.append(f"{f.name}: unbalanced <details>")
        for m in re.finditer(r"<summary>(.*?)</summary>", t, re.S):
            if "`" in m.group(1):
                bad.append(f"{f.name}: backticks inside <summary> ({m.group(1)[:30]!r})")
    return not bad, f"alerts written correctly, <details> balanced, no backticks in <summary>: {bad or 'ok'}"


def fences_and_latex():
    bad = []
    for f in md_files():
        open_ = False
        t = f.read_text(encoding="utf-8")
        for i, line in enumerate(t.splitlines(), 1):
            m = re.match(r"^(\s*)```(.*)$", line)
            if not m:
                continue
            if not open_:
                open_ = True
                if "[" in m.group(2):
                    bad.append(f"{f.name}:{i} labelled fence {line!r}")
            else:
                open_ = False
                if m.group(2).strip():
                    bad.append(f"{f.name}:{i} closing fence {line!r}")
        if open_:
            bad.append(f"{f.name}: unclosed fence")
    return not bad, f"fences closed cleanly: {bad or 'ok'}"


def tables_consistent():
    bad = []
    for f in md_files():
        in_code, width = False, None
        for i, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if line.lstrip().startswith("```"):
                in_code = not in_code
            if in_code:
                continue
            if line.startswith("|"):
                cells = len(re.split(r"(?<!\\)\|", re.sub(r"`[^`]*`", lambda m: m.group(0).replace("|", "\\|"), line).rstrip().rstrip("|")[1:]))
                if width is None:
                    width = cells
                elif cells != width:
                    bad.append(f"{f.name}:{i} {cells} cells, header has {width}")
            else:
                width = None
    return not bad, f"every table row has as many cells as its header (GitHub cuts a cell at every unescaped |): {bad or 'ok'}"


def links_resolve():
    bad, n = [], 0
    for f in md_files():
        raw = f.read_text(encoding="utf-8")
        text_ = re.sub(r"```.*?```", "", raw, flags=re.S)
        for m in re.finditer(r"!?\[[^\]]*\]\(([^)\s]+)\)", text_):
            url = m.group(1)
            if re.match(r"(https?:|mailto:)", url):
                continue
            n += 1
            path, _, anchor = url.partition("#")
            target = (f.parent / path).resolve() if path else f
            if not target.exists():
                bad.append(f"{f.name}: {url} (not found)")
            elif anchor and target.suffix == ".md":
                tt = re.sub(r"```.*?```", "", target.read_text(encoding="utf-8"), flags=re.S)
                slugs = {github_slug(h) for h in re.findall(r"^#{1,6}\s+(.*)$", tt, re.M)}
                if anchor not in slugs:
                    bad.append(f"{f.name}: {url} (no such heading)")
    return not bad, f"{n} local links, anchors and images checked: {bad or 'all resolve'}"


def mermaid_renders():
    js, node = os.environ.get("MERMAID_JS"), shutil.which("node")
    if not (js and Path(js).exists() and node and HAVE_PW):
        SKIPPED.append("mermaid render check skipped (set MERMAID_JS=.../mermaid.min.js, needs node + playwright)")
        return None
    diagrams, where = [], []
    for f in md_files():
        for m in re.finditer(r"^\s*```mermaid\n(.*?)^\s*```", f.read_text(encoding="utf-8"), re.S | re.M):
            diagrams.append(m.group(1))
            where.append(f.name)
    with tempfile.TemporaryDirectory() as d:
        Path(d, "in.json").write_text(json.dumps(diagrams))
        Path(d, "r.js").write_text(r"""
const { chromium } = require('playwright'); const fs = require('fs');
(async () => { const [js, input] = process.argv.slice(2);
  const diagrams = JSON.parse(fs.readFileSync(input, 'utf8'));
  const b = await chromium.launch(); const p = await b.newPage();
  await p.setContent('<html><body></body></html>'); await p.addScriptTag({ path: js });
  const out = await p.evaluate(async (ds) => { mermaid.initialize({ startOnLoad: false }); const res = [];
    for (let i = 0; i < ds.length; i++) { try { const { svg } = await mermaid.render('d' + i, ds[i]);
      const doc = new DOMParser().parseFromString(svg, 'image/svg+xml');
      res.push({ ok: true, text: [...doc.querySelectorAll('text, foreignObject')].map(n => n.textContent.trim()).filter(Boolean) });
    } catch (e) { res.push({ ok: false, err: String(e.message || e).split('\n')[0] }); } } return res; }, diagrams);
  console.log(JSON.stringify(out)); await b.close(); })();
""")
        p = subprocess.run([node, str(Path(d, "r.js")), js, str(Path(d, "in.json"))], capture_output=True, text=True, env=NODE_ENV)
        res = json.loads(p.stdout.strip().splitlines()[-1])
    bad = []
    for w, r in zip(where, res):
        if not r["ok"]:
            bad.append(f"{w}: {r['err']}")
        else:
            lit = [t_ for t_ in r["text"] if re.search(r"\*\*|&lt;|&gt;|<br|</?b>", t_)]
            if lit:
                bad.append(f"{w}: literal markup in labels {lit[:2]}")
    return not bad, f"{len(diagrams)} mermaid diagrams rendered with real mermaid ({', '.join(sorted(set(where)))}); errors / literal markup: {bad or 'none'}"


def no_personal_data():
    bad = []
    for f in md_files():
        t = f.read_text(encoding="utf-8")
        bad += [f"{f.name}: {m}" for m in re.findall(r"[\w.+-]+@[\w-]+\.[\w.]+|Downloaded by|quizpractice", t) if not m.endswith(("example.com", "x.com", "b.com"))]
    return not bad, f"no e-mail address of a person / source watermark in the notes (example addresses are placeholders): {bad or 'none'}"


def js_basics_blocks_convention():
    """```js blocks are Node-runnable and ```javascript blocks are browser blocks: nothing in a ```js block may need a browser"""
    bad = []
    for f in md_files():
        for b in fenced(f.read_text(encoding="utf-8"), "js"):
            if re.search(r"document\.|window\.|localStorage|addEventListener", b):
                bad.append(f"{f.name}: {b.strip().splitlines()[0][:40]}")
    return not bad, f"```js blocks need no browser API (except prompt/alert, which the checker runs in Chromium): {bad or 'ok'}"


# ------------------------------------------------------------------------------------------------------------------ #
if __name__ == "__main__":
    print("=" * 78 + "\nWeek 8 claim checker\n" + "=" * 78 + "\n")
    check(F, "SSR vs CSR app of the note: curl sees the data only with SSR, the browser makes 1 vs 2 requests; machine client POST", ssr_csr_machine_client)
    check(F, "HTTP caching: ETag, Last-Modified, Cache-Control: no-cache, conditional request -> 304 with an empty body", http_caching)
    check(F, "minification + gzip make files smaller; loading=\"lazy\" delays off-screen images (Chromium)", minify_and_lazy)
    check(W, "WSGI: simple_app under wsgiref + validator, environ table, str body fails, Flask called as WSGI, middleware, Gunicorn with 4 workers", wsgi_claims)
    check(J, "every ```js block of the note printed what its `// comment` says (Node)", js_blocks_print_what_they_say)
    check(J, "typeof / == / falsy / hoisting / var-let / this / for-in tables and traps", js_tables_and_traps)
    check(J, "script in <head> fails, end of body / defer / DOMContentLoaded work; prompt returns null on Cancel (Chromium)", js_placement_and_prompt)
    check(D, "every snippet of the DOM note on its starting page, and every measured statement (Chromium)", dom_claims)
    check(A, "fetch without await, async/await order, event loop, busy loop vs async, worker, response.ok, WebSocket, canvas, storage, drag and drop (Chromium)", async_claims)
    check(A, "a WebSocket starts with an HTTP Upgrade answered by 101 Switching Protocols", websocket_handshake)
    check(V, "every validity state of the table, custom validity, submit blocking, novalidate / formnovalidate, :invalid CSS, DevTools tampering (Chromium)", validation_claims)
    check(V, "curl bypasses the form; the server-side validation of the note rejects it with 400", server_side_validation)
    check(S, "the 41-byte WebAssembly module: bytes, Node, Chromium, imports, wrap-around, validation, memory trap", wasm_claims)
    check(S, "sandbox (no file://, no Node), same-origin / CORS (request still reaches the server), permissions, busy-loop DoS", sandbox_cors_permissions)
    check(S, "Subresource Integrity: good hash loads, tampered file blocked, no attribute = no protection; the openssl command", sri_claims)
    check(S, "rate limiter of the note: 5 x 200 then 429, Retry-After, window reset", rate_limiter)
    check(S, "DoS arithmetic of the note", dos_arithmetic)
    check(IX, "the index links every topic file; no duplicate 8-Frontend.md", index_lists_everything)
    check("week8/*.md", "no VitePress-only syntax (:::, == tabs, components)", no_vitepress_syntax)
    check("week8/*.md", "no HTML that GitHub strips (style, class, div, pre, table cards)", no_stripped_html)
    check("week8/*.md", "alerts, <details> and <summary> written correctly", alerts_and_details)
    check("week8/*.md", "fences are closed cleanly", fences_and_latex)
    check("week8/*.md", "every table row has the same number of cells as its header", tables_consistent)
    check("week8/*.md", "every local link, #anchor and image resolves", links_resolve)
    check("week8/*.md", "```js blocks are Node-runnable (browser code is in ```javascript blocks)", js_basics_blocks_convention)
    check("week8/*.md", "no personal data in the notes", no_personal_data)
    m = mermaid_renders()
    if m is not None:
        check("week8/*.md", "mermaid diagrams render without literal markup", lambda: m)

    wrong = [f for ok, f in RESULTS if not ok]
    print("=" * 78)
    print(f"{len(RESULTS)} checks, {len(RESULTS) - len(wrong)} OK, {len(wrong)} WRONG")
    if wrong:
        print("files with WRONG statements:", ", ".join(sorted(set(wrong))))
    print("\nNOT VERIFIABLE HERE (kept because they are standard, but not executed):")
    for s in SKIPPED + [
        "which engine ships in which browser, the lecture's examples of CAPTCHA use (railway Tatkal booking, CoWin) and of what Next.js / Gatsby / Jekyll / Hugo do",
        "the claim that WebAssembly gives near-native speed and that Emscripten maps OpenGL to WebGL (hardware- and version-dependent / documentation)",
        "CDN, brotli compression and `Cache-Control: max-age` behaviour (only the ETag / 304 and no-cache responses of Flask were run)",
        "site isolation (separate processes per site), Content Security Policy as a crypto-mining defence, and the existence of paid CAPTCHA-solving services",
        "the camera / microphone / notification permission prompts (a headless browser has no devices; only geolocation was run), a real screen reader and WCAG conformance",
        "ASGI / FastAPI / Django Channels as the asynchronous successor to WSGI, uWSGI / Waitress / mod_wsgi and Nginx-in-front deployments (only Gunicorn and wsgiref were run)",
        "external links (MDN, javascript.info, python.org PEP 3333)",
    ]:
        print("  -", s)
    sys.exit(1 if wrong else 0)
