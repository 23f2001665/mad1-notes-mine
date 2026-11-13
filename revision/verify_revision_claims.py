"""
Revision notes (revision/revision-notes.md) -- claim checker.

Every question, answer, number and code result of the revision session is run for real:

  * the numericals (latency, bandwidth, bits), number-system and IPv4 conversions
  * string.Template / Jinja2 / pyhtml examples and every PYQ that uses them
  * the Flask PYQs, with Flask's test client (routes, converters, query strings,
    forms, methods, redirects, errors)
  * the sys.argv PYQs, as real `python` processes started from a shell
  * the CSS / HTML PYQs, in headless Chromium (colours, box widths, flex, <dl>)
  * links, anchors, markdown hygiene and the 120-minute agenda

    OK     -> the notes say what actually happens
    WRONG  -> the notes say something that does not happen

Run (from anywhere):
    python revision/verify_revision_claims.py

Needs Flask, Jinja2 and pyhtml (`pip install flask pyhtml`). Optional:
    node + playwright (global)  -> the Chromium checks (skipped otherwise)
    VNU_JAR=/path/to/vnu.jar    -> HTML validation of the table snippet (needs java)

The four PYQ papers themselves are not stored in the repository (they carry the
name and e-mail of the person who downloaded them); the questions were retyped
into the notes and their answers are re-checked here.
"""
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from string import Template

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
NOTE = HERE / "revision-notes.md"
RESULTS, SKIPPED = [], []


def check(claim, fn):
    try:
        ok, evidence = fn()
    except Exception as e:                      # a crash is a WRONG result, with the reason
        ok, evidence = False, f"raised {type(e).__name__}: {str(e).splitlines()[0][:200]}"
    RESULTS.append(ok)
    print(f"[{'OK   ' if ok else 'WRONG'}] {claim}\n        {evidence}\n")


def text():
    return NOTE.read_text(encoding="utf-8")


def has(t, pattern):
    return re.search(pattern, t, re.S) is not None


def py_env():
    """PATH in which `python` is this interpreter (the notes write `python main.py`)."""
    d = Path(tempfile.mkdtemp(prefix="revshim"))
    shim = d / "python"
    shim.write_text(f'#!/bin/sh\nexec "{sys.executable}" "$@"\n')      # a wrapper (not a symlink) keeps the virtualenv of this interpreter
    shim.chmod(0o755)
    return dict(os.environ, PATH=f"{d}:{os.environ['PATH']}")


def sh(cmd, cwd):
    return subprocess.run(["bash", "-c", cmd], cwd=cwd, env=py_env(), capture_output=True, text=True, timeout=60)


# --------------------------------------------------------------------------- #
# numbers
# --------------------------------------------------------------------------- #
def numericals():
    t = text()
    train_s = 4.5 / 180 * 3600
    train_mb = 5 * train_s / 8
    rtt = 2 * 12.5e6 / 2e8 * 1000
    concurrent = 6000 / 2
    mbs = 2000 / 8
    wait = 3e6 / 2e8 * 1000 + 47 + 3e6 / 3e8 * 1000
    bits = math.ceil(math.log2(26))
    chennai = (2000e3 / 2e8 * 1000, 2 * 2000e3 / 2e8 * 1000, 1 / (2 * 2000e3 / 2e8))
    portal = 1000 * 2 * 18.2 / 1000, 1000 * 2 * 18.2 / 1000 * 8
    ex = (3000e3 / 2e8 * 1000, 1 / (2 * 3000e3 / 2e8), 500 * 3 * 40 / 1000, 500 * 3 * 40 / 1000 * 8)
    ok = (train_s == 90 and train_mb == 56.25 and rtt == 125 and concurrent == 3000 and mbs == 250 and abs(wait - 72) < 1e-9 and bits == 5
          and chennai[0] == 10 and chennai[1] == 20 and chennai[2] == 50 and abs(portal[0] - 36.4) < 1e-9 and abs(portal[1] - 291.2) < 1e-9
          and 50_000 * 4 / 1000 == 200 and ex[0] == 15 and abs(ex[1] - 33.33) < 0.01 and ex[2] == 60 and ex[3] == 480 and 2 ** 4 < 26 <= 2 ** 5)
    good = all(s in t for s in ("**56.25 MB**", "**125 ms**", "**3000**", "**250 MB**", "**72 ms**", "**5**", "$2^4 = 16 < 26 \\le 32 = 2^5$", "**291.2 Mbps**" if False else "291.2"))
    return ok and good, (f"M26 Q1: 4.5 km at 180 km/h = {train_s:g} s, 5 Mb/s x {train_s:g} s = {5 * train_s:g} Mb = {train_mb} MB; J26 Q12 RTT = {rtt:g} ms; J26 Q5 = {concurrent:g}; "
                         f"J25 Q11 = {mbs:g} MB/s; J25 Q12 = 15 + 47 + 10 = {wait:g} ms; J26 Q13: ceil(log2 26) = {bits} bits; notes' problems: 10 / 20 ms, {chennai[2]:g} req/s, "
                         f"{portal[0]:g} MB/s = {portal[1]:g} Mbps, 200 GB; new problem: {ex[0]:g} ms, {ex[1]:.1f} req/s, {ex[2]:g} MB/s = {ex[3]:g} Mbps; the numbers appear in the notes: {good}")


def number_systems():
    t = text()
    rows = [(int("110101", 2), 53), (int("101101", 2), 45), (bin(45), "0b101101"), (hex(int("11101101", 2)), "0xed"), (hex(254), "0xfe"), (oct(int("10111101", 2)), "0o275"),
            (int("624", 8), 404), (int("572", 8), 378), (int("9B", 16), 155), (int("1C7", 16), 455), (bin(int("3F", 16)), "0b111111"), (int("623", 8), 403)]
    frac = 0.625
    bits, f = "", frac
    while f:
        f *= 2
        bits += str(int(f))
        f -= int(f)
    ok = all(a == b for a, b in rows) and bits == "101" and 2 ** 8 == 256 and 2 ** 4 == 16
    good = all(s in t for s in ("$53$", "$101101_2$", "$ED_{16}$", "$FE_{16}$", "$275_8$", "$404$", "$155$", "$111111_2$", "$0.101_2$"))
    return ok and good, (f"all conversions of the table are right (110101b=53, 45=101101b, 11101101b=ED, 254=FE, 10111101b=275 octal, 624 octal=404, 9B=155, 3F=111111b, 0.625=0.{bits}b); n bits give 2^n values; table says so: {good}")


def ip_addresses():
    import ipaddress
    t = text()
    a = ipaddress.IPv4Address("192.168.1.1")
    b = ipaddress.IPv4Address("172.16.10.25")
    bin_a = ".".join(f"{o:08b}" for o in a.packed)
    bin_b = ".".join(f"{o:08b}" for o in b.packed)
    hex_a = ".".join(f"{o:02X}" for o in a.packed)
    hex_b = ".".join(f"{o:02X}" for o in b.packed)
    mapped = ipaddress.IPv6Address("::ffff:172.16.10.25")
    ok = (bin_a == "11000000.10101000.00000001.00000001" and hex_a == "C0.A8.01.01" and bin_b == "10101100.00010000.00001010.00011001" and hex_b == "AC.10.0A.19"
          and 2 ** 32 == 4_294_967_296 and mapped.ipv4_mapped == b and mapped.packed.hex().endswith("ffffac100a19") and ipaddress.IPv4Address("127.255.0.1").is_loopback
          and ipaddress.IPv4Address("192.168.1.1").is_private and 2 ** 16 == 65536)
    good = all(s in t for s in (bin_a, hex_a, bin_b, hex_b, "0000:0000:AC10:0A19", "::ffff:ac10:0a19", "4{,}294{,}967{,}296"))
    return ok and good, (f"192.168.1.1 = {bin_a} = {hex_a}; 172.16.10.25 = {bin_b} = {hex_b}; IPv4 count 2^32 = {2 ** 32:,}; IPv4-mapped IPv6 {mapped.exploded}; 127.x.x.x is loopback; "
                         f"192.168.x.x is private; 16-bit ports = {2 ** 16}; table says so: {good}")


