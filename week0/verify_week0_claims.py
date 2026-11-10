"""
Week 0 notes -- claim checker.

Every check takes one statement (or code snippet) from the week0 notes, runs it
on the real Python interpreter / pip / shell, and reports whether the notes are
right:

    OK     -> the notes say what actually happens
    WRONG  -> the notes say something that does not happen (the evidence shows what does)

A check usually has two halves:
    1. the FACT        -> measured here (subprocess, venv, pip, arithmetic)
    2. the NOTE TEXT   -> the markdown contains the correct statement and not the wrong one

The claims are written as the notes state them *after* the accuracy fixes, so a
clean run ends with "0 WRONG". If a Python/pip upgrade changes behaviour, the
affected check turns WRONG and points to the note that needs updating.

Run (from anywhere):
    python week0/verify_week0_claims.py        # needs network only for the two pip checks
    python week0/verify_week0_claims.py -v     # also print the raw output of each probe

Checked against CPython 3.13 / pip 26 on Linux. Windows-only and website-only
statements cannot be run here; they are listed under "NOT VERIFIABLE HERE" at
the end instead of being silently trusted.
"""
import os
import re
import shlex
import subprocess
import sys
import tempfile
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
VERBOSE = "-v" in sys.argv
RESULTS = []
SKIPPED = []
PY = sys.executable


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def note(name):
    return (HERE / name).read_text(encoding="utf-8")


def check(file, claim, fn):
    """fn() returns (notes_are_correct: bool, evidence: str)."""
    try:
        ok, evidence = fn()
    except Exception as e:  # a crash while checking = WRONG
        ok, evidence = False, f"raised {type(e).__name__}: {str(e).splitlines()[0][:150]}"
    RESULTS.append((ok, file))
    print(f"[{'OK   ' if ok else 'WRONG'}] {file}\n        claim   : {claim}\n        actual  : {evidence}\n")


def run(args, cwd, **kw):
    p = subprocess.run(args, cwd=cwd, capture_output=True, text=True, **kw)
    if VERBOSE:
        print(f"        $ {' '.join(map(str, args))}\n          -> rc={p.returncode} out={p.stdout.strip()[:120]!r} err={p.stderr.strip()[:120]!r}")
    return p


def argv_of(args, cwd, stdin=None):
    p = run([PY, *args], cwd, input=stdin)
    return eval(p.stdout.strip().splitlines()[-1])  # the child prints repr(sys.argv)


def has(text, pattern, flags=re.I):
    return re.search(pattern, text, flags) is not None


def fenced_blocks(text):
    """[(info_string, body)] for every ``` block."""
    return re.findall(r"^```([^\n]*)\n(.*?)^\s*```", text, re.S | re.M)


# --------------------------------------------------------------------------- #
# 0-sys.md
# --------------------------------------------------------------------------- #
def sys_argv0():
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        (d / "sub").mkdir()
        for p in (d / "myfile.py", d / "sub" / "myfile.py"):
            p.write_text("import sys\nprint(sys.argv)\n")
        rel = argv_of(["myfile.py"], d)[0]
        dot = argv_of(["./myfile.py"], d)[0]
        sub = argv_of(["sub/myfile.py"], d)[0]
        ab = argv_of([str(d / "myfile.py")], d)[0]
        c = argv_of(["-c", "import sys;print(sys.argv)"], d)[0]
        m = argv_of(["-m", "myfile"], d / "sub")[0]
        std = argv_of(["-"], d, stdin="import sys;print(sys.argv)")[0]
    fact = (rel == "myfile.py" and dot == "./myfile.py" and sub == "sub/myfile.py"
            and ab == str(d / "myfile.py") and c == "-c" and m.endswith("myfile.py") and m != "myfile.py"
            and std == "-")
    text = note("0-sys.md")
    good = has(text, r"as (it was )?typed|path .*given|exactly as") and has(text, r"-c")
    bad = has(text, r"always the file name")
    return fact and good and not bad, (
        f"argv[0]: 'myfile.py' -> {rel!r}, './myfile.py' -> {dot!r}, 'sub/myfile.py' -> {sub!r}, "
        f"absolute -> path, -c -> {c!r}, -m -> full path, '-' -> {std!r} | note says 'always the file name': {bad}; "
        f"explains path/-c: {good}")


