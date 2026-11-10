"""
Week 3 notes -- claim checker.

Every check takes one statement or code example from the week3 notes and runs it
for real:

    * EVERY ```python example (3-1 .. 3-4) is executed and its printed output is compared with
      the output block shown in the note (blank lines and indentation ignored for HTML output,
      exact for pyhtml)
    * %-formatting, str.format, f-strings, string.Template ... CPython (incl. a leak demo and timeit)
    * pyhtml ................................. the real PyHTML 1.3.2 library
    * Jinja2 ................................. the real Jinja2 3.1 (Template, Environment, DictLoader,
                                               SandboxedEnvironment, extensions) and Flask's jinja_env
    * every Jinja template snippet is parsed with Environment().parse()

and reports whether the notes are right:

    OK     -> the notes say what actually happens
    WRONG  -> the notes say something that does not happen (the evidence shows what does)

A check usually has two halves: the FACT (measured here) and the NOTE TEXT (the markdown contains the
correct statement and not the wrong one). The claims are written as the notes state them *after* the
accuracy fixes, so a clean run ends with "0 WRONG".

Run (from anywhere), in an environment that has the libraries the notes use:
    pip install jinja2 pyhtml flask
    python week3/verify_week3_claims.py        [-v]

A check whose library is missing is skipped and listed at the end.
Checked against CPython 3.13, Jinja2 3.1.6, PyHTML 1.3.2, Flask 3.x.
"""
import importlib.util
import re
import shlex
import subprocess
import sys
import tempfile
import timeit
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
VERBOSE = "-v" in sys.argv
PY = sys.executable
RESULTS, SKIPPED = [], []
HAVE = {m: importlib.util.find_spec(m) is not None for m in ("jinja2", "pyhtml", "flask")}


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def note(name):
    return (HERE / name).read_text(encoding="utf-8")


def check(file, claim, fn):
    try:
        ok, evidence = fn()
    except Exception as e:
        ok, evidence = False, f"raised {type(e).__name__}: {str(e).splitlines()[0][:150]}"
    RESULTS.append((ok, file))
    print(f"[{'OK   ' if ok else 'WRONG'}] {file}\n        claim   : {claim}\n        actual  : {evidence}\n")


def need(*libs):
    missing = [l for l in libs if not HAVE[l]]
    if missing:
        SKIPPED.append(f"checks needing {', '.join(missing)} skipped (pip install {' '.join(missing)})")
    return not missing


def has(text, pattern, flags=re.I | re.S):
    return re.search(pattern, text, flags) is not None


def md_files():
    return sorted(HERE.glob("*.md"))


def blocks(text, with_pos=False):
    """[(lang, body, start, end)] of every fenced block."""
    out = []
    for m in re.finditer(r"^[ \t]*```[ \t]*([\w+-]*)[^\n]*\n(.*?)^[ \t]*```[ \t]*$", text, re.S | re.M):
        out.append((m.group(1).lower(), m.group(2), m.start(), m.end()))
    return out


def github_slug(heading):
    s = re.sub(r"[`*_]", "", re.sub(r"<[^>]+>", "", heading).strip().lower())
    return re.sub(r"[^\w\- ]", "", s, flags=re.UNICODE).replace(" ", "-")


def strip_fences(text):
    return re.sub(r"^[ \t]*```.*?^[ \t]*```", "", text, flags=re.S | re.M)


def run_code(code, cwd, timeout=30):
    p = Path(cwd, "snippet.py")
    p.write_text(code, encoding="utf-8")
    return subprocess.run([PY, str(p)], cwd=cwd, capture_output=True, text=True, timeout=timeout)


def norm_loose(s):
    return [l.strip() for l in s.strip().splitlines() if l.strip()]


def norm_exact(s):
    return [l.rstrip() for l in s.strip("\n").splitlines()]