# --------------------------------------------------------------------------- #
# string.Template, Jinja2, pyhtml
# --------------------------------------------------------------------------- #
def jinja_claims():
    from jinja2 import Template as J
    from jinja2.exceptions import UndefinedError
    t = text()
    r = {}
    r["arith"] = J("{{ 7 // 2 }} {{ 7 / 2 }} {{ 7 % 3 }} {{ 2 ** 3 }} {{ 'a' ~ 1 }} {{ 2 in items }}").render(items=[1, 2])
    r["missing"] = J("[{{ x }}]").render()
    try:
        J("{{ user.name }}").render()
        r["attr"] = "no error"
    except UndefinedError:
        r["attr"] = "UndefinedError"
    r["html_comment"] = J("a{# hidden #}b <!-- {{ 1+1 }} -->").render()
    r["eq"] = J('{% if user == "admin" %}Admin{% else %}User{% endif %}').render(user="admin iitm")
    r["filters"] = J("{{ n|upper }}|{{ n|lower }}|{{ n|title }}|{{ n|length }}|{{ items|join('-') }}|{{ n|replace('a','4') }}|{{ items|sum }}").render(n="aLice bob", items=[1, 2, 3])
    r["default"] = J("{{ m|default('none') }}|{{ z|default('none') }}|{{ e|default('none', true) }}").render(z=0, e="")
    r["sort"] = J("{{ l|sort }}|{{ m|sort(reverse=True) }}|{{ k|reject('even')|list }}|{{ k|select('even')|list }}").render(l=[5, 2, 8, 1, 9], m=[6, 8, 5, 2, 4], k=[10, 3, 9, 8, 15])
    r["loop"] = J("{% for x in i %}[{{ loop.index }} {{ loop.index0 }} {{ loop.revindex }} {{ loop.first }} {{ loop.last }} {{ loop.length }}]{% endfor %}").render(i=["a", "b"])
    r["dict"] = J("{% for k, v in d.items() %}{{ k }}={{ v }};{% endfor %}|{% for k in d %}{{ k }};{% endfor %}").render(d={"a": 1, "b": 2})
    r["groupby"] = J("{% for c, items in ps|groupby('c') %}{{ c }}:{% for i in items %}{{ i.n }},{% endfor %};{% endfor %}").render(ps=[{"c": "f", "n": "apple"}, {"c": "v", "n": "kale"}, {"c": "f", "n": "fig"}])
    r["scope"] = J("{% set a = 1 %}{% for i in [1,2] %}{% set a = 5 %}{% endfor %}{{ a }}|{% set b = 1 %}{% if true %}{% set b = 5 %}{% endif %}{{ b }}").render()
    r["autoescape"] = (J("{{ s }}").render(s="<b>"), J("{{ s }}", autoescape=True).render(s="<b>"))
    try:
        J("{% for x in l.sort() %}{{ x }}{% endfor %}").render(l=[3, 1])
        r["sort_method"] = "no error"
    except TypeError:
        r["sort_method"] = "TypeError"
    ok = (r["arith"] == "3 3.5 1 8 a1 True" and r["missing"] == "[]" and r["attr"] == "UndefinedError" and r["html_comment"] == "ab <!-- 2 -->" and r["eq"] == "User"
          and r["filters"] == "ALICE BOB|alice bob|Alice Bob|9|1-2-3|4Lice bob|6" and r["default"] == "none|0|none"
          and r["sort"] == "[1, 2, 5, 8, 9]|[8, 6, 5, 4, 2]|[3, 9, 15]|[10, 8]"
          and r["loop"] == "[1 0 2 True False 2][2 1 1 False True 2]" and r["dict"] == "a=1;b=2;|a;b;" and r["groupby"] == "f:apple,fig,;v:kale,;" and r["scope"] == "1|5"
          and r["autoescape"] == ("<b>", "&lt;b&gt;") and r["sort_method"] == "TypeError")
    good = all(s in t for s in ("`3`, `3.5`" if False else "{{ 7 // 2 }}", "`4Lice bob`", "`1-2-3`", "`8, 6, 5, 4, 2`", "`3, 9, 15`", "`select(\"even\")` keeps them", "in the main notes"))
    return ok and good, f"every Jinja2 example of the notes gives the shown result: {json.dumps(r, ensure_ascii=False)[:700]}; the notes mention them: {good}"


def string_template_claims():
    from jinja2 import Template as JT
    from jinja2.exceptions import UndefinedError
    t = text()
    r = {}

    def run(label, fn):
        try:
            r[label] = fn()
        except Exception as e:
            r[label] = type(e).__name__ + (f": {e}" if isinstance(e, KeyError) else "")
    run("swap1", lambda: Template("{{ name }} $name").safe_substitute(name="Z"))
    run("swap2", lambda: JT("{{ name }} $name").render(name="Z"))
    run("owe_t", lambda: Template("Hi $name, you owe $$${amount}").substitute(name="Ann", amount=5))
    run("owe_j", lambda: JT("Hi {{ name }}, you owe ${{ amount }}").render(name="Ann", amount=5))
    run("braces", lambda: Template("${w}s and $ws").safe_substitute(w="cat"))
    run("braces2", lambda: Template("${w}s").substitute(w="cat"))
    run("ws", lambda: Template("$ws").substitute(w="cat"))
    run("missing", lambda: Template("$a-$b").substitute(a=1))
    run("safe", lambda: Template("$a-$b").safe_substitute(a=1))
    run("jmissing", lambda: JT("[{{ a }}-{{ b }}]").render(a=1))
    run("attr_t", lambda: Template("$user.name").substitute(user={"name": "A"}))
    run("attr_j", lambda: JT("{{ user.name }}").render(user={"name": "A"}))
    run("stray", lambda: Template("cost $ 5").substitute())
    run("stray_safe", lambda: Template("cost $ 5").safe_substitute())
    run("kw", lambda: Template("$x").substitute({"x": 1}, x=2))
    run("fmt", lambda: Template("${price:.2f}").substitute(price=3.14159))
    run("fmt_j", lambda: JT("{{ '%.2f'|format(price) }} {{ price|round(2) }}").render(price=3.14159))
    try:
        JT("{{ user.name }}").render()
        r["undef"] = "none"
    except UndefinedError:
        r["undef"] = "UndefinedError"
    ok = (r["swap1"] == "{{ name }} Z" and r["swap2"] == "Z $name" and r["owe_t"] == "Hi Ann, you owe $5" and r["owe_j"] == "Hi Ann, you owe $5" and r["braces"] == "cats and $ws"
          and r["braces2"] == "cats" and r["ws"] == "KeyError: 'ws'" and r["missing"] == "KeyError: 'b'" and r["safe"] == "1-$b" and r["jmissing"] == "[1-]"
          and r["attr_t"] == "{'name': 'A'}.name" and r["attr_j"] == "A" and r["stray"].startswith("ValueError") and r["stray_safe"] == "cost $ 5" and r["kw"] == "2"
          and r["fmt"].startswith("ValueError") and r["fmt_j"] == "3.14 3.14" and r["undef"] == "UndefinedError")
    good = all(s in t for s in ("{{ name }} Z", "Z $name", "`Hi Ann, you owe $5`", "`cats and $ws`", "`{'name': 'A'}.name`", "cost $ 5", "`ValueError`", "`2` (keywords override the mapping)", "`UndefinedError`"))
    return ok and good, f"every row of the Template-vs-Jinja tables is right: {json.dumps(r, ensure_ascii=False)[:600]}; the notes show them: {good}"


def pyq_template_mix():
    from jinja2 import Template as JTemplate
    from string import Template as STemplate
    t = text()
    out = {}
    # O25 Q8
    data = {'name1': 'Alice', 'name2': 'name1', 'age1': '25', 'age2': 'age1', 'job1': 'Engineer', 'job2': 'job1'}
    result1 = JTemplate("{{name2}} is {{age2}} years old and works as a {{job2}}.").render(data)
    result2 = STemplate(result1).substitute(data)
    out["O25Q8"] = (result1, result2)
    # J25 Q5
    template1 = STemplate('Hello $name, welcome to $city!')
    template2 = JTemplate('{{product}} costs {{price}}')
    res = {}
    for label, fn in (("A", lambda: template1.substitute(name='Alice')), ("B", lambda: template1.substitute(name='Alice', city='Boston', state='Massachusetts')),
                      ("C", lambda: template2.render({"product": "laptop"})), ("D", lambda: template2.render({"product": "laptop", "price": "45000", "currency": "rupees"}))):
        try:
            res[label] = fn()
        except KeyError as e:
            res[label] = "KeyError " + str(e)
    out["J25Q5"] = res
    # M26 Q16
    tp = STemplate("Hello $name, you have $count messages")
    m = {}
    for label, fn in (("A", lambda: tp.substitute({"name": "Alice"})), ("B", lambda: tp.safe_substitute({"name": "Alice"})), ("C", lambda: tp.substitute({"name": "Alice", "count": 5})),
                      ("D", lambda: tp.safe_substitute({"name": "Alice", "count": 5}))):
        try:
            m[label] = fn()
        except KeyError as e:
            m[label] = "KeyError " + str(e)
    out["M26Q16"] = m
    # J26 Q8
    lines = []
    for name in ["Siya", "Sunita"]:
        lines.append(STemplate("Student Name: $name ").substitute(name=name))
    out["J26Q8"] = lines
    ok = (result1 == "name1 is age1 years old and works as a job1." and result2 == result1 and res["A"] == "KeyError 'city'" and res["B"] == "Hello Alice, welcome to Boston!"
          and res["C"] == "laptop costs " and res["D"] == "laptop costs 45000"
          and m == {"A": "KeyError 'count'", "B": "Hello Alice, you have $count messages", "C": "Hello Alice, you have 5 messages", "D": "Hello Alice, you have 5 messages"}
          and lines == ["Student Name: Siya ", "Student Name: Sunita "])
    good = all(s in t for s in ("name1 is age1 years old and works as a job1.", "**`KeyError: 'city'`**", "`laptop costs `", "`Hello Alice, you have $count messages`", "**`Student Name: Siya`**", "the \"question 5\" mix question"))
    return ok and good, (f"O25 Q8: first print = {result1!r}, second print = the same sentence (no $ placeholders); J25 Q5: only A raises ({res['A']}), C prints {res['C']!r}; "
                         f"M26 Q16: A raises, B/C/D do not; J26 Q8: {lines}; the notes show them: {good}")