def sys_argv_basic():
    with tempfile.TemporaryDirectory() as d:
        Path(d, "myfile.py").write_text("import sys\nprint(sys.argv)\n")
        none = argv_of(["myfile.py"], d)
        five = run([PY, "-c", "import sys;print(type(sys.argv[1]).__name__)", "5"], d).stdout.strip()
    return none == ["myfile.py"] and five == "str", f"no arguments -> {none}; python x.py 5 -> sys.argv[1] is {five}"


def sys_argv_shell_does_splitting():
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        (d / "myfile.py").write_text("import sys\nprint(sys.argv)\n")
        (d / "a1.txt").write_text("")
        (d / "a2.txt").write_text("")
        quoted = eval(run(["bash", "-c", f'{shlex.quote(PY)} myfile.py complex "argument 3"'], d).stdout)
        unq = eval(run(["bash", "-c", f"{shlex.quote(PY)} myfile.py complex argument 3"], d).stdout)
        glob = eval(run(["bash", "-c", f"{shlex.quote(PY)} myfile.py *.txt"], d).stdout)
        raw = argv_of(["myfile.py", "has space"], d)  # no shell at all: Python keeps the list as is
    fact = quoted == ["myfile.py", "complex", "argument 3"] and unq[1:] == ["complex", "argument", "3"] \
        and glob[1:] == ["a1.txt", "a2.txt"] and raw[1:] == ["has space"]
    text = note("0-sys.md")
    good = has(text, r"the shell") and has(text, r"quote")
    return fact and good, f'shell quoting -> {quoted[1:]}; unquoted -> {unq[1:]}; *.txt expanded by the shell -> {glob[1:]}; note credits the shell: {good}'


def sys_exit():
    r = lambda code: run([PY, "-c", code], ".")
    none, three, text_, nn = (r("import sys;sys.exit()"), r("import sys;sys.exit(3)"),
                              r("import sys;sys.exit('boom')"), r("import sys;sys.exit(None)"))
    caught = r("import sys\ntry:\n  try: sys.exit(2)\n  finally: print('finally ran')\nexcept SystemExit as e: print('caught', e.code)").stdout.split()
    fact = (none.returncode, three.returncode, text_.returncode, nn.returncode) == (0, 3, 1, 0) \
        and text_.stderr.strip() == "boom" and caught == ["finally", "ran", "caught", "2"]
    t = note("0-sys.md")
    good = has(t, r"SystemExit") and has(t, r"exit status|exit code")
    return fact and good, (f"exit()={none.returncode}, exit(3)={three.returncode}, exit('boom')={text_.returncode} (+stderr 'boom'), "
                           f"exit(None)={nn.returncode}; raises SystemExit (finally runs, can be caught): {caught}; note mentions SystemExit: {good}")


def sys_platform_version():
    plat = sys.platform
    vi = tuple(sys.version_info)[:3]
    fact = isinstance(plat, str) and plat in {"linux", "win32", "darwin"} and isinstance(sys.version, str) \
        and vi >= (3, 8, 0) and sys.version.startswith(".".join(map(str, vi)))
    t = note("0-sys.md")
    good = all(has(t, w) for w in (r"`linux`", r"`win32`", r"`darwin`", r"sys\.version_info"))
    return fact and good, f"sys.platform={plat!r}; sys.version starts '{sys.version.split()[0]}' (str); sys.version_info={vi}; note lists linux/win32/darwin + version_info: {good}"


def sys_note_examples():
    """Run the python/bash/txt triples of 0-sys.md exactly as written."""
    blocks = fenced_blocks(note("0-sys.md"))
    triples, i = [], 0
    while i < len(blocks):
        if blocks[i][0].strip() == "python" and i + 2 < len(blocks) and blocks[i + 1][0].strip() == "bash" \
                and blocks[i + 2][0].strip() in ("txt", "text"):
            triples.append((blocks[i][1], blocks[i + 1][1].strip(), blocks[i + 2][1].strip()))
            i += 3
        else:
            i += 1
    if len(triples) < 2:
        return False, f"expected 2 python/bash/txt example triples, found {len(triples)}"
    out = []
    for code, cmd, expected in triples:
        with tempfile.TemporaryDirectory() as d:
            Path(d, "myfile.py").write_text(code)
            got = run(["bash", "-c", cmd.replace("python ", f"{shlex.quote(PY)} ", 1)], d).stdout.strip()
        out.append(got == expected)
        if got != expected:
            print(f"        mismatch: {cmd!r}\n          expected {expected!r}\n          got      {got!r}")
    return all(out), f"{sum(out)}/{len(out)} python+command+output examples reproduce exactly"