# --------------------------------------------------------------------------- #
# generic: execute every python example and compare with the shown output
# --------------------------------------------------------------------------- #
def run_examples(fname, exact=False):
    t = note(fname)
    bl = blocks(t)
    ran, matched, problems = 0, 0, []
    for i, (lang, code, s, e) in enumerate(bl):
        if lang != "python":
            continue
        if re.search(r"^\s*(\{%|\{\{)", code, re.M) and "Template(" not in code and "from_string" not in code:
            continue                                            # a template shown in a python fence (should not exist any more)
        line = t[:s].count("\n") + 1
        expect_error = bool(re.search(r"#.*raises", code))
        nxt = bl[i + 1] if i + 1 < len(bl) else None
        out_block, cmd = None, None
        if nxt and nxt[0] == "bash" and re.match(r"\s*python\s", nxt[1]):          # python file + command + output (sys.argv examples)
            cmd = nxt[1].strip()
            nn = bl[i + 2] if i + 2 < len(bl) else None
            out_block = nn[1] if nn and nn[0] in ("txt", "text") else None
        elif nxt and nxt[0] in ("txt", "text", "html") and has(t[e:nxt[2]], r"output") and not has(t[e:nxt[2]], r"```"):
            out_block = nxt[1]
        with tempfile.TemporaryDirectory() as d:
            if cmd:
                Path(d, "myfile.py").write_text(code, encoding="utf-8")
                p = subprocess.run(["bash", "-c", cmd.replace("python ", f"{shlex.quote(PY)} ", 1)], cwd=d, capture_output=True, text=True, timeout=30)
            else:
                p = run_code(code, d)
        ran += 1
        if expect_error:
            if p.returncode == 0:
                problems.append(f"{fname}:{line} was expected to raise but did not")
                continue
        elif p.returncode != 0:
            problems.append(f"{fname}:{line} crashed: {p.stderr.strip().splitlines()[-1][:110]}")
            continue
        if out_block is None:
            continue
        if expect_error and out_block.lstrip().startswith(("Hello", "Traceback")) or "Traceback" in out_block:
            exp_lines = out_block.strip().splitlines()
            before = exp_lines[: [k for k, l in enumerate(exp_lines) if l.startswith("Traceback")][0]] if any(l.startswith("Traceback") for l in exp_lines) else exp_lines
            ok = norm_exact(p.stdout) == [l.rstrip() for l in before] and p.stderr.strip().splitlines()[-1] == exp_lines[-1].strip()
        else:
            got, want = (norm_exact(p.stdout), norm_exact(out_block)) if exact else (norm_loose(p.stdout), norm_loose(out_block))
            ok = got == want
            if VERBOSE or not ok:
                if not ok:
                    problems.append(f"{fname}:{line} output differs. note: {want[:4]} real: {got[:4]}")
        if ok:
            matched += 1
    return ran, matched, problems


def examples_check(fname, exact=False, libs=()):
    if not need(*libs):
        return None
    ran, matched, problems = run_examples(fname, exact)
    return not problems and ran > 0, f"{ran} python examples executed, {matched} with a shown output reproduced exactly; problems: {problems or 'none'}"


# --------------------------------------------------------------------------- #
# 3-1-pyhtml-sys.md
# --------------------------------------------------------------------------- #
def sys_argv0():
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        (d / "sub").mkdir()
        for p in (d / "myfile.py", d / "sub" / "myfile.py"):
            p.write_text("import sys\nprint(sys.argv)\n")
        rel = eval(subprocess.run([PY, "myfile.py"], cwd=d, capture_output=True, text=True).stdout)[0]
        sub = eval(subprocess.run([PY, "sub/myfile.py"], cwd=d, capture_output=True, text=True).stdout)[0]
        c = eval(subprocess.run([PY, "-c", "import sys;print(sys.argv)"], cwd=d, capture_output=True, text=True).stdout)[0]
        s = eval(subprocess.run(["bash", "-c", f'{shlex.quote(PY)} myfile.py complex "argument 3" *.py'], cwd=d, capture_output=True, text=True).stdout)
    t = note("3-1-pyhtml-sys.md")
    good = has(t, r"as (it was )?typed") and has(t, r"shell") and has(t, r"\bstr\b|strings?") and has(t, r"SystemExit") and has(t, r"version_info")
    bad = has(t, r"is always the file name")
    return rel == "myfile.py" and sub == "sub/myfile.py" and c == "-c" and s[1:] == ["complex", "argument 3", "myfile.py"] and good and not bad, (
        f"argv[0]: 'myfile.py' -> {rel!r}, 'sub/myfile.py' -> {sub!r}, -c -> {c!r}; the SHELL splits/unquotes/expands *.py -> {s[1:]}; "
        f"note says 'as typed', 'shell', SystemExit, version_info: {good}; old 'always the file name' present: {bad}")