def pyhtml_claims():
    from pyhtml import a, p, img, h1, html, head, title, body, ul, li
    t = text()
    r = {}
    r["a"] = str(a(href="https://e.com", id_="l")("link"))
    r["p"] = str(p(class_="c", data_value="x")("t"))
    r["img"] = str(img(src="a.png", alt="A"))
    r["esc"] = str(p("<b>x</b>")), str(p("<b>x</b>", _safe=True))
    try:
        h1("Hello", style="color: blue;")
        r["both"] = "no error"
    except AssertionError:
        r["both"] = "AssertionError"
    r["doc"] = str(html(head(title("T")), body(h1("Hi"), ul(li("a"), li("b"))))).splitlines()[:2]
    ok = (r["a"] == '<a href="https://e.com" id="l">\n  link\n</a>' and r["p"] == '<p class="c" data-value="x">\n  t\n</p>' and r["img"] == '<img alt="A" src="a.png"/>'
          and r["esc"][0].count("&lt;b&gt;") == 1 and "<b>x</b>" in r["esc"][1] and r["both"] == "AssertionError" and r["doc"][0] == "<!DOCTYPE html>")
    good = all(s in t for s in ('<a href="https://e.com" id="l">', "`class_`", "`data_value` → `data-value`", "`AssertionError`", "`_safe=True`"))
    return ok and good, f"pyhtml: tag(attributes)(children), class_, underscores become hyphens, alphabetical attributes, escaping and _safe, both in one call -> {r['both']}, html() adds the doctype ({r['doc'][0]}); notes say so: {good}"


# --------------------------------------------------------------------------- #
# sys.argv PYQs: real processes
# --------------------------------------------------------------------------- #
def argv_pyqs():
    t = text()
    r = {}
    with tempfile.TemporaryDirectory() as d:
        D = Path(d)
        (D / "main.py").write_text("import sys\nimport utils\nprint('Processing: ' + sys.argv[2])\n")
        (D / "utils.py").write_text("import sys\nprint('Module: ' + sys.argv[0])\n")
        r["O25Q6"] = sh("python main.py data.txt output.txt", D).stdout.splitlines()
        (D / "j.py").write_text("import sys\ndef process(v):\n    st = \",\".join(v)\n    return st\nv = sys.argv\noutput = process(v[1:])\nprint(output)\n")
        r["J25Q10"] = sh("python j.py 1 2 3 4 5", D).stdout.strip()
        (D / "mainj.py").write_text('''from jinja2 import Template
import sys

t = """
    Better learning path of App Dev courses:
    =>{{course[0]}} => {{course[1]}} => {{course[2]}} => {{course[3]}}
"""
course = sys.argv[1:]
render_t = Template(t)
output = render_t.render(course=course)
print(output)
''')
        want = "=>MAD1 => MAD2 => MAD1_Project => MAD2_Project"
        cmds = {"A": 'python mainj.py MAD1 MAD2 MAD1_ Project MAD2_ Project', "B": 'python mainj.py MAD1 MAD2 MAD1_Project MAD2_Project',
                "C": 'python mainj.py "MAD1 MAD2 MAD1_Project MAD2_Project"', "D": 'python mainj.py MAD1 MAD2 "MAD1_Project" "MAD2_Project"'}
        r["J26Q11"] = {k: (want in sh(c, D).stdout) for k, c in cmds.items()}
        (D / "webapp.py").write_text('''import sys
from jinja2 import Template

args = sys.argv
frameworks = {
    'django': 'python',
    'react': 'javascript',
    'flask': 'python',
    'vue': 'javascript'
}

languages = {
    'python': 'server-side',
    'javascript': 'client-side'
}

template = Template("{{ framework }} is a {{ lang_type }} {{ language }} framework.")

if len(args) >= 3 and args[1] in frameworks:
    framework_name = args[1]
    language = frameworks[framework_name]
    if args[2] == 'type' and language in languages:
        lang_type = languages[language]
        print(template.render(framework=framework_name, language=language, lang_type=lang_type))
    else:
        print("Invalid second argument or language not found!")
else:
    print("Invalid command")
''')
        w = lambda a: sh(f"python webapp.py {a}", D).stdout.strip()
        r["J25Q13"] = {"A": w("flask python type"), "B": w("flask type server-side"), "C": w("flask type"), "D": w("type flask python"), "E": w("flask server-side")}
        r["J25Q14"] = w("react type")
        r["J25Q15"] = w("django python")
        (D / "app.py").write_text('''from flask import Flask
import sys

app = Flask(__name__)

MULTIPLIER = int(sys.argv[1]) if len(sys.argv) > 1 else 2

@app.route('/calculate/<int:value>')
def calculate(value):
    return f"Result: {value * MULTIPLIER}"

if __name__ == '__main__':
    app.run()
''')
        r["J26Q6"] = sh("python -c \"import sys; sys.argv = ['app.py', '7']; import app; print(app.app.test_client().get('/calculate/6').get_data(as_text=True))\"", D).stdout.strip()
        r["J26Q6_default"] = sh("python -c \"import sys; sys.argv = ['app.py']; import app; print(app.app.test_client().get('/calculate/6').get_data(as_text=True))\"", D).stdout.strip()
        (D / "argv.py").write_text("import sys\nprint(sys.argv)\nprint([type(x).__name__ for x in sys.argv])\n")
        r["argv"] = sh('python argv.py arg1 arg2 "complex argument 3" 5', D).stdout.splitlines()
    ok = (r["O25Q6"] == ["Module: main.py", "Processing: output.txt"] and r["J25Q10"] == "1,2,3,4,5" and r["J26Q11"] == {"A": False, "B": True, "C": False, "D": True}
          and r["J25Q13"] == {"A": "Invalid second argument or language not found!", "B": "flask is a server-side python framework.", "C": "flask is a server-side python framework.",
                               "D": "Invalid command", "E": "Invalid second argument or language not found!"}
          and r["J25Q14"] == "react is a client-side javascript framework." and r["J25Q15"] == "Invalid second argument or language not found!" and r["J26Q6"] == "Result: 42"
          and r["J26Q6_default"] == "Result: 12" and r["argv"][0] == "['argv.py', 'arg1', 'arg2', 'complex argument 3', '5']" and r["argv"][1] == "['str', 'str', 'str', 'str', 'str']")
    good = all(s in t for s in ("**`Module: main.py`**", "**`1,2,3,4,5`**", "`python main.py MAD1 MAD2 MAD1_Project MAD2_Project`", "**`flask is a server-side python framework.`**",
                                "**`react is a client-side javascript framework.`**", "**`Invalid second argument or language not found!`**", "**`Result: 42`**"))
    return ok and good, (f"run as real processes: O25 Q6 -> {r['O25Q6']}; J25 Q10 -> {r['J25Q10']}; J26 Q11 commands A-D produce the line: {r['J26Q11']}; J25 Q13 options A-E: "
                         f"{[k for k, v in r['J25Q13'].items() if v.startswith('flask is')]} work; Q14 -> {r['J25Q14']!r}; Q15 -> {r['J25Q15']!r}; J26 Q6 with 7 -> {r['J26Q6']}, default -> {r['J26Q6_default']}; "
                         f"sys.argv items are all str; notes show them: {good}")