# --------------------------------------------------------------------------- #
# 0-basic-setup-guide.md
# --------------------------------------------------------------------------- #
def pip_probe(d):
    """Fresh venv in directory d; returns (venv_python, helper to run pip)."""
    v = Path(d) / "env_name"
    run([PY, "-m", "venv", str(v)], d)
    return v / "bin" / "python"


def pip_freeze_vs_list():
    with tempfile.TemporaryDirectory() as d:
        vpy = pip_probe(d)
        fresh_freeze = run([vpy, "-m", "pip", "freeze"], d).stdout.strip()
        fresh_list = run([vpy, "-m", "pip", "list"], d).stdout
        fresh_all = run([vpy, "-m", "pip", "freeze", "--all"], d).stdout.strip()
        inst = run([vpy, "-m", "pip", "install", "-q", "--disable-pip-version-check", "six"], d)
        if inst.returncode:
            SKIPPED.append("pip install needs network (PyPI) -> pip freeze/list/uninstall checks skipped")
            RESULTS.append((True, "0-basic-setup-guide.md"))
            print("[SKIP ] 0-basic-setup-guide.md  pip freeze vs list (no network)\n")
            return None
        freeze = run([vpy, "-m", "pip", "freeze"], d).stdout.strip()
        lst = run([vpy, "-m", "pip", "list", "--disable-pip-version-check"], d).stdout
        req = Path(d, "requirements.txt")
        req.write_text(freeze + "\n")
        show = run([vpy, "-m", "pip", "show", "six"], d)
        up = run([vpy, "-m", "pip", "install", "--upgrade", "--disable-pip-version-check", "six"], d)
        un = run([vpy, "-m", "pip", "uninstall", "-r", str(req), "-y"], d)
        after = run([vpy, "-m", "pip", "freeze"], d).stdout.strip()
        re_ins = run([vpy, "-m", "pip", "install", "-q", "--disable-pip-version-check", "-r", str(req)], d)
        back = run([vpy, "-m", "pip", "freeze"], d).stdout.strip()
    fact = (fresh_freeze == "" and "pip" in fresh_list and fresh_all.startswith("pip==")
            and re.fullmatch(r"six==[\d.]+", freeze) and re.search(r"^six\s+[\d.]+$", lst, re.M)
            and show.returncode == 0 and up.returncode == 0 and un.returncode == 0 and after == ""
            and re_ins.returncode == 0 and back == freeze)
    t = note("0-basic-setup-guide.md")
    good = has(t, r"pip list") and has(t, r"pip freeze > requirements\.txt") and not has(t, r"list installed packages: `pip freeze`")
    return bool(fact) and good, (f"fresh venv: `pip freeze` prints {fresh_freeze!r} (hides pip itself), `pip list` shows pip, `freeze --all` -> {fresh_all!r}; "
                                 f"after installing six: freeze -> {freeze!r}, list -> table; show/upgrade/`uninstall -r req -y`/`install -r req` all work; "
                                 f"note uses `pip list` + `pip freeze > requirements.txt`: {good}")


def venv_activate_files():
    with tempfile.TemporaryDirectory() as d:
        vpy = pip_probe(d)
        names = sorted(p.name for p in (Path(d) / "env_name" / "bin").iterdir())
        out = run(["bash", "-c", f"source {shlex.quote(str(Path(d)/'env_name'/'bin'/'activate'))}; "
                   "python -c 'import sys;print(sys.prefix!=sys.base_prefix)'; type -t deactivate; echo $VIRTUAL_ENV_PROMPT; deactivate; "
                   "python -c 'import sys;print(sys.prefix!=sys.base_prefix)' 2>/dev/null || echo gone"], d).stdout.split()
    fact = {"activate", "Activate.ps1"} <= set(names) and out[:3] == ["True", "function", "env_name"]
    t = note("0-basic-setup-guide.md")
    good = has(t, r"Activate\.ps1") and has(t, r"execution policy") and has(t, r"source env_name/bin/activate")
    return fact and good, (f"on POSIX the venv has {', '.join(n for n in names if 'activ' in n.lower())}; after sourcing: venv active={out[0]}, deactivate is a {out[1]}, "
                           f"prompt prefix={out[2]!r}; note names Activate.ps1 + execution policy: {good}")