def pyhtml_api():
    if not need("pyhtml"):
        return None
    from pyhtml import body, h1, head, html, img, p, title
    try:
        h1("Hello", style="color: blue;")
        mixed = "accepted"
    except AssertionError:
        mixed = "AssertionError"
    doc = str(html(head(title("T")), body(h1(style="color: blue;")("Hello"), p(class_="my-paragraph", gender="female")("Text"))))
    esc = str(p("<script>alert(1)</script> & \"q\""))
    safe = str(p("<b>x</b>", _safe=True))
    t = note("3-1-pyhtml-sys.md")
    fact = (mixed == "AssertionError" and doc.startswith("<!DOCTYPE html>\n<html>") and '<h1 style="color: blue;">' in doc
            and '<p class="my-paragraph" gender="female">' in doc and "\n      T\n" in doc and "&lt;script&gt;" in esc and "<b>x</b>" in safe
            and str(img(src="a.png", alt="x")) == '<img alt="x" src="a.png"/>')
    good = (has(t, r"h1\(style=\"color: blue;\"\)\(\"Hello, Pyhtml!\"\)") and has(t, r"<!DOCTYPE html>") and has(t, r"escape")
            and has(t, r"AssertionError|cannot (be )?(mix|pass)|not in the same call|separate call") and not has(t, r"h1\(\"Hello, Pyhtml!\", style="))
    return fact and good, (f"h1('Hello', style=...) -> {mixed} (children and attributes cannot be given in the same call: use tag(attrs)(children)); "
                           f"print(html(...)) starts with <!DOCTYPE html> and puts every text on its own line; attributes are sorted alphabetically; text is HTML-escaped by default "
                           f"(&lt;script&gt;), `_safe=True` disables it; void tags render <img .../>; note shows the working form + DOCTYPE + escaping: {good}")


# --------------------------------------------------------------------------- #
# 3-2-string-formatting.md
# --------------------------------------------------------------------------- #
class _Obj:
    def __init__(self):
        self.secret = "S3CR3T"
        self.items = [1, 2]


SECRET = "top-secret-module-variable"


def percent_facts():
    try:
        "%d" % "a"
        strict = False
    except TypeError:
        strict = True
    ok = (strict and "%d" % 3.7 == "3" and "%(a.b)s" % {"a.b": 1} == "1" and "%s and %r" % (None, "x") == "None and 'x'")
    try:
        "%(a.b)s" % {"a": _Obj()}
        attr = True
    except KeyError:
        attr = False
    t = note("3-2-string-formatting.md")
    good = has(t, r"TypeError") and has(t, r"truncat") and has(t, r"%\(name\)s|%\(key\)s|%\(\w+\)s")
    return ok and not attr and good, (f"'%d' % 'a' raises TypeError ({strict}); '%d' % 3.7 == '3' (silently truncates); no attribute access: '%(a.b)s' only looks up the KEY 'a.b' ({not attr}); "
                                      f"note mentions TypeError / truncation / %(name)s: {good}")


def format_facts():
    o = _Obj()
    attr = "{0.secret}".format(o) == "S3CR3T" and "{0[1]}".format([1, 2]) == "2" and "{o.items[1]}".format(o=o) == "2"
    try:
        "{a+b}".format(a=1, b=2)
        expr = True
    except KeyError:
        expr = False
    value_safe = "{}".format("{0.__class__}") == "{0.__class__}"
    leak = "{0.__init__.__globals__[SECRET]}".format(o) == SECRET
    t = note("3-2-string-formatting.md")
    good = (has(t, r"2\.6") and has(t, r"__globals__|leak") and has(t, r"(template|format) string.{0,80}(user|attacker|untrusted)")
            and not has(t, r"Python 2\.7\+\) <a"))
    return attr and not expr and value_safe and leak and good, (
        f"str.format reads attributes/items ({attr}) but cannot evaluate '{{a+b}}' ({not expr}: KeyError); a user-supplied VALUE is inserted harmlessly ({value_safe}); "
        f"a user-supplied FORMAT STRING can read module data: '{{0.__init__.__globals__[SECRET]}}' -> {SECRET!r} ({leak}); "
        f"note: introduced in 2.6, explains the leak and that the danger is a user-controlled template string: {good}")