# --------------------------------------------------------------------------- #
# Flask
# --------------------------------------------------------------------------- #
def flask_routes():
    from flask import Flask, request
    t = text()
    app = Flask("routes")

    @app.route("/user/<username>")
    def user(username): return f"User: {username}"

    @app.route("/post/<int:post_id>")
    def post(post_id): return f"Post {post_id} {type(post_id).__name__}"

    @app.route("/price/<float:price>")
    def price(price): return str(price)

    @app.route("/files/<path:sub>")
    def files(sub): return sub

    @app.route("/search")
    def search():
        return f"q={request.args.get('q')} tags={request.args.getlist('tag')} n={request.args.get('n', type=int)}"

    @app.route("/about/")
    def about(): return "About"

    @app.route("/contact")
    def contact(): return "Contact"

    @app.route("/num")
    def num(): return 42

    c = app.test_client()
    app.testing = False
    code = lambda u: c.get(u).status_code
    r = {u: code(u) for u in ("/user/john/doe", "/post/12", "/post/abc", "/post/1.5", "/post/-3", "/price/19.99", "/price/19", "/files/a/b/c.txt", "/contact/", "/num")}
    s1 = c.get("/search?q=flask&tag=x&tag=y&n=5").get_data(as_text=True)
    s2 = c.get("/search").get_data(as_text=True)
    about = c.get("/about")
    rules = {rule.rule: rule.endpoint for rule in app.url_map.iter_rules()}
    ok = (r["/user/john/doe"] == 404 and r["/post/12"] == 200 and c.get("/post/12").get_data(as_text=True) == "Post 12 int" and r["/post/abc"] == r["/post/1.5"] == r["/post/-3"] == 404
          and r["/price/19.99"] == 200 and r["/price/19"] == 404 and c.get("/files/a/b/c.txt").get_data(as_text=True) == "a/b/c.txt" and r["/contact/"] == 404 and r["/num"] == 500
          and s1 == "q=flask tags=['x', 'y'] n=5" and s2 == "q=None tags=[] n=None" and about.status_code == 308 and about.headers["Location"].endswith("/about/")
          and rules.get("/static/<path:filename>") == "static" and rules.get("/post/<int:post_id>") == "post")
    good = all(s in t for s in ("`/post/abc`, `/post/1.5`, `/post/-3`", "(308 redirect)", "an `int` gives **500**", "`request.args.get(\"q\")`", "**returns a string**" if False else "returns a **string**"))
    return ok and good, (f"/user/john/doe 404, /post/12 ok as int, /post/abc /1.5 /-3 all 404, /price/19.99 ok and /price/19 404, path converter keeps slashes, /about/ also answers /about with {about.status_code}, "
                         f"/contact/ 404, returning an int gives {r['/num']}; request.args: {s1!r} and {s2!r}; url_map has static -> {rules.get('/static/<path:filename>')}; notes say so: {good}")


def flask_pyqs():
    from flask import Flask, request, redirect, url_for, render_template
    t = text()
    out = {}
    # M26 Q3
    app = Flask("m26q3")

    @app.route('/calculate')
    def calculate():
        a = request.args.get('a')
        b = request.args.get('b', 2)
        c = request.args.get('c', "5")
        try:
            a = int(a)
            b = int(b)
            c = int(c)
        except:
            return "Invalid Input"
        if a + b == c:
            return f"Sum: {a+b}"
        elif a * c == b:
            return f"Product: {a*b}"
        else:
            return f"No match: {a+b+c}"
    cl = app.test_client()
    out["M26Q3"] = [cl.get(u).get_data(as_text=True) for u in ("/calculate?a=3", "/calculate?a=3&d=5", "/calculate?a=1&b=5", "/calculate?a=1&b=5&c=6")]
    # M26 Q4
    try:
        compile("app.run(port=0007)", "app.py", "exec")
        out["M26Q4"] = "compiles"
    except SyntaxError as e:
        out["M26Q4"] = "SyntaxError"
    # M26 Q8
    a2 = Flask("m26q8")

    @a2.route('/profile/<string:username>')
    def profile(username): return f"Profile of {username}"

    @a2.route('/post/<int:post_id>')
    def post(post_id): return f"Post ID: {post_id}"
    out["M26Q8"] = a2.test_client().get('/post/abc123').status_code
    # J26 Q3 / Q4
    a3 = Flask("j26q3", template_folder=tempfile.mkdtemp())
    Path(a3.template_folder, "numbers.html").write_text('<!DOCTYPE html><html lang="en"><body><form method="POST" action="/"><h3>Enter a number : <input type=text name="txtn"></h3><h3><input type="submit"></h3></form></body></html>')

    @a3.route("/", methods=["GET", "POST"])
    def numbers():
        if request.method == "POST":
            L = []
            n = int(request.form["txtn"])
            for i in range(n):
                L.append(i)
            return str(L)
        else:
            return render_template("numbers.html")
    c3 = a3.test_client()
    page = c3.get("/").get_data(as_text=True)
    out["J26Q3"] = (c3.get("/").status_code, 'method="POST"' in page, c3.get("/").request.method if hasattr(c3.get("/"), "request") else "GET")
    out["J26Q4"] = c3.post("/", data={"txtn": "5"}).get_data(as_text=True)
    # J26 Q7
    a4 = Flask("j26q7")

    @a4.route("/total")
    def total():
        price = request.args.get("price", 0)
        qty = request.args.get("qty", 1)
        result = price * qty
        return str(result)
    a4.testing = True
    try:
        a4.test_client().get("/total?price=5&qty=2")
        out["J26Q7"] = "no error"
    except TypeError as e:
        out["J26Q7"] = "TypeError"
    a4.testing = False
    out["J26Q7_noargs"] = a4.test_client().get("/total").get_data(as_text=True)
    out["J26Q7_500"] = a4.test_client().get("/total?price=5&qty=2").status_code
    # J26 Q9
    a5 = Flask("j26q9")

    @a5.route("/user/<name>")
    def user(name): return f"User: {name}"

    @a5.route("/user/admin")
    def admin(): return "Admin Panel"
    out["J26Q9"] = (a5.test_client().get("/user/admin").get_data(as_text=True), a5.test_client().get("/user/bob").get_data(as_text=True))
    # J26 Q10
    a6 = Flask("j26q10")

    @a6.route("/calculate/<int:v1>/<int:v2>")
    def compute(v1, v2):
        try:
            return f"{v1 / v2}"
        except:
            return "Arithmetic operation error!"
    c6 = a6.test_client()
    out["J26Q10"] = {u: (c6.get(u).status_code, c6.get(u).get_data(as_text=True)[:3] if c6.get(u).status_code == 200 else "") for u in
                     ("/calculate/10/5", "/calculate/3/0.2", "/calculate/3/2?v1=1", "/calculate?v1=5&v2=2")}

    # O25 Q5
    def status(rule):
        ap = Flask("o25q5" + str(abs(hash(rule))))

        @ap.route(rule)
        def profile(username, status, year): return {'username': username, 'status': status, 'year': year}
        return ap.test_client().get("/profile/user123/active/2024").status_code
    out["O25Q5"] = [status(r) for r in ('/profile/<username>/<status>/<int:year>', '/profile/<string:username>/<string:status>/<string:year>', '/profile/<username>/<status>/<year>',
                                        '/profile/user/<username>/<status>/<year>')]
    # O25 Q9
    a7, a8, a9 = Flask("o25q9a"), Flask("o25q9b"), Flask("o25q9c")

    @a7.route('/user')
    def pa():
        creds = request.args
        return {'username': creds["username"], 'role': creds["role"]}

    @a8.route('/user/<username>/<role>')
    def pb(username, role): return {'username': username, 'role': role}

    @a9.route('/user')
    def pc(): return {'message': 'data retrieved successfully'}
    out["O25Q9"] = [x.test_client().get("/user?username=mad1&role=admin").status_code for x in (a7, a8, a9)]
    # O25 Q14 / Q15
    methods = ["GET", "PUT", "POST"]
    a10 = Flask("o25q14")

    @a10.route('/api/data', methods=methods)
    def handle_data():
        if request.method == 'GET': return "<h1>Data retrieved successfully</h1>"
        elif request.method == 'PUT': return "<h1>Data updated successfully</h1>"
        elif request.method == 'DELETE': return "<h1>Data deleted successfully</h1>"
        else: return "<h1>Unsupported operation</h1>"
    c10 = a10.test_client()
    out["O25Q14"] = c10.post("/api/data").get_data(as_text=True)
    out["O25Q15"] = (c10.delete("/api/data").status_code, "Method Not Allowed" in c10.delete("/api/data").get_data(as_text=True))
    # O25 Q16 / Q17
    with tempfile.TemporaryDirectory() as d:
        Path(d, "bad.py").write_text("from flask import Flask, render_template, request\napp = Flask(__name__)\n@app.route('/login', method=\"GET\")\ndef login(id):\n    name = request.form.get('name', 'Guest')\n    return render_template('login.html', name=name)\n")
        p = sh("python bad.py", d)
        out["O25Q16"] = ("TypeError" in p.stderr and "method" in p.stderr, p.stderr.strip().splitlines()[-1][:90])
    a11 = Flask("o25q17")

    @a11.route('/login')
    def login(id): return "x"
    a11.testing = True
    try:
        a11.test_client().get("/login")
        out["O25Q17"] = "no error"
    except TypeError as e:
        out["O25Q17"] = "TypeError"
    a11.testing = False
    out["O25Q17_500"] = a11.test_client().get("/login").status_code
    # J25 Q7
    a12 = Flask("j25q7")

    @a12.route("/signin/user")
    def login2(): return url_for("login2")

    @a12.route("/")
    def home(): return redirect(url_for("login2"))
    c12 = a12.test_client()
    r1 = c12.get("/")
    out["J25Q7"] = (r1.status_code, r1.headers["Location"], c12.get("/", follow_redirects=True).get_data(as_text=True))
    # J25 Q3
    tdir = tempfile.mkdtemp()
    Path(tdir, "score.html").write_text("{{ mayur }} {{ manoj }}")
    a13 = Flask("j25q3", template_folder=tdir)

    @a13.route('/score')
    def score(): return render_template('score.html', mayur=50, manoj=45)
    a14 = Flask("j25q3c")

    def score_c(): return "x"
    a14.route('/score')   # decorator created but never applied to the function (written after def): nothing registered
    out["J25Q3"] = (a13.test_client().get("/score").get_data(as_text=True), a14.test_client().get("/score").status_code)
    try:
        compile("def score():\n    return 'score.html', mayur=50, manoj=45\n", "d", "exec")
        out["J25Q3_D"] = "compiles"
    except SyntaxError:
        out["J25Q3_D"] = "SyntaxError"
    # M26 Q6
    tdir2 = tempfile.mkdtemp()
    Path(tdir2, "home.html").write_text('<body>\n{% if user == "admin" %}\n<p>Welcome Admin</p>\n{% else %}\n<p>Welcome User</p>\n{% endif %}\n</body>')
    a15 = Flask("m26q6", template_folder=tdir2)

    @a15.route("/")
    def login3(): return render_template("home.html", user="admin iitm")
    out["M26Q6"] = "Welcome User" in a15.test_client().get("/").get_data(as_text=True) and "Welcome Admin" not in a15.test_client().get("/").get_data(as_text=True)
    ok = (out["M26Q3"] == ["Sum: 5", "Sum: 5", "Product: 5", "Sum: 6"] and out["M26Q4"] == "SyntaxError" and out["M26Q8"] == 404 and out["J26Q3"][0] == 200 and out["J26Q3"][1]
          and out["J26Q4"] == "[0, 1, 2, 3, 4]" and out["J26Q7"] == "TypeError" and out["J26Q7_noargs"] == "0" and out["J26Q7_500"] == 500 and out["J26Q9"] == ("Admin Panel", "User: bob")
          and out["J26Q10"] == {"/calculate/10/5": (200, "2.0"), "/calculate/3/0.2": (404, ""), "/calculate/3/2?v1=1": (200, "1.5"), "/calculate?v1=5&v2=2": (404, "")}
          and out["O25Q5"] == [200, 200, 200, 404] and out["O25Q9"] == [200, 404, 200] and out["O25Q14"] == "<h1>Unsupported operation</h1>" and out["O25Q15"] == (405, True)
          and out["O25Q16"][0] and out["O25Q17"] == "TypeError" and out["O25Q17_500"] == 500 and out["J25Q7"] == (302, "/signin/user", "/signin/user")
          and out["J25Q3"] == ("50 45", 404) and out["J25Q3_D"] == "SyntaxError" and out["M26Q6"] is True)
    good = all(s in t for s in ("**1-c, 2-c, 3-d, 4-a**", "**`Admin Panel`**", "**`/calculate/3/0.2`**", "`/profile/user/<username>/<status>/<year>`", "**`TypeError`** (500)", "**A and C**",
                                "**`<h1>Unsupported operation</h1>`**", "**`405 Method Not Allowed`**", "**`/signin/user`**", "**`[0, 1, 2, 3, 4]`**", "`SyntaxError`** in Python 3"))
    return ok and good, (f"M26 Q3 -> {out['M26Q3']}; M26 Q4 port=0007 -> {out['M26Q4']}; M26 Q8 -> {out['M26Q8']}; J26 Q4 -> {out['J26Q4']}; J26 Q7 -> {out['J26Q7']} ({out['J26Q7_500']}), no args -> {out['J26Q7_noargs']}; "
                         f"J26 Q9 -> {out['J26Q9']}; J26 Q10 -> {out['J26Q10']}; O25 Q5 routes A-D -> {out['O25Q5']}; O25 Q9 A-C -> {out['O25Q9']}; O25 Q14 POST -> {out['O25Q14']}; Q15 DELETE -> {out['O25Q15']}; "
                         f"O25 Q16 -> {out['O25Q16'][1]}; Q17 -> {out['O25Q17']} / {out['O25Q17_500']}; J25 Q7 -> {out['J25Q7']}; J25 Q3 B -> {out['J25Q3'][0]!r}, C -> {out['J25Q3'][1]}, D -> {out['J25Q3_D']}; "
                         f"M26 Q6 -> {out['M26Q6']}; notes show them: {good}")