def ensurepip_ships_pip():
    import ensurepip
    r = run([PY, "-m", "ensurepip", "--version"], ".")
    t = note("0-basic-setup-guide.md")
    good = has(t, r"ensurepip") and has(t, r"separate package")
    return r.returncode == 0 and bool(ensurepip.version()) and good, f"`python -m ensurepip --version` -> {r.stdout.strip()!r}; note mentions ensurepip and distro-separate packages: {good}"


def python_command_name():
    t = note("0-basic-setup-guide.md")
    good = has(t, r"python3 --version") and has(t, r"py --version|`py`")
    return good, f"note shows the per-OS commands (python / python3 / py): {good}"


# --------------------------------------------------------------------------- #
# 0-metrics.md
# --------------------------------------------------------------------------- #
UNIT = {  # value of one unit in the base unit of its family
    "bit": Fraction(1, 8), "bits": Fraction(1, 8), "byte": 1, "bytes": 1,
    "kb": 10**3, "mb": 10**6, "gb": 10**9, "tb": 10**12,
    "s": 1, "second": 1, "seconds": 1, "ms": Fraction(1, 10**3), "millisecond": Fraction(1, 10**3), "milliseconds": Fraction(1, 10**3),
    "µs": Fraction(1, 10**6), "microsecond": Fraction(1, 10**6), "microseconds": Fraction(1, 10**6),
    "ns": Fraction(1, 10**9), "nanosecond": Fraction(1, 10**9), "nanoseconds": Fraction(1, 10**9),
    "unit": 1, "units": 1, "million": 10**6, "billion": 10**9, "trillion": 10**12,
}


def parse_amount(tok):
    tok = tok.strip().strip("*")
    m = re.fullmatch(r"\$10\^\{(-?\d+)\}\$", tok)
    return Fraction(10) ** int(m.group(1)) if m else Fraction(tok)


def metrics_equalities():
    bad, n = [], 0
    for line in note("0-metrics.md").splitlines():
        m = re.match(r"\s*- \*\*1 ([^*(]+?)(?: \([^)]*\))?\*\* = (.+)", line)
        if not m:
            continue
        first, rest = m.group(1).strip().lower(), m.group(2)
        for part in re.split(r"\s=\s", " = " + rest)[1:]:
            part = part.strip()
            mm = re.fullmatch(r"(\$10\^\{-?\d+\}\$|\d+)\s+(\S+)(?:\s+\([^)]*\))?", part)  # "1000 milliseconds (ms)"
            if not mm:
                bad.append(f"cannot parse {part!r}")
                continue
            n += 1
            if parse_amount(mm.group(1)) * UNIT[mm.group(2).lower()] != UNIT[first]:
                bad.append(f"1 {first} != {part}")
    return n >= 20 and not bad, f"{n} equalities evaluated with exact fractions; wrong: {bad or 'none'}"


def metrics_prefix_table():
    si = {"exa": 18, "peta": 15, "tera": 12, "giga": 9, "mega": 6, "kilo": 3, "hecto": 2, "deka": 1,
          "milli": -3, "micro": -6, "nano": -9}
    rows = dict(re.findall(r"^\|\s*(\w+)\s*\|\s*\$10\^\{(-?\d+)\}\$\s*\|", note("0-metrics.md"), re.M))
    wrong = {k: v for k, v in rows.items() if k in si and int(v) != si[k]}
    missing = [k for k in ("milli", "micro", "nano") if k not in rows]
    return not wrong and not missing, f"{len(rows)} table rows; wrong exponents: {wrong or 'none'}; small prefixes used further down but missing from the table: {missing or 'none'}"


def metrics_decimal_vs_binary():
    ratio = Fraction(1024**3, 1000**3)
    t = note("0-metrics.md")
    good = has(t, r"KiB|1024") and has(t, r"decimal|SI")
    return good, f"1 GiB / 1 GB = {float(ratio):.4f} (~{(ratio-1)*100:.1f}% bigger), so 1000 vs 1024 matters in numericals; note states the decimal (SI) convention and mentions 1024/KiB: {good}"