def fstring_facts():
    user = "{__import__('os').getcwd()}"
    inserted = f"Hello {user}" == "Hello {__import__('os').getcwd()}"
    t = note("3-2-string-formatting.md")
    bad = has(t, r"Very High") or has(t, r"Both `?fstring`? and `?string\.format`? allows? \*\*dynamic expression evaluation")
    good = has(t, r"values?.{0,120}(never|not) (executed|evaluated)|just inserted|inserted as text") and has(t, r"eval")
    return inserted and good and not bad, (
        f"f\"Hello {{user}}\" with user={user!r} just inserts the text, nothing runs ({inserted}); an f-string's template is source code, so it can never come from a user "
        f"(unless someone uses eval); note says that and no longer rates f-strings 'Very High' risk: {good and not bad}; old wording present: {bad}")


def speed_claim():
    ns = {"name": "A", "age": 3}
    n = 200_000
    f = min(timeit.repeat('f"{name} {age}"', globals=ns, number=n, repeat=5))
    p = min(timeit.repeat('"%s %d" % (name, age)', globals=ns, number=n, repeat=5))
    m = min(timeit.repeat('"{} {}".format(name, age)', globals=ns, number=n, repeat=5))
    return f < p and f < m, f"{n:,} formats, best of 5: f-string {f:.4f}s, % {p:.4f}s, str.format {m:.4f}s -> 'faster than both' holds: {f < p and f < m}"


def formatting_table_text():
    t = note("3-2-string-formatting.md")
    bad = [p for p in (r"revist", r"comparision", r"comparsion", r"\./string-templating\.md", r"\./jinja2\.md") if has(t, p)]
    return not bad, f"typos / broken relative links still present: {bad or 'none'}"


# --------------------------------------------------------------------------- #
# 3-3-string-templating.md
# --------------------------------------------------------------------------- #
def template_facts():
    from string import Template
    under = Template("$my_age").substitute(my_age=3) == "3"
    nameish = Template("$nameish|${name}ish").safe_substitute(name="N") == "$nameish|Nish"
    try:
        Template("cost $ 5").substitute()
        invalid = None
    except ValueError:
        invalid = "ValueError"
    safe = Template("cost $ 5").safe_substitute() == "cost $ 5"
    try:
        Template("${x:.2f}").substitute(x=1.0)
        spec = True
    except ValueError:
        spec = False
    noattr = Template("$x.__class__").substitute(x="v") == "v.__class__"
    t = note("3-3-string-templating.md")
    good = (has(t, r"\$\{name\}ish") and has(t, r"\$nameish") and has(t, r"ValueError") and has(t, r"format specif") and not has(t, r"complex names ?\(with underscores\)"))
    return under and nameish and invalid == "ValueError" and safe and not spec and noattr and good, (
        f"$my_age works WITHOUT braces ({under}); braces are needed to end a name: ${{name}}ish vs $nameish ({nameish}); a stray '$' makes substitute raise {invalid} while safe_substitute keeps it ({safe}); "
        f"no format specs ({not spec}); '$x.__class__' is plain text after the value, no attribute access ({noattr}); note explains the braces rule + ValueError + no format specs: {good}")


def template_user_templates():
    from string import Template
    leaked = Template("$password").substitute(password="hunter2", name="A")
    t = note("3-3-string-templating.md")
    good = has(t, r"user-?(supplied|generated|provided) template.{0,200}(only|names? you pass|data you pass)") or has(t, r"can only (read|use|see) the names")
    return leaked == "hunter2" and good, f"a user-written Template can read any key you pass to substitute() ({leaked!r}) but nothing else; note says to pass only what may be shown: {good}"


# --------------------------------------------------------------------------- #
# 3-4-jinja2.md
# --------------------------------------------------------------------------- #
def jinja_template_parse():
    if not need("jinja2"):
        return None
    from jinja2 import Environment, TemplateSyntaxError
    env = Environment(extensions=["jinja2.ext.loopcontrols"])
    bad, n = [], 0
    for f in md_files():
        t = f.read_text(encoding="utf-8")
        for lang, body, s, e in blocks(t):
            if lang in ("jinja", "html", "html+jinja", "django") and re.search(r"\{%|\{\{|\{#", body):
                n += 1
                try:
                    env.parse(body)
                except TemplateSyntaxError as ex:
                    bad.append(f"{f.name}:{t[:s].count(chr(10)) + 2} {ex.message[:60]}")
    return not bad and n >= 10, f"{n} template snippets parsed with Jinja2's own parser; syntax errors: {bad or 'none'}"