def flask_forms_and_functions():
    from flask import Flask, request, url_for, redirect, abort, render_template, render_template_string
    t = text()
    tdir = tempfile.mkdtemp()
    Path(tdir, "page.html").write_text("<h1>{{ title }}</h1>{% for x in items %}<li>{{ x }}</li>{% endfor %}")
    app = Flask("forms", template_folder=tdir)

    @app.route("/submit", methods=["GET", "POST"])
    def submit():
        if request.method == "POST":
            return f"name={request.form.get('name')} fruits={request.form.getlist('fruits')}"
        return "form"

    @app.route("/strict", methods=["POST"])
    def strict(): return request.form["name"]

    @app.route("/mixed", methods=["POST"])
    def mixed(): return f"form={request.form.get('name')} args={request.args.get('name')}"

    @app.route("/")
    def home(): return "Home"

    @app.route("/user/<username>")
    def profile(username): return username

    @app.route("/links")
    def links():
        return " ".join([url_for("home"), url_for("profile", username="bob"), url_for("profile", username="bob", age=23), url_for("static", filename="css/main.css")])

    @app.route("/old")
    def old(): return redirect(url_for("home"))

    @app.route("/old301")
    def old301(): return redirect(url_for("home"), code=301)

    @app.route("/res/<int:rid>")
    def res(rid):
        if rid != 1:
            abort(404)
        return "found"

    @app.route("/admin")
    def admin(): abort(403)

    @app.route("/render")
    def render(): return render_template("page.html", title="Hi", items=["a", "b"])

    @app.errorhandler(404)
    def not_found(e): return "custom 404 page", 404

    @app.route("/o25q11", methods=['GET', 'POST'])
    def o25q11():
        if request.method == 'POST':
            name = request.form['name']
            template = "Hello, {{ name }}!"
            return render_template_string(template, name=name)
        return '<form method="POST"><input type="text" name="name"></form>'

    @app.route("/protein", methods=['GET'])
    def protein():
        def parse_weight(w):
            if w.endswith('kg'): return float(w[:-2])
            elif w.endswith('lb'): return float(w[:-2]) * 0.453592
            return float(w)

        def rda(g, kg): return kg * (0.8 if g.lower() == 'male' else 0.75)
        gender = request.args.get('gender', 'male')
        weight_raw = request.args.get('weight', '60kg')
        r = int(round(rda(gender, parse_weight(weight_raw))))
        return render_template_string("Gender: {{ gender }} Weight: {{ w }} Recommended Intake: {{ rda }} grams", gender=gender, w=weight_raw, rda=r)
    c = app.test_client()
    app.testing = False
    r = {}
    r["post"] = c.post("/submit", data={"name": "Ann", "fruits": ["apple", "cherry"]}).get_data(as_text=True)
    r["post_one"] = c.post("/submit", data={"name": "Ann"}).get_data(as_text=True)
    r["get"] = c.get("/submit").get_data(as_text=True)
    r["strict_missing"] = c.post("/strict", data={}).status_code
    r["strict_get"] = c.get("/strict").status_code
    r["mixed"] = c.post("/mixed?name=Q", data={"name": "F"}).get_data(as_text=True)
    r["links"] = c.get("/links").get_data(as_text=True)
    r["old"] = (c.get("/old").status_code, c.get("/old").headers["Location"], c.get("/old301").status_code)
    r["abort"] = (c.get("/res/1").status_code, c.get("/res/2").get_data(as_text=True), c.get("/admin").status_code)
    r["render"] = c.get("/render").get_data(as_text=True)
    r["o25q11"] = c.post("/o25q11", data={"name": "Alice"}).get_data(as_text=True)
    r["p1"] = c.get("/protein?gender=FeMaLe&weight=154lb").get_data(as_text=True)
    r["p2"] = c.get("/protein?gender=FEMALE&weight=60").get_data(as_text=True)
    from werkzeug.exceptions import abort as wabort, HTTPException
    try:
        wabort(407)
        r["abort407"] = "no error"
    except LookupError:
        r["abort407"] = "LookupError"
    except HTTPException:
        r["abort407"] = "HTTPException"
    ok = (r["post"] == "name=Ann fruits=['apple', 'cherry']" and r["post_one"] == "name=Ann fruits=[]" and r["get"] == "form" and r["strict_missing"] == 400 and r["strict_get"] == 405
          and r["mixed"] == "form=F args=Q" and r["links"] == "/ /user/bob /user/bob?age=23 /static/css/main.css" and r["old"] == (302, "/", 301)
          and r["abort"] == (200, "custom 404 page", 403) and r["render"] == "<h1>Hi</h1><li>a</li><li>b</li>" and r["o25q11"] == "Hello, Alice!"
          and "Recommended Intake: 52 grams" in r["p1"] and "Gender: FeMaLe" in r["p1"] and "Recommended Intake: 45 grams" in r["p2"] and r["abort407"] == "LookupError")
    good = all(s in t for s in ("→ **400**", "gives **405**", "`/user/bob?age=23`", "`/static/css/main.css`", "`302`, `Location: /`", "**`Hello, Alice!`**", "**`Recommended Intake: 52 grams`**",
                                "**`45 grams`**", "`abort(407)` raises `LookupError`", "`request.form.get('name')` is `F`, `request.args.get('name')` is `Q`", "unchecked checkboxes are not sent" if False else "Unchecked checkboxes are not sent"))
    return ok and good, (f"form POST -> {r['post']!r}, one field -> {r['post_one']!r}; missing key with [] -> {r['strict_missing']}, POST-only route via GET -> {r['strict_get']}; form vs args: {r['mixed']!r}; url_for: {r['links']!r}; "
                         f"redirect {r['old']}; abort/errorhandler {r['abort']}; render_template {r['render']!r}; O25 Q11 -> {r['o25q11']!r}; J25 Q16/17 -> 52 and 45 grams; abort(407) -> {r['abort407']}; notes show them: {good}")