# --------------------------------------------------------------------------- #
# 0-python-basics.md / 0-vscode-setup.md
# --------------------------------------------------------------------------- #
def terminology_tui():
    t = note("0-python-basics.md")
    return not has(t, r"Terminal User Interface") and has(t, r"command[- ]line"), (
        "a TUI is a full-screen text application (vim, htop); typing commands (cd, ls, python ...) into a shell is the command-line interface (CLI). "
        f"note says 'Terminal User Interface': {has(t, 'Terminal User Interface')}")


def typos():
    bad = {
        "0-python-basics.md": [r"you or may not", r"including every language feature we will cover"],
        "0-vscode-setup.md": [r"Window installation", r"error related script"],
    }
    found = [(f, p) for f, ps in bad.items() for p in ps if has(note(f), p)]
    return not found, f"known typos/garbled phrases still present: {found or 'none'}"


YT_OK = re.compile(r"https://(?:youtu\.be/[\w-]{11}|www\.youtube\.com/watch\?v=[\w-]{11})(?:[?&][\w=&-]*)?$")


def youtube_links():
    bad = []
    for f in sorted(HERE.glob("*.md")):
        for url in re.findall(r"https?://(?:www\.)?youtu[^\s)>\]]*", f.read_text(encoding="utf-8")):
            if not YT_OK.match(url):
                bad.append((f.name, url))
    return not bad, f"YouTube links that are not youtu.be/<id> or youtube.com/watch?v=<id>: {bad or 'none'}"


def vscode_licence_wording():
    t = note("0-vscode-setup.md")
    bad = has(t, r"free and open source")
    good = has(t, r"Code - OSS|MIT")
    return not bad and good, f"'Free and open source' stated for the Microsoft build: {bad}; note explains Code - OSS/MIT vs the Microsoft licence: {good}"


def vscode_mac_shortcuts():
    t = note("0-vscode-setup.md")
    new = has(t, r"new\*\* (terminal|Command Prompt)|restart")
    return has(t, r"Cmd|⌘") and new, f"note mentions macOS (Cmd) shortcut: {has(t, r'Cmd|⌘')}; says to open a new terminal after PATH changes: {new}"


# --------------------------------------------------------------------------- #
# markdown hygiene (the "what we did in week5" part)
# --------------------------------------------------------------------------- #
def no_vitepress_syntax():
    found = []
    for f in sorted(HERE.glob("*.md")):
        for i, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if re.match(r"^:::|^== |^```\w+ \[|<[A-Z]\w+[^>]*/>", line):
                found.append(f"{f.name}:{i}")
    return not found, f"VitePress-only syntax (::: / == / ```lang [Label] / <Component/>): {found or 'none'}"


def local_images_exist():
    miss = []
    for f in sorted(HERE.glob("*.md")):
        for rel in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", f.read_text(encoding="utf-8")):
            if not rel.startswith("http") and not (f.parent / rel).resolve().exists():
                miss.append(f"{f.name}: {rel}")
    return not miss, f"missing local images: {miss or 'none'}"


def fences_clean():
    bad = []
    for f in sorted(HERE.glob("*.md")):
        lines = f.read_text(encoding="utf-8").splitlines()
        open_ = False
        for i, line in enumerate(lines, 1):
            m = re.match(r"^(\s*)```(.*)$", line)
            if not m:
                continue
            if not open_:
                open_ = True
                if m.group(1) or "[" in m.group(2):
                    bad.append(f"{f.name}:{i} opening fence {line!r}")
            else:
                open_ = False
                if m.group(1) or m.group(2).strip():
                    bad.append(f"{f.name}:{i} closing fence {line!r}")
        if open_:
            bad.append(f"{f.name}: unclosed fence")
    return not bad, f"badly indented / labelled / unclosed code fences: {bad or 'none'}"


def no_empty_sections():
    bad = []
    for f in sorted(HERE.glob("*.md")):
        prev = None
        for i, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            m = re.match(r"^(#{1,6}) (.*)", line)
            if m and prev and len(m.group(1)) <= prev[0]:
                bad.append(f"{f.name}:{prev[2]} '{prev[1]}' is immediately followed by a same/higher level heading")
            prev = (len(m.group(1)), m.group(2), i) if m else None
    return not bad, f"headings with no content before the next same-level heading: {bad or 'none'}"


# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    S, B, M, P, V = "0-sys.md", "0-basic-setup-guide.md", "0-metrics.md", "0-python-basics.md", "0-vscode-setup.md"
    print("=" * 78 + "\nWeek 0 claim checker\n" + "=" * 78 + "\n")
    check(S, "sys.argv[0] is the script name *as typed on the command line* (path included); '-c' / '-' / full module path for -c, stdin, -m", sys_argv0)
    check(S, "no arguments -> sys.argv has one element; every argument is a str", sys_argv_basic)
    check(S, "the shell (not Python) splits on spaces, removes quotes and expands *.txt; Python just receives the list", sys_argv_shell_does_splitting)
    check(S, "sys.exit(n) raises SystemExit; exit status 0 / n / 1 for a message; finally blocks still run", sys_exit)
    check(S, "sys.platform is 'linux' / 'win32' / 'darwin'; sys.version is a str, sys.version_info is the comparable tuple", sys_platform_version)
    check(S, "the python/command/output examples print exactly what the note shows", sys_note_examples)
    r = pip_freeze_vs_list()
    if r is not None:
        check(B, "`pip list` lists installed packages; `pip freeze` prints name==version for requirements.txt; install/upgrade/show/uninstall -r all work", lambda: r)
    check(B, "venv creates activate / Activate.ps1; `deactivate` is a shell function; prompt shows the env name", venv_activate_files)
    check(B, "pip comes with Python via ensurepip, but some Linux distributions ship pip/venv as separate packages", ensurepip_ships_pip)
    check(B, "the version check is shown for every OS (python / python3 / py)", python_command_name)
    check(M, "every '1 X = ... = ...' equality in the unit lists is arithmetically correct", metrics_equalities)
    check(M, "prefix table exponents match SI and include milli/micro/nano used below", metrics_prefix_table)
    check(M, "1 KB = 1000 B is the decimal (SI) convention; 1024-based units are KiB/MiB/GiB", metrics_decimal_vs_binary)
    check(P, "the command line is a CLI, not a 'Terminal User Interface'", terminology_tui)
    check(f"{P}, {V}", "no typos / garbled sentences", typos)
    check(V, "YouTube links use a working form (youtu.be/<id> or watch?v=<id>)", youtube_links)
    check(V, "VS Code licence wording is precise (Code - OSS is MIT; the Microsoft build has its own free licence)", vscode_licence_wording)
    check(V, "macOS shortcut (Cmd) and 'open a new terminal after installing' are mentioned", vscode_mac_shortcuts)
    check("week0/*.md", "no VitePress-only syntax", no_vitepress_syntax)
    check("week0/*.md", "all local images exist", local_images_exist)
    check("week0/*.md", "code fences are opened/closed cleanly (no [Label], no indentation)", fences_clean)
    check("week0/*.md", "no heading is directly followed by a same-level heading (empty section)", no_empty_sections)

    wrong = [f for ok, f in RESULTS if not ok]
    print("=" * 78)
    print(f"{len(RESULTS)} checks, {len(RESULTS) - len(wrong)} OK, {len(wrong)} WRONG")
    if wrong:
        print("files with WRONG statements:", ", ".join(sorted(set(wrong))))
    print("\nNOT VERIFIABLE HERE (statements kept because they are standard/documented, but not executed):")
    for s in SKIPPED + [
        "Windows: `.\\env_name\\Scripts\\activate` in cmd and PowerShell (the note's screenshot shows it working in PowerShell), the PowerShell execution-policy error, "
        "'Add python.exe to PATH' wording, PATH needing a new terminal, `echo %errorlevel%`, `py` launcher (needs Windows)",
        "doc links/anchors on docs.python.org, pip.pypa.io, code.visualstudio.com and every YouTube video title/ID (these sites are blocked from this sandbox)",
        "VS Code: menu/shortcut names (View > Terminal, Ctrl+`, Ctrl/Cmd+Shift+X), the macOS 'Install code command in PATH' action and the licence text (needs the VS Code docs)",
        "Debian/Ubuntu package names python3-pip / python3-venv (needs apt on Debian)",
    ]:
        print("  -", s)
    sys.exit(1 if wrong else 0)