def jinja_expression_facts():
    if not need("jinja2"):
        return None
    from jinja2 import Template, TemplateSyntaxError
    name_on_str = Template("Hello, {{ user.name }}!").render(user="Alice")
    try:
        Template("{{ [x for x in items] }}")
        comp = True
    except TemplateSyntaxError:
        comp = False
    t = note("3-4-jinja2.md")
    bad = has(t, r"For example, Jinja2 uses `and`, `or`, `not`")
    good = has(t, r"list comprehension") and not has(t, r'\{% if user == "Alice" %\}')
    return name_on_str == "Hello, !" and not comp and not bad and good, (
        f"`user.name` on the STRING 'Alice' renders {name_on_str!r} (a str has no .name), so the old example could not print 'Hello, Alice!'; list comprehensions are a TemplateSyntaxError ({not comp}) -- "
        f"a better example than 'and/or/not' (which Python has too); note fixed: {good and not bad}")


def jinja_default_filter():
    if not need("jinja2"):
        return None
    from jinja2 import Template
    r = Template('{{ a|default("x") }}|{{ b|default("x") }}|{{ c|default("x", true) }}|{{ d|default("x", true) }}|{{ e|default("x") }}').render(a=0, b="", c="", d=False)
    t = note("3-4-jinja2.md")
    good = has(t, r"default\(.{0,20}, ?true\)") and not has(t, r"if the variable is undefined or false")
    return r == "0||x|x|x" and good, f"default('x') only replaces UNDEFINED values (0 and '' stay: '{r}'); default('x', true) also replaces falsy ones; note fixed: {good}"


def jinja_loops():
    if not need("jinja2"):
        return None
    from jinja2 import Environment, Template, TemplateSyntaxError
    try:
        Template("{% for i in x %}{% break %}{% endfor %}")
        plain = "works"
    except TemplateSyntaxError:
        plain = "TemplateSyntaxError"
    ext = Environment(extensions=["jinja2.ext.loopcontrols"]).from_string("{% for i in x %}{% if i == 2 %}{% break %}{% endif %}{{ i }}{% endfor %}").render(x=[1, 2, 3])
    filt = Template("{% for i in x if i != 2 %}{{ i }}{% endfor %}").render(x=[1, 2, 3])
    t = note("3-4-jinja2.md")
    good = has(t, r"loopcontrols") and not has(t, r"does not support `break` or `continue` statements\.")
    return plain == "TemplateSyntaxError" and ext == "1" and filt == "13" and good, f"{{% break %}} without the extension -> {plain}; with jinja2.ext.loopcontrols -> {ext!r}; `for ... if` filters instead ({filt!r}); note mentions the extension: {good}"


def jinja_scopes():
    if not need("jinja2"):
        return None
    from jinja2 import Template
    gotcha = Template("{% set x = 10 %}{% for i in range(5) %}{% set x = x + i %}{% endfor %}{{ x }}").render()
    ns = Template("{% set n = namespace(t=0) %}{% for i in range(5) %}{% set n.t = n.t + i %}{% endfor %}{{ n.t }}").render()
    wth = Template("{% with d = 1 %}{{ d }}{% endwith %}[{{ d }}]{# not in output #}").render()
    macro = Template('{% set g = "Hello" %}{% macro m(n) %}{{ g }}, {{ n }}!{% endmacro %}{{ m("A") }}').render()
    t = note("3-4-jinja2.md")
    good = has(t, r"x \+ i") and not has(t, r"set x = i`? statement") and not re.search(r"Discount outside block: \$</p>\s*\{#", t)
    return gotcha == "10" and ns == "10" and wth == "1[]" and macro == "Hello, A!" and good, (
        f"`set` inside a loop does not change the outer variable (x stays {gotcha}); namespace(t=0) accumulates (0+1+2+3+4 = {ns}); `with` variable is gone after endwith and the {{# #}} comment never reaches the output ({wth!r}); "
        f"a macro can read a top-level `set` ({macro!r}); note's explanation says `x + i` and its output no longer shows the comment: {good}")