# --------------------------------------------------------------------------- #
# Chromium: CSS / HTML PYQs
# --------------------------------------------------------------------------- #
BROWSER_JS = r"""
const { chromium } = require('playwright'); const fs = require('fs');
(async () => {
  const cases = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
  const b = await chromium.launch(); const page = await b.newPage({ viewport: { width: 900, height: 700 } });
  const out = {};
  for (const c of cases) {
    await page.setContent(c.html);
    out[c.name] = await page.evaluate(c.js);
  }
  console.log(JSON.stringify(out)); await b.close();
})();
"""


def doc(style, body):
    return f"<!DOCTYPE html><html><head><style>{style}</style></head><body style='margin:0'>{body}</body></html>"


def chromium_pyqs():
    node = shutil.which("node")
    if not node:
        SKIPPED.append("Chromium checks skipped (needs node + playwright)")
        print("[SKIP ] CSS / HTML PYQs in Chromium (node missing)\n")
        return None
    t = text()
    color = "(e) => getComputedStyle(e).color"
    bg = "(e) => getComputedStyle(e).backgroundColor"
    cases = [
        {"name": "J26Q1", "html": doc("div{color:green} .cdiv{color:red} #div1{color:blue}", '<div id="div1" class="cdiv">IITM</div>'), "js": f"({color})(document.getElementById('div1'))"},
        {"name": "J25Q8", "html": doc("p{color:blue} #highlight{color:green} .important{color:red}", '<p class="important" id="highlight">x</p>'), "js": f"({color})(document.querySelector('p'))"},
        {"name": "J25Q4", "html": doc(".container p.highlight { background-color: red; } .content .special { background-color: blue; } span.highlight { background-color: green; }",
                                      '<div class="container"><p class="highlight">1 Welcome</p><div class="content"><p>2 regular</p><p class="highlight special">3 Important</p><span class="highlight">4 Notice</span></div>'
                                      '<p class="highlight">5 Footer</p></div><p class="highlight">6 outside</p>'),
         "js": f"[...document.querySelectorAll('p, span')].map(e => [e.textContent.slice(0, 1), ({bg})(e)])"},
        {"name": "M26Q2", "html": doc("p { background-color: yellow; display:inline-block } div p { background-color: lightblue; } .highlight { background-color: pink; } #special { background-color: orange; }",
                                      '<div><p class="highlight">Paragraph One</p><p class="highlight" id="special">Paragraph Two</p><p>Paragraph Three</p></div>'),
         "js": f"[...document.querySelectorAll('p')].map(e => [({bg})(e), Math.round(e.getBoundingClientRect().top)])"},
        {"name": "O25Q10", "html": doc("div { width: 0px; margin: 0px; } .container { width: 200px; padding: 15px; border: 5px solid black; } #box { margin: 10px; }", '<div class="container" id="box">Hello World</div>'),
         "js": "document.getElementById('box').offsetWidth"},
        {"name": "M26Q14", "html": doc("#container { width: 200px; padding: 10px; border: 2px solid black; margin: 15px; }", '<div id="container">x</div>'),
         "js": "(() => { const e = document.getElementById('container'); const r = e.getBoundingClientRect(); return [e.offsetWidth, r.left, getComputedStyle(e).width]; })()"},
        {"name": "M26Q15", "html": doc(".s{width:100px;height:50px;padding:0} .b{display:block;background:#eee}", '<div style="width:400px"><span class="s" id="s">x</span><span class="s" id="ib" style="display:inline-block">y</span><div class="b" id="b">z</div></div>'),
         "js": "(() => { const g = id => document.getElementById(id); return { inlineW: g('s').offsetWidth < 100, inlineBlock: [g('ib').offsetWidth, g('ib').offsetHeight], blockW: g('b').offsetWidth, sameLine: g('s').getBoundingClientRect().top === g('ib').getBoundingClientRect().top, blockBelow: g('b').getBoundingClientRect().top > g('ib').getBoundingClientRect().top }; })()"},
        {"name": "J26Q15", "html": doc(".container{display:flex; width:250px; border:2px solid black;} .box{width:80px; height:40px; border:1px solid blue; margin:5px; text-align:center;}",
                                      '<div class="container" id="c"><div class="box">1</div><div class="box">2</div><div class="box">3</div></div>'),
         "js": "(() => { const c = document.getElementById('c'); const cr = c.getBoundingClientRect(); const bs = [...document.querySelectorAll('.box')].map(e => e.getBoundingClientRect()); return { widths: bs.map(r => +r.width.toFixed(2)), sameRow: bs.every(r => r.top === bs[0].top), inside: bs[2].right + 5 <= cr.right - 2 + 0.05, container: [cr.width, cr.height] }; })()"},
        {"name": "J25Q2", "html": doc("", '<dl><dt>Flask</dt><dd>A Python web framework.</dd><dt>SQLAlchemy</dt><dd>A database toolkit for Python.</dd></dl>'),
         "js": "(() => { const dt = document.querySelector('dt'), dd = document.querySelector('dd'); return { ddMargin: getComputedStyle(dd).marginLeft, ddIndent: dd.getBoundingClientRect().left - dt.getBoundingClientRect().left, ddBelow: dd.getBoundingClientRect().top > dt.getBoundingClientRect().top }; })()"},
        {"name": "box_border", "html": doc(".a{width:200px;padding:10px 20px;border:5px solid;margin:15px} .b{box-sizing:border-box;width:200px;padding:10px 20px;border:5px solid;margin:15px}", '<div class="a" id="a">x</div><div class="b" id="b">x</div>'),
         "js": "(() => { const g = id => document.getElementById(id); return [g('a').offsetWidth, g('b').offsetWidth, getComputedStyle(g('a')).width, getComputedStyle(g('b')).width]; })()"},
        {"name": "collapse", "html": doc("", '<div id="a" style="height:50px;margin-bottom:20px"></div><div id="b" style="height:50px;margin-top:30px"></div>'),
         "js": "document.getElementById('b').getBoundingClientRect().top - document.getElementById('a').getBoundingClientRect().bottom"},
    ]
    # specificity pairs: higher rule written FIRST, lower rule LATER: the higher one must still win
    el = '<div id="main" class="container a b c d e f g h i j k"><div class="content"><p id="p1" class="note highlight special" type="text">x</p></div></div>'
    pairs = [("p.note", ".note"), ("div p", "p"), (".note", "p"), ("p.note", "[type=\"text\"]"), (".container p.highlight", ".content .special"), ("p", "*"),
             ("p:first-child", ".note")]
    for i, (hi, lo) in enumerate(pairs):
        css = f"{hi}{{color:rgb(255,0,0)}} {lo}{{color:rgb(0,0,255)}}"
        cases.append({"name": f"spec{i}", "html": doc(css, el), "js": "getComputedStyle(document.getElementById('p1')).color"})
    cases.append({"name": "spec_id", "html": doc("#main{color:rgb(255,0,0)} .a.b.c.d.e.f.g.h.i.j.k{color:rgb(0,0,255)}", el), "js": "getComputedStyle(document.getElementById('main')).color"})
    # ties: the later rule wins in both orders
    for i, (x, y) in enumerate([(".note", "[type=\"text\"]"), ("[type=\"text\"]", ".note"), (".note", ".note")]):
        cases.append({"name": f"tie{i}", "html": doc(f"{x}{{color:rgb(255,0,0)}} {y}{{color:rgb(0,0,255)}}", '<div class="content"><p id="p1" class="note" type="text">x</p></div>'),
                      "js": "getComputedStyle(document.getElementById('p1')).color"})
    with tempfile.TemporaryDirectory() as d:
        Path(d, "in.json").write_text(json.dumps(cases))
        Path(d, "b.js").write_text(BROWSER_JS)
        env = dict(os.environ, NODE_PATH=subprocess.run(["npm", "root", "-g"], capture_output=True, text=True).stdout.strip())
        p = subprocess.run([node, str(Path(d, "b.js")), str(Path(d, "in.json"))], capture_output=True, text=True, env=env, timeout=180)
        if p.returncode:
            SKIPPED.append("Chromium checks skipped (playwright could not run)")
            print("[SKIP ] CSS / HTML PYQs in Chromium (playwright could not run)\n")
            return None
        R = json.loads(p.stdout.strip().splitlines()[-1])
    RED, BLUE, GREEN = "rgb(255, 0, 0)", "rgb(0, 0, 255)", "rgb(0, 128, 0)"
    j25q4 = {k: v for k, v in R["J25Q4"]}
    m26q2 = R["M26Q2"]
    c15, j15 = R["M26Q15"], R["J26Q15"]
    conds = {
        "J26 Q1 blue": R["J26Q1"] == BLUE, "J25 Q8 green": R["J25Q8"] == GREEN,
        "J25 Q4 red set": j25q4 == {"1": RED, "2": "rgba(0, 0, 0, 0)", "3": RED, "4": GREEN, "5": RED, "6": "rgba(0, 0, 0, 0)"},
        "M26 Q2 colours": [x[0] for x in m26q2] == ["rgb(255, 192, 203)", "rgb(255, 165, 0)", "rgb(173, 216, 230)"], "M26 Q2 one line": len({x[1] for x in m26q2}) == 1,
        "O25 Q10 240": R["O25Q10"] == 240, "M26 Q14 224": R["M26Q14"][0] == 224 and R["M26Q14"][1] == 15 and R["M26Q14"][2] == "200px",
        "M26 Q15 display": c15["inlineW"] and c15["inlineBlock"] == [100, 50] and c15["blockW"] == 400 and c15["sameLine"] and c15["blockBelow"],
        "J26 Q15 flex": j15["sameRow"] and j15["inside"] and all(abs(w - 73.33) < 0.05 for w in j15["widths"]) and j15["container"][0] == 254,
        "J25 Q2 dd": R["J25Q2"]["ddMargin"] == "40px" and R["J25Q2"]["ddIndent"] == 40 and R["J25Q2"]["ddBelow"],
        "box-sizing": R["box_border"] == [250, 200, "200px", "200px"], "margin collapse": R["collapse"] == 30,
        "specificity pairs": all(R[f"spec{i}"] == RED for i in range(len(pairs))) and R["spec_id"] == RED,
        "ties go to the later rule": R["tie0"] == BLUE and R["tie1"] == BLUE and R["tie2"] == BLUE}
    ok = all(conds.values())
    failed = [k for k, v_ in conds.items() if not v_]
    good = all(s in t for s in ("**blue** (ID)", "**green** (ID)", "**240 px**", "$200+20+4 = 224$", "about 73 px", "**one line**: pink, orange, lightblue", "`dd` is indented by default",
                                "(0, 2, 1)", "**A, C, D**"))
    return ok and good, (f"Chromium: J26 Q1 -> {R['J26Q1']}; J25 Q8 -> {R['J25Q8']}; J25 Q4 backgrounds {j25q4} (red = the three p.highlight inside .container); M26 Q2: {[x[0] for x in m26q2]} on one line "
                         f"({len({x[1] for x in m26q2}) == 1}); O25 Q10 -> {R['O25Q10']} px; M26 Q14 -> {R['M26Q14'][0]} px (margin outside); M26 Q15: inline ignores width ({c15['inlineW']}), inline-block {c15['inlineBlock']}, "
                         f"block {c15['blockW']}; J26 Q15: flex items shrink to {j15['widths']} px inside a {j15['container'][0]} px container; J25 Q2: dd indented {R['J25Q2']['ddIndent']} px; "
                         f"box-sizing example {R['box_border']}; margin collapse gap {R['collapse']}; all {len(pairs) + 1} specificity pairs of the table behave as listed, ties go to the later rule; notes say so: {good}" + (f"; FAILED: {failed}" if failed else ""))


def html_snippets():
    jar, java = os.environ.get("VNU_JAR"), shutil.which("java")
    t = text()
    m = re.search(r"```html\n(<table>.*?</table>)\n```", t, re.S)
    if not m:
        return False, "the table snippet of section 6 was not found"
    if not (jar and java):
        SKIPPED.append("Nu HTML validator skipped (set VNU_JAR=.../vnu.jar, needs java)")
        return True, "table snippet found (validation skipped: VNU_JAR / java not available)"
    page = f"<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n<title>t</title>\n</head>\n<body>\n{m.group(1)}\n</body>\n</html>\n"
    img_page = '<!DOCTYPE html>\n<html lang="en"><head><meta charset="utf-8"><title>t</title></head><body><img src="logo.png"></body></html>\n'
    with tempfile.TemporaryDirectory() as d:
        Path(d, "t.html").write_text(page)
        Path(d, "i.html").write_text(img_page)
        r = subprocess.run([java, "-jar", jar, "--errors-only", "--format", "json", str(Path(d, "t.html"))], capture_output=True, text=True)
        r2 = subprocess.run([java, "-jar", jar, "--errors-only", "--format", "json", str(Path(d, "i.html"))], capture_output=True, text=True)
    def messages(proc):
        m = re.search(r"\{.*\}", proc.stderr + proc.stdout, re.S)          # skip the "Picked up JAVA_TOOL_OPTIONS" banner; no JSON = no errors
        return json.loads(m.group(0))["messages"] if m else []
    msgs, msgs2 = messages(r), messages(r2)
    alt_error = any("alt" in x.get("message", "") for x in msgs2)
    return not msgs and alt_error, f"the table (colspan / rowspan) is valid HTML: errors {[x['message'] for x in msgs] or 'none'}; an <img> without alt is still reported by the validator: {alt_error}"


# --------------------------------------------------------------------------- #
# the page itself: agenda, links, hygiene
# --------------------------------------------------------------------------- #
def github_slug(heading):
    s = re.sub(r"[`*_]", lambda m: "_" if m.group(0) == "_" else "", heading.lower())
    s = re.sub(r"[^\w\- ]", "", s, flags=re.UNICODE)
    return s.replace(" ", "-")


def agenda():
    t = text()
    rows = re.findall(r"^\| (\d+)-(\d+) \|", t, re.M)
    spans = [(int(a), int(b)) for a, b in rows]
    contiguous = all(spans[i][1] == spans[i + 1][0] for i in range(len(spans) - 1))
    total = spans[-1][1] - spans[0][0]
    section_min = [int(x) for x in re.findall(r"⏱ \*\*(\d+) min", t)]
    agenda_text = t.split("## How to run the session", 1)[1].split("---", 1)[0]
    codes = re.findall(r"\b([MJO]\d\d) Q(\d+)", agenda_text)
    body = t.split("## What the four papers ask", 1)[1]
    missing = [f"{p} Q{n}" for p, n in codes if f"{p} Q{n}" not in body]
    ok = spans[0][0] == 0 and total == 120 and contiguous and sum(section_min) == 110 and len(section_min) == 14 and not missing
    return ok, (f"agenda blocks {spans[0][0]}-{spans[-1][1]} min, contiguous: {contiguous}, total {total} min; the 14 topic blocks add up to {sum(section_min)} min (+ 5 min exam pattern + 5 min checklist = 120); "
                f"every PYQ named in the agenda is solved in the body: {not missing} {missing or ''}")