def jinja_whitespace():
    if not need("jinja2"):
        return None
    from jinja2 import Template
    left = Template("\n  {%- if user %}\n    <h1>Hi</h1>\n  {%- endif %}\n").render(user=1)
    both = Template("\n  {%- if user -%}\n    <h1>Hi</h1>\n  {%- endif -%}\n  after").render(user=1)
    t = note("3-4-jinja2.md")
    good = has(t, r"(left|before).{0,160}(only|but not)|only .{0,80}before") and not has(t, r"This trims whitespace before and after the tags\.")
    return left == "\n    <h1>Hi</h1>" and both == "<h1>Hi</h1>after" and good, (
        f"`{{%- ... %}}` strips whitespace BEFORE the tag only ({left!r}: the newline+indent after the tag stays); adding `-%}}` strips after it too ({both!r}); note says so: {good}")


def jinja_loader_needed():
    if not need("jinja2"):
        return None
    from jinja2 import DictLoader, Environment, Template
    errs = []
    for src in ('{% extends "base.html" %}', '{% include "h.html" %}'):
        try:
            Template(src).render()
            errs.append("worked")
        except TypeError as ex:
            errs.append(str(ex))
    base = "<main>{% block content %}<p>Default</p>{% endblock %}</main>"
    env = Environment(loader=DictLoader({"base.html": base, "child.html": '{% extends "base.html" %}{% block content %}{{ super() }}<p>extra</p>{% endblock %}',
                                         "f.html": "&copy; {{ year }}"}))
    sup = env.get_template("child.html").render()
    inc = (env.from_string('{% include "f.html" %}|{% include "f.html" without context %}').render(year=2024))
    env_i = Environment(loader=DictLoader({"m.html": "{% macro show() %}[{{ who }}]{% endmacro %}"}))
    imp = (env_i.from_string('{% from "m.html" import show %}{{ show() }}').render(who="A") + env_i.from_string('{% from "m.html" import show with context %}{{ show() }}').render(who="A"))
    t = note("3-4-jinja2.md")
    good = has(t, r"DictLoader") and has(t, r"no loader") and not has(t, r"open\(\"base\.html\"\)") and has(t, r"super\(\).{0,160}(position|where)") and not has(t, r"prepend the base content")
    return all("no loader" in e for e in errs) and sup == "<main><p>Default</p><p>extra</p></main>" and inc == "&copy; 2024|&copy; " and imp == "[][A]" and good, (
        f"`Template(...)` has no loader, so extends/include fail ({errs[0]}); with Environment(loader=DictLoader(...)) extends + super() gives {sup!r}; include shares the context by default, `without context` drops it ({inc!r}); import does NOT get the context unless `with context` ({imp!r}); "
        f"note uses DictLoader, says what super() does, and no longer reads files that do not exist: {good}")


def jinja_autoescape_and_safety():
    if not need("jinja2"):
        return None
    from jinja2 import Template
    from jinja2.exceptions import SecurityError
    from jinja2.sandbox import SandboxedEnvironment
    raw = Template("{{ x }}").render(x="<b>&")
    esc = Template("{{ x }}", autoescape=True).render(x="<b>&")
    manual = Template("{{ x|e }}|{{ x|safe }}", autoescape=True).render(x="<b>")
    plain_ssti = Template("{{ ''.__class__.__mro__[1].__subclasses__()|length > 10 }}").render()
    try:
        SandboxedEnvironment().from_string("{{ ''.__class__.__mro__ }}").render()
        sandbox = "allowed"
    except SecurityError:
        sandbox = "SecurityError"
    try:
        Template("{{ user.name }}").render()
        undef_attr = "printed"
    except Exception as ex:
        undef_attr = type(ex).__name__
    t = note("3-4-jinja2.md")
    good = (has(t, r"autoescape") and has(t, r"SandboxedEnvironment") and has(t, r"UndefinedError") and has(t, r"\|safe")
            and not has(t, r"\| Escaping & Safety \| Yes \(auto-escaping, sandboxing\)"))
    return raw == "<b>&" and esc == "&lt;b&gt;&amp;" and manual == "&lt;b&gt;|<b>" and plain_ssti == "True" and sandbox == "SecurityError" and undef_attr == "UndefinedError" and good, (
        f"plain Template does NOT escape ({raw!r}); autoescape=True -> {esc!r}; |e / |safe -> {manual!r}; a plain template can walk ''.__class__.__mro__ (user-written templates are dangerous: {plain_ssti}); "
        f"SandboxedEnvironment blocks it ({sandbox}); `{{{{ user.name }}}}` with `user` undefined raises {undef_attr} while `{{{{ missing }}}}` prints nothing; "
        f"note covers autoescape, |safe, sandbox, UndefinedError and the table says autoescaping is opt-in: {good}")