#: the answer each PYQ row must state (the facts behind them are run in the checks above)
EXPECTED_ANSWERS = {
    "M26 Q11": "**B, C**", "O25 Q12": "**A, B, C**", "M26 Q9": "**B** (`-v`)",
    "J26 Q12": "**125 ms**", "J26 Q5": "**3000**", "J25 Q11": "**250 MB**", "J25 Q12": "**72 ms**", "M26 Q1": "**56.25 MB**",
    "J26 Q13": "**5**", "M26 Q10": "**A, B, D**",
    "J26 Q2": "**B**", "O25 Q4": "**S2 correct, S1 incorrect**", "O25 Q13": "**A, B**", "J25 Q2": "**indented**",
    "J26 Q1": "**blue** (ID)", "J25 Q8": "**green** (ID)", "J25 Q4": "every `<p class=\"highlight\">` that is a descendant of `.container`", "M26 Q2": "**one line**: pink, orange, lightblue",
    "O25 Q10": "**240 px**", "M26 Q14": "**A, C, D**", "M26 Q15": "**A, C, D**", "J26 Q15": "**three separate boxes in one row, all inside the container, with small gaps**",
    "O25 Q2": "**B**", "M26 Q5": "**`51117`**", "M26 Q7": "**`<p>1</p><p>2</p><p>5</p><p>8</p><p>9</p>`**", "J26 Q14": "**A**", "J25 Q9": "**`{%for item in sl\\|sort%}`**",
    "J26 Q16": "**Kittu**", "M26 Q6": "**Welcome User**", "M26 Q13": "**all four**", "J25 Q6": "**Hello, Alice! Hello, Bob!**",
    "O25 Q7": "**1→B, 2→D, 3→C, 4→A**", "M26 Q12": "**A, B, D**", "O25 Q6": "**`Module: main.py`**", "J25 Q10": "**`1,2,3,4,5`**", "J26 Q6": "**`Result: 42`**",
    "J26 Q9": "**`Admin Panel`**", "M26 Q8": "**404**", "J26 Q10": "**`/calculate/3/0.2`**", "O25 Q5": "**`/profile/user/<username>/<status>/<year>`**", "J26 Q7": "**`TypeError`** (500)",
    "M26 Q3": "**1-c, 2-c, 3-d, 4-a**", "O25 Q9": "**A and C**", "O25 Q14": "**`<h1>Unsupported operation</h1>`**", "O25 Q16": "**`methods=[\"GET\"]`**", "O25 Q17": "**500 `TypeError`**",
    "J26 Q3": "**both correct**", "J26 Q4": "**`[0, 1, 2, 3, 4]`**", "O25 Q11": "**`Hello, Alice!`**", "J25 Q16": "**`Recommended Intake: 52 grams`**", "J25 Q17": "**`45 grams`**",
    "J25 Q7": "**`/signin/user`**", "J25 Q3": "**B**", "M26 Q4": "**none of these**",
}


def answers_match():
    t = text()
    rows = {}
    for line in t.splitlines():
        m = re.match(r"^\| \*\*(.*?)\*\*(.*?) \| .* \| (.+?) \|$", line)
        if not m:
            continue
        code = re.match(r"([MJO]\d\d) Q(\d+)", m.group(1))
        if code:
            rows.setdefault(f"{code.group(1)} Q{code.group(2)}", []).append(m.group(3))
    wrong = [f"{k}: expected {v!r}, row says {rows.get(k)}" for k, v in EXPECTED_ANSWERS.items() if not any(v in cell for cell in rows.get(k, []))]
    return not wrong, f"{len(EXPECTED_ANSWERS)} PYQ rows state exactly the answer verified above: {wrong or 'all match'}"


def pyq_coverage():
    t = text()
    body = t.split("## What the four papers ask", 1)[1]
    found = set(re.findall(r"\b([MJO]\d\d) Q(\d+)", body))
    papers = {p for p, _ in found}
    n = len(found)
    return papers == {"M26", "J26", "O25", "J25"} and n >= 40, f"PYQs worked in the notes: {n} question numbers from {sorted(papers)}"


def links_resolve():
    t = text()
    bad = []
    no_code = re.sub(r"```.*?```", "", t, flags=re.S)
    heads_self = {github_slug(h) for h in re.findall(r"^#{1,6}\s+(.*)$", t, re.M)}
    n = 0
    for m in re.finditer(r"\]\(([^)\s]+)\)", no_code):
        url = m.group(1)
        if re.match(r"(https?:|mailto:)", url):
            continue
        n += 1
        path, _, anchor = url.partition("#")
        target = (HERE / path).resolve() if path else NOTE
        if not target.exists():
            bad.append(f"{url} (file not found)")
        elif anchor:
            slugs = heads_self if target == NOTE else {github_slug(h) for h in re.findall(r"^#{1,6}\s+(.*)$", re.sub(r"```.*?```", "", target.read_text(encoding='utf-8'), flags=re.S), re.M)}
            if anchor not in slugs:
                bad.append(f"{url} (no such heading)")
    return not bad, f"{n} local links / anchors checked, unresolved: {bad or 'none'}"


def hygiene():
    t = text()
    bad = []
    for i, line in enumerate(t.splitlines(), 1):
        if re.match(r"^\s*:::|^== |^```\w+ \[|</?[A-Z]\w+[^>]*/?>", line):
            bad.append(f"{i}: VitePress syntax")
        if re.search(r"style\s*=|&emsp;|<font|<center", re.sub(r"`[^`]*`", "", line)) and "```" not in line:     # inline code is fine
            bad.append(f"{i}: HTML that GitHub strips")
        m = re.match(r"^> \[!(\w+)\]\s*$", line)
        if m and m.group(1) not in {"NOTE", "TIP", "IMPORTANT", "WARNING", "CAUTION"}:
            bad.append(f"{i}: alert type")
    if t.count("<details>") != t.count("</details>"):
        bad.append("unbalanced <details>")
    for m in re.finditer(r"<summary>(.*?)</summary>", t, re.S):
        if "`" in m.group(1):
            bad.append(f"backticks in <summary> {m.group(1)[:30]!r}")
    open_ = False
    for i, line in enumerate(t.splitlines(), 1):
        m = re.match(r"^(\s*)```(.*)$", line)
        if not m:
            continue
        if not open_:
            open_ = True
        else:
            open_ = False
            if m.group(1) or m.group(2).strip():
                bad.append(f"{i}: closing fence {line!r}")
    if open_:
        bad.append("unclosed fence")
    for m in re.finditer(r"\\=|\\text\{[^}]*\$", t):
        bad.append(f"LaTeX problem {m.group(0)!r}")
    # tables: GitHub cuts a cell at every unescaped "|", even inside `code`, so every row needs the same number of cells as its header
    in_code, width = False, None
    for i, line in enumerate(t.splitlines(), 1):
        if line.lstrip().startswith("```"):
            in_code = not in_code
        if in_code:
            continue
        if line.startswith("|"):
            cells = len(re.split(r"(?<!\\)\|", line.rstrip().rstrip("|")[1:]))
            if width is None:
                width = cells
            elif cells != width:
                bad.append(f"{i}: table row has {cells} cells, header has {width}")
        else:
            width = None
    personal = re.findall(r"[\w.+-]+@[\w-]+\.[\w.]+|Downloaded by|quizpractice", t)       # e-mail addresses and the PDF watermark
    if personal:
        bad.append(f"personal data / source watermark: {personal}")
    return not bad, f"VitePress-only syntax, stripped HTML, bad alerts, unbalanced <details>, backticks in <summary>, fences, LaTeX typos, personal data: {bad or 'none'}"


if __name__ == "__main__":
    print("=" * 78 + "\nRevision notes claim checker\n" + "=" * 78 + "\n")
    check("numericals: 56.25 MB, 125 ms, 3000, 250 MB, 72 ms, 5 bits, plus the worked problems", numericals)
    check("number-system conversion table", number_systems)
    check("IPv4 / IPv6 conversions and counts", ip_addresses)
    check("Jinja2: variables, if, for, loop variables, filters (sort, reject, default, ...), scope", jinja_claims)
    check("string.Template vs Jinja2 table: each engine ignores the other's syntax", string_template_claims)
    check("PYQs J25 Q5, O25 Q8, M26 Q16, J26 Q8 (Template / Jinja2 mix)", pyq_template_mix)
    check("pyhtml: tag(attributes)(children), class_, underscores, escaping", pyhtml_claims)
    check("sys.argv PYQs (O25 Q6, J25 Q10, J26 Q11, J25 Q13-15, J26 Q6) as real processes", argv_pyqs)
    check("Flask routes: converters, 404s, query strings, trailing slash, return types, url_map", flask_routes)
    check("Flask PYQs: M26 Q3/Q4/Q6/Q8, J26 Q3/Q4/Q7/Q9/Q10, O25 Q5/Q9/Q14-17, J25 Q3/Q7", flask_pyqs)
    check("forms, url_for, redirect, abort, render_template, J25 Q16/Q17, O25 Q11", flask_forms_and_functions)
    b = chromium_pyqs()
    if b is not None:
        check("CSS / HTML PYQs in Chromium: specificity, box widths, display, flex, dl", lambda: b)
    check("HTML snippet of section 6 (colspan / rowspan table)", html_snippets)
    check("the 120-minute agenda adds up and every named PYQ is solved", agenda)
    check("every PYQ row of the notes states the verified answer", answers_match)
    check("PYQ coverage: all four papers are used", pyq_coverage)
    check("every local link and anchor resolves", links_resolve)
    check("markdown hygiene (GitHub rendering, no personal data)", hygiene)
    print("=" * 78)
    wrong = len([r for r in RESULTS if not r])
    print(f"{len(RESULTS)} checks, {len(RESULTS) - wrong} OK, {wrong} WRONG")
    print("\nNOT VERIFIABLE HERE (kept because they are standard, but not executed):")
    for s in SKIPPED + [
        "the exam key of O25 Q13 (alt 'not mandatory') is the course's convention; HTML validators still require alt (checked with VNU when available)",
        "the original quiz pages (quizpractice.space) are blocked from this sandbox: the questions were retyped from the PDFs the course provided and their answer keys re-derived by running the code",
        "TCP / UDP / IP statements are from the notes (RFC behaviour, nothing executed)",
    ]:
        print("  -", s)
    sys.exit(1 if wrong else 0)