def flask_autoescape():
    if not need("flask"):
        return None
    from flask import Flask, render_template_string
    app = Flask(__name__)
    with app.test_request_context():
        s = render_template_string("{{ x }}", x="<b>")
    f = app.jinja_env.autoescape
    html_on, txt_on = f("page.html"), f("page.txt")
    others = all(f(n) for n in ("a.htm", "a.xml", "a.xhtml"))
    t = note("3-4-jinja2.md")
    return s == "&lt;b&gt;" and html_on and others and not txt_on and has(t, r"Flask.{0,120}autoescap|autoescap.{0,160}Flask"), (
        f"Flask enables autoescaping: render_template_string -> {s!r}; for 'page.html' {bool(html_on)}, for 'page.txt' {bool(txt_on)}; note says Flask turns it on: {has(t, r'Flask.{0,120}autoescap|autoescap.{0,160}Flask')}")


def jinja_groupby_and_misc():
    if not need("jinja2"):
        return None
    from jinja2 import Template
    s = Template("{% for k, items in p|groupby('k') %}{{ k }}{% endfor %}").render(p=[{"k": "b"}, {"k": "a"}, {"k": "b"}])
    gl = Template("{% for g in p|groupby('k') %}{{ g.grouper }}={{ g.list|length }} {% endfor %}").render(p=[{"k": "b"}, {"k": "a"}, {"k": "b"}])
    loop = Template("{% for i in x %}{{ loop.index }}{{ loop.index0 }}{{ loop.revindex }}{{ loop.revindex0 }}{{ loop.first }}{{ loop.last }}{{ loop.length }}|{% endfor %}").render(x="ab")
    raw = Template("{% raw %}{{ 2+3 }}{% endraw %}").render()
    undefined_ok = Template("[{{ missing }}]").render() == "[]"
    t = note("3-4-jinja2.md")
    good = has(t, r"groupby.{0,200}sort")
    return s == "ab" and gl == "a=1 b=2 " and loop == "1021TrueFalse2|2110FalseTrue2|" and raw == "{{ 2+3 }}" and undefined_ok and good, (
        f"groupby sorts the groups by the key ({s!r}); .grouper/.list work ({gl!r}); loop.index/index0/revindex/revindex0/first/last/length for 'ab' -> {loop!r}; {{% raw %}} -> {raw!r}; note says groupby sorts: {good}")


def jinja_table_text():
    t = note("3-4-jinja2.md")
    bad = [p for p in (r"No parameters, static inclusion", r"Example #7\b.*Example #7\b", r"^</div>\s*$", r"\{\{#") if has(t, p, re.M | re.S | re.I)]
    return not bad, f"wrong/stale statements still present (static inclusion, duplicate 'Example #7', stray </div>, '{{{{#'): {bad or 'none'}"


# --------------------------------------------------------------------------- #
# markdown / GitHub hygiene (as for the other weeks)
# --------------------------------------------------------------------------- #
def no_vitepress_syntax():
    found = []
    for f in md_files():
        for i, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if re.match(r"^\s*:::|^\s*== ?\S|^\s*```\s*\w+\s*\[", line) or re.search(r"</?[A-Z][\w-]*[^>]*/?>", re.sub(r"`[^`]*`", "", line)) and not re.search(r"<(!DOCTYPE)", line):
                if re.search(r"<[A-Z][\w-]*[^>]*/>|^\s*:::|^\s*== ?\S|^\s*```\s*\w+\s*\[", line):
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
        raw = f.read_text(encoding="utf-8")
        text = re.sub(r"```.*?```", "", raw, flags=re.S)
        for m in re.finditer(r"!?\[[^\]]*\]\(([^)\s]+)\)", text):
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


def mislabelled_fences():
    bad = []
    for f in md_files():
        t = f.read_text(encoding="utf-8")
        for lang, body, s, e in blocks(t):
            if lang == "python" and re.match(r"\s*\{%", body):
                bad.append(f"{f.name}:{t[:s].count(chr(10)) + 2}: Jinja template in a ```python fence")
    return not bad, f"template code labelled as python: {bad or 'none'}"


# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    P, F, S, J = "3-1-pyhtml-sys.md", "3-2-string-formatting.md", "3-3-string-templating.md", "3-4-jinja2.md"
    print("=" * 78 + "\nWeek 3 claim checker\n" + "=" * 78 + "\n")
    for fname, exact, libs in ((P, True, ("pyhtml",)), (F, False, ()), (S, False, ()), (J, False, ("jinja2",))):
        r = examples_check(fname, exact, libs)
        if r is not None:
            check(fname, "every python example runs and prints exactly what the note shows", lambda r=r: r)
    check(P, "sys.argv[0] as typed / -c; the shell splits and expands; SystemExit; version_info", sys_argv0)
    for c, fn in ((P, pyhtml_api),):
        r = fn()
        if r is not None:
            check(c, "pyhtml: tag(attrs)(children), DOCTYPE, one text per line, escaping by default", lambda r=r: r)
    check(F, "%-formatting: strict types (but %d truncates floats), no attribute access", percent_facts)
    check(F, "str.format: attributes/items yes, expressions no; a user-controlled TEMPLATE leaks data, a user VALUE does not", format_facts)
    check(F, "f-strings: user text inserted as a value is never executed; the template can't come from a user", fstring_facts)
    check(F, "f-strings are faster than % and str.format", speed_claim)
    check(F, "no typos / broken relative links", formatting_table_text)
    check(S, "string.Template: braces only to end a name, ValueError, no format specs, no attribute access", template_facts)
    check(S, "a user-written string.Template can only read the names you pass in", template_user_templates)
    for c, fn, claim in ((J, jinja_template_parse, "every template snippet parses with Jinja2's parser (no '{{# #}}')"),
                         (J, jinja_expression_facts, "`user.name` on a str prints nothing; list comprehensions are unsupported"),
                         (J, jinja_default_filter, "default() replaces only undefined values unless boolean=true"),
                         (J, jinja_loops, "break/continue need jinja2.ext.loopcontrols"),
                         (J, jinja_scopes, "set/with/namespace/macro scoping, comment not in output"),
                         (J, jinja_whitespace, "`{%-` strips before the tag only; `-%}` after"),
                         (J, jinja_loader_needed, "extends/include need a loader (DictLoader); super(); include context rules"),
                         (J, jinja_autoescape_and_safety, "autoescape is opt-in; |e / |safe; sandbox; UndefinedError on attribute of undefined"),
                         (J, flask_autoescape, "Flask turns autoescaping on for HTML templates"),
                         (J, jinja_groupby_and_misc, "groupby sorts; loop.* variables; raw")):
        r = fn()
        if r is not None:
            check(c, claim, lambda r=r: r)
    check(J, "no stale/wrong statements in the tables and examples", jinja_table_text)
    check("week3/*.md", "Jinja templates are not labelled as python", mislabelled_fences)
    check("week3/*.md", "no VitePress-only syntax (:::, ==, ```lang[label], Vue components)", no_vitepress_syntax)
    check("week3/*.md", "no HTML that GitHub strips (style=, class=, &emsp;) outside code blocks", no_stripped_html)
    check("week3/*.md", "GitHub alerts written correctly", alerts_valid)
    check("week3/*.md", "<details> balanced, no backticks in <summary>", details_balanced)
    check("week3/*.md", "every local link, #anchor and image resolves", links_resolve)
    check("week3/*.md", "code fences are labelled/closed cleanly", fences_clean)

    wrong = [f for ok, f in RESULTS if not ok]
    print("=" * 78)
    print(f"{len(RESULTS)} checks, {len(RESULTS) - len(wrong)} OK, {len(wrong)} WRONG")
    if wrong:
        print("files with WRONG statements:", ", ".join(sorted(set(wrong))))
    print("\nNOT VERIFIABLE HERE (kept because they are standard, but not executed):")
    for s in sorted(set(SKIPPED)) + [
        "str.format() was introduced in Python 2.6 (empty {} placeholders in 2.7) and string.Template in 2.4: needs old interpreters / the docs",
        "t-strings (PEP 750, Python 3.14): this checker runs on 3.13",
        "docs.python.org / realpython / geeksforgeeks / jinja.palletsprojects.com / PyPI links (blocked from this sandbox)",
        "popularity / community-size / documentation-quality rows of the pyhtml-vs-jinja2 table (opinions, not executable)",
    ]:
        print("  -", s)
    sys.exit(1 if wrong else 0)
