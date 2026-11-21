"""
Week 7 notes -- claim checker.

Every check takes statements, numbers or code from the week7 notes, runs them for real and reports
whether the notes are right:

    OK     -> the notes say what actually happens
    WRONG  -> the notes say something that does not happen (the evidence shows what does)

What is executed:

    7-data-search-algo.md ...... step counts, growth table, binary-search traces, BST / hash-table behaviour,
                                 list resizing, timing ratios of `in list` / bisect / `in set`
    7-memory-architecture.md ... bandwidth / average-access-time / latency-scaling / disk-rotation arithmetic,
                                 the cache-locality experiment, the figures of the lecture slides
    7-SQL-web.md ............... SQLite query plans (EXPLAIN QUERY PLAN) for every index claim, index timing and write
                                 cost, the JOIN example, Redis commands (fakeredis), MongoDB queries (mongomock),
                                 sharding and replication-lag examples
    7-web-security.md .......... SQL injection against a real SQLite database and a Flask login route, parameterised
                                 queries, SQLAlchemy bound parameters vs text() f-strings, password hashing, a TLS
                                 server with a recording "eavesdropper", certificate and hostname verification
    7-logging.md ............... the code blocks of the note are extracted and run (files / console / e-mail output)
    debugging.md ............... traceback, breakpoint() / pdb, flask shell, FLASK_ENV vs --debug, the Werkzeug debugger
    all files .................. GitHub-markdown hygiene, links and anchors, tables, mermaid (MERMAID_JS=...)

Run (from anywhere):
    pip install flask flask-sqlalchemy fakeredis mongomock aiosmtpd flask-mail numpy matplotlib
    python week7/verify_week7_claims.py [-v]

Optional: MERMAID_JS=/path/to/mermaid.min.js (needs node + playwright) renders the mermaid diagrams;
MAKE_SHOT=1 regenerates static/week7-growth-rates.png.  A check whose tool is missing is skipped and listed at the end.
Checked against CPython 3.13, Flask 3.1, SQLite 3.5x, OpenSSL 3, curl 8.

The timing checks compare *ratios* with generous limits (the absolute times depend on the machine).
"""
import contextlib
import hashlib
import http.client
import http.server
import json
import math
import os
import random
import re
import shutil
import signal
import socket
import sqlite3
import ssl
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
ROOT = HERE.parent
NOTES = Path(os.environ.get("NOTES_DIR", HERE))
RESULTS, SKIPPED = [], []
VERBOSE = "-v" in sys.argv


def check(file, claim, fn):
    try:
        ok, evidence = fn()
    except Exception as e:                         # a crash is a WRONG result, with the reason
        ok, evidence = False, f"raised {type(e).__name__}: {str(e).splitlines()[0][:200] if str(e) else ''}"
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


def run_py(code, cwd=None, env=None, stdin=None, name="t.py", args=()):
    d = Path(cwd or tempfile.mkdtemp(prefix="w7"))
    (d / name).write_text(textwrap.dedent(code))
    p = subprocess.run([sys.executable, name, *args], cwd=d, capture_output=True, text=True, input=stdin, env=dict(os.environ, **(env or {})), timeout=120)
    return d, p


def read(d, f="app.log"):
    p = Path(d) / f
    return p.read_text() if p.exists() else ""


TS = r"\d{4}-\d\d-\d\d \d\d:\d\d:\d\d,\d{3}"


def strip_ts(s):
    return re.sub(TS, "<ts>", s)


# =========================================================================== #
# 7-data-search-algo.md
# =========================================================================== #
def big_o_numbers():
    t = note("7-data-search-algo.md")

    def binary_steps(n, target):
        lo, hi, steps = 0, n - 1, 0
        while lo <= hi:
            steps += 1
            mid = (lo + hi) // 2
            if mid == target:
                return steps
            lo, hi = (mid + 1, hi) if mid < target else (lo, mid - 1)
        return steps
    worst = max(binary_steps(10 ** 6, x) for x in random.Random(1).sample(range(10 ** 6), 3000) + [0, 999_999])
    steps = {n: math.floor(math.log2(n)) + 1 for n in (10 ** 6, 10 ** 9, 2 * 10 ** 6)}
    rows = {n: (math.log2(n), n, n * math.log2(n), n ** 2, n ** 3, 2 ** n) for n in (1, 2, 4, 8, 16, 32, 64)}
    matmul = [sum(1 for _ in range(n) for _ in range(n) for _ in range(n)) for n in (10, 20, 40)]
    from itertools import combinations
    n_subsets = {n: sum(1 for r in range(n + 1) for _ in combinations(range(n), r)) for n in (10, 16)}
    calls = {}

    def fib(n):
        calls[n_] += 1
        return n if n < 2 else fib(n - 1) + fib(n - 2)
    for n_ in (10, 20, 25):
        calls[n_] = 0
        fib(n_)
    from functools import lru_cache
    memo = {"calls": 0}

    @lru_cache(None)
    def fibm(n):
        memo["calls"] += 1
        return n if n < 2 else fibm(n - 1) + fibm(n - 2)
    fibm(60)
    ratio = (calls[25] / calls[20]) ** (1 / 5)
    ok = (worst == 20 and steps == {10 ** 6: 20, 10 ** 9: 30, 2 * 10 ** 6: 21} and rows[64][5] == 18_446_744_073_709_551_616 and rows[32][5] == 4_294_967_296 and rows[64][3] == 4096 and rows[64][4] == 262_144
          and rows[16][2] == 64 and rows[64][2] == 384 and matmul == [1000, 8000, 64000] and matmul[2] // matmul[1] == 8 and n_subsets == {10: 1024, 16: 65536}
          and (calls[10], calls[20], calls[25]) == (177, 21891, 242785) and abs(ratio - 1.618) < 0.005 and memo["calls"] == 61 and round(math.log2(10 ** 6)) == 20)
    good = all(s in t for s in ("18,446,744,073,709,551,616", "4,294,967,296", "needs at most **20** steps", "$10^9$ elements need only **30**", "and $2{,}000{,}000$ need 21", "**20** for $10^6$ and **30** for $10^9$", "8{,}000", "64{,}000", "177", "21,891", "242,785", "**61**", "$1.618$"))
    return ok and good, (f"binary search over 10^6 sorted numbers: worst case {worst} comparisons (floor(log2 N)+1 = {steps[10 ** 6]}); 10^9 -> {steps[10 ** 9]}; 2x10^6 -> {steps[2 * 10 ** 6]}; the growth table row N=64: "
                         f"{rows[64][5]:,} for 2^N; naive matmul steps {matmul} (x8 when N doubles); subsets {n_subsets}; fib calls {calls} (x{ratio:.3f} per +1); memoised fib(60) -> {memo['calls']} calls; notes show them: {good}")


def search_and_arrays():
    import bisect
    t = note("7-data-search-algo.md")

    def trace(a, x):
        lo, hi, rows = 0, len(a) - 1, []
        while lo <= hi:
            mid = (lo + hi) // 2
            rows.append((len(rows) + 1, lo, hi, mid, a[mid]))
            if a[mid] == x:
                return rows, mid
            lo, hi = (mid + 1, hi) if a[mid] < x else (lo, mid - 1)
        return rows, -1
    a = [3, 8, 15, 23, 42, 57, 61, 90]
    r57, p57 = trace(a, 57)
    r10, p10 = trace(a, 10)
    lst = list(range(0, 2000, 2))
    pos = bisect.bisect_left(lst, 1)
    shift_front = len(lst) - pos
    shift_end = len(lst) - bisect.bisect_left(lst, 1999)
    sizes, l, last = [], [], sys.getsizeof([])
    for i in range(40):
        l.append(i)
        s = sys.getsizeof(l)
        if s != last:
            sizes.append(len(l))
            last = s
    data = list(range(200_000))
    s_ = set(data)

    def best(fn, rep=3, n=20):
        out = []
        for _ in range(rep):
            t0 = time.perf_counter()
            for _ in range(n):
                fn()
            out.append((time.perf_counter() - t0) / n)
        return min(out)
    t_lin = best(lambda: 199_999 in data, n=10)
    t_bin = best(lambda: bisect.bisect_left(data, 199_999), n=200)
    t_set = best(lambda: 199_999 in s_, n=200)
    ok = (r57 == [(1, 0, 7, 3, 23), (2, 4, 7, 5, 57)] and p57 == 5 and r10 == [(1, 0, 7, 3, 23), (2, 0, 2, 1, 8), (3, 2, 2, 2, 15)] and p10 == -1
          and shift_front == 999 and shift_end == 0 and sizes[0] == 1 and len(sizes) < 10 and (sys.version_info[:2] != (3, 13) or sizes == [1, 5, 9, 17, 25, 33])
          and t_lin / t_bin > 100 and t_lin / t_set > 100 and t_bin < 50e-6 and t_set < 50e-6)
    good = all(s in t for s in ("| **57** | 1 | 0 | 7 | 3 | 23 |", "| 2 | 4 | 7 | 5 | 57 |", "| 3 | 2 | 2 | 2 | 15 |", "shifts all 999 others", "1, 5, 9, 17, 25 and 33"))
    return ok and good, (f"trace for 57: {r57}; for 10: {len(r10)} steps -> not found; sorted insert at the front shifts {shift_front} of 1000 elements, at the end {shift_end}; list reallocations while appending 40 items: "
                         f"{sizes}; N=200,000: `in list` {t_lin * 1e6:.0f} us, bisect {t_bin * 1e6:.2f} us, `in set` {t_set * 1e6:.2f} us (ratios {t_lin / t_bin:.0f}x and {t_lin / t_set:.0f}x); notes show the traces: {good}")


def bst_and_hash():
    t = note("7-data-search-algo.md")

    class Nd:
        def __init__(s, k):
            s.k, s.l, s.r = k, None, None

    def ins(root, k):
        if root is None:
            return Nd(k)
        cur = root
        while True:
            if k < cur.k:
                if cur.l is None:
                    cur.l = Nd(k)
                    break
                cur = cur.l
            else:
                if cur.r is None:
                    cur.r = Nd(k)
                    break
                cur = cur.r
        return root

    def height(root):
        h, level = 0, [root] if root else []
        while level:
            h += 1
            level = [c for n in level for c in (n.l, n.r) if c]
        return h

    def path(r, k):
        p = []
        while r:
            p.append(r.k)
            if k == r.k:
                return p
            r = r.l if k < r.k else r.r
        return p + ["not found"]

    def inorder(r):
        return inorder(r.l) + [r.k] + inorder(r.r) if r else []
    root = None
    for k in (50, 30, 70, 20, 40, 60, 80):
        root = ins(root, k)
    r = None
    for k in range(1000):
        r = ins(r, k)
    h_sorted = height(r)
    ks = list(range(1000))
    random.Random(1).shuffle(ks)
    r = None
    for k in ks:
        r = ins(r, k)
    h_random = height(r)

    class Bad:
        def __init__(self, v): self.v = v
        def __hash__(self): return 42
        def __eq__(self, o): return self.v == o.v
    ratios = []
    for n in (500, 1000, 2000):
        good_d, bad_d = {i: i for i in range(n)}, {Bad(i): i for i in range(n)}
        keys = [Bad(i) for i in range(n)]
        t0 = time.perf_counter()
        [good_d[i] for i in range(n)]
        tg = time.perf_counter() - t0
        t0 = time.perf_counter()
        [bad_d[k] for k in keys]
        tb = time.perf_counter() - t0
        ratios.append(tb / tg)
    ok = (path(root, 60) == [50, 70, 60] and path(root, 45) == [50, 30, 40, "not found"] and inorder(root) == [20, 30, 40, 50, 60, 70, 80] and h_sorted == 1000 and 10 <= h_random <= 35
          and (10 % 8, 13 % 8, 18 % 8) == (2, 5, 2) and ratios[0] > 50 and ratios[2] > ratios[0] * 2)
    good = all(s in t for s in ("**3 comparisons**", "20, 30, 40, 50, 60, 70, 80", "the height was **1,000**", "key 10 -> index 2", "10 and 18 both give 2"))
    return ok and good, (f"BST of the note: search 60 -> {path(root, 60)}, search 45 -> {path(root, 45)}, in-order {inorder(root)}; 1,000 keys: height {h_sorted} (sorted insertion) vs {h_random} (random order); "
                         f"hash table: 10 mod 8 = 2, 13 mod 8 = 5, 18 mod 8 = 2; all-colliding keys are {ratios[0]:.0f}x, {ratios[1]:.0f}x, {ratios[2]:.0f}x slower for 500 / 1000 / 2000 keys; notes say so: {good}")


def growth_chart():
    path = ROOT / "static" / "week7-growth-rates.png"
    if os.environ.get("MAKE_SHOT"):
        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
            import numpy as np
        except ImportError:
            SKIPPED.append("growth chart not regenerated (matplotlib / numpy missing)")
        else:
            n = np.arange(2, 31)
            fig, ax = plt.subplots(figsize=(7.2, 4.4), dpi=200)
            for label, y, c in [(r"$\log_2 N$", np.log2(n), "#1b9e77"), (r"$N$", n, "#377eb8"), (r"$N\log_2 N$", n * np.log2(n), "#7570b3"), (r"$N^2$", n ** 2, "#b8860b"), (r"$2^N$", 2.0 ** n, "#d95f02")]:
                ax.plot(n, y, color=c, lw=2)
                ax.annotate(label, (n[-1], y[-1]), textcoords="offset points", xytext=(6, 0), va="center", color=c, fontsize=11, fontweight="bold")
            ax.set_yscale("log")
            ax.set_xlim(2, 34)
            ax.set_ylim(0.8, 3e9)
            ax.set_xlabel("input size N")
            ax.set_ylabel("number of steps (log scale)")
            ax.set_title("How the number of steps grows with N", fontsize=11)
            ax.grid(True, which="major", alpha=0.25)
            for s in ("top", "right"):
                ax.spines[s].set_visible(False)
            fig.tight_layout()
            fig.savefig(path)
    t = note("7-data-search-algo.md")
    return path.exists() and path.stat().st_size > 5000 and "../static/week7-growth-rates.png" in t, f"the growth-rate picture exists ({path.stat().st_size if path.exists() else 0} bytes) and is used by the note"


# =========================================================================== #
# 7-memory-architecture.md
# =========================================================================== #
def memory_numbers():
    t = note("7-memory-architecture.md")
    bw = 800e6 * 2 * 8 * 2 / 1e9
    bw1 = 800e6 * 2 * 8 * 1 / 1e9
    amat = lambda hit, miss, pen: hit + miss * pen
    rows = [amat(1, 0, 100), amat(1, 0.01, 100), amat(1, 0.05, 100), amat(1, 1, 100)]
    scale = {k: v / 1e-9 for k, v in {"dram": 100e-9, "ssd": 100e-6, "hdd": 10e-3}.items()}
    rot = 60 / 7200 * 1000
    q1, q2 = amat(2, 0.10, 80), 1000e6 * 2 * 8 * 2 / 1e9
    ok = (abs(bw - 25.6) < 1e-9 and abs(bw1 - 12.8) < 1e-9 and [round(x, 6) for x in rows] == [1, 2, 6, 101] and round(scale["dram"], 6) == 100 and round(scale["ssd"] / 86400, 2) == 1.16
          and round(scale["hdd"] / 86400) == 116 and round(rot, 2) == 8.33 and round(rot / 2, 2) == 4.17 and abs(q1 - 10) < 1e-9 and q2 == 32 and rows[2] / rows[0] == 6)
    good = all(s in t for s in ("25.6", "12.8 GB/s", "**2 ns**", "**6 ns**", "101 ns", "about **100 seconds**" if False else "**100 seconds**", "**1.2 days**", "**116 days**", "= 8.33$ ms", "**4.17 ms**", "**10 ns**", "**32 GB/s**", "six times slower"))
    return ok and good, (f"DDR3-1600 dual channel = {bw:g} GB/s (one channel {bw1:g}); average access time for miss rates 0/1/5/100 % = {rows}; if L1 = 1 s: DRAM {scale['dram']:g} s, SSD {scale['ssd'] / 86400:.2f} days, "
                         f"HDD {scale['hdd'] / 86400:.0f} days; one rotation at 7,200 rpm = {rot:.2f} ms (average wait {rot / 2:.2f} ms); practice answers {q1:g} ns and {q2:g} GB/s; notes show them: {good}")


def slide_figures():
    t = note("7-memory-architecture.md")
    figs = ["10s-100s of bytes", "0.1-1 MB", "0.1-10 GB", "1-100 GB", "0.1-10 TB", "48 hours", "`Register < SRAM < DRAM < SSD < HDD`", "`DRAM > SSD > HDD`", "`HDD > SSD > DRAM > SRAM > Registers`"]
    missing = [f for f in figs if f not in t]
    return not missing, f"the figures and orderings of the lecture slides (registers 10s-100s of bytes, SRAM 0.1-1 MB, DRAM 0.1-10 GB, SSD 1-100 GB, HDD 0.1-10 TB, cold storage up to 48 hours, the latency / throughput / density orders) are in the note; missing: {missing or 'none'}"


def locality_experiment():
    try:
        import numpy as np
    except ImportError:
        SKIPPED.append("cache-locality experiment skipped (numpy missing)")
        return True, "skipped (numpy not installed)"
    n = 4000
    a = np.random.rand(n, n)

    def best(fn, rep=3):
        out = []
        for _ in range(rep):
            t0 = time.perf_counter()
            fn()
            out.append(time.perf_counter() - t0)
        return min(out)
    by_rows = lambda: sum(a[i, :].sum() for i in range(n))
    by_cols = lambda: sum(a[:, j].sum() for j in range(n))
    tr, tc = best(by_rows), best(by_cols)
    L = a[:1500, :1500].tolist()
    lr = best(lambda: sum(sum(r) for r in L))
    lc = best(lambda: sum(sum(L[i][j] for i in range(1500)) for j in range(1500)))
    t = note("7-memory-architecture.md")
    same = abs(by_rows() - by_cols()) < 1e-6 * by_rows()
    return same and tc / tr > 1.1 and lc / lr > 1.5 and a.strides == (n * 8, 8) and "jumps 32,000 bytes" in t and "3.6 times slower" in t, (
        f"summing a {n}x{n} array: by rows {tr * 1000:.1f} ms, by columns {tc * 1000:.1f} ms (x{tc / tr:.1f}); python lists of lists x{lc / lr:.1f}; both give the same total ({same}); the note's own measurement is quoted: {'3.6 times slower' in t}")


# =========================================================================== #
# 7-SQL-web.md
# =========================================================================== #
def _plan(con, sql):
    return [r[3] for r in con.execute("EXPLAIN QUERY PLAN " + sql)]


def sqlite_index_claims():
    t = note("7-SQL-web.md")
    con = sqlite3.connect(":memory:")
    con.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, age INTEGER, city TEXT)")
    rnd = random.Random(0)
    names = ["Yash", "Yashvi", "Puneet", "Baskaran", "Alice", "Bob", "Kittu", "Carol", "Yasmin", "Zoya"]
    con.executemany("INSERT INTO users VALUES (?,?,?,?)", [(i, rnd.choice(names) + str(i), rnd.randint(15, 60), rnd.choice("ABCDE")) for i in range(1, 200_001)])
    q = "SELECT * FROM users WHERE name = 'Yash5'"
    before = _plan(con, q)

    def timeit(sql, n=10):
        t0 = time.perf_counter()
        for _ in range(n):
            con.execute(sql).fetchall()
        return (time.perf_counter() - t0) / n
    t_scan = timeit(q)
    con.execute("CREATE INDEX idx_name ON users(name)")
    after = _plan(con, q)
    t_idx = timeit(q, 200)
    p = {k: _plan(con, v) for k, v in {
        "like": "SELECT * FROM users WHERE name LIKE 'Yas%'", "like_any": "SELECT * FROM users WHERE name LIKE '%Yas%'",
        "range": "SELECT * FROM users WHERE name >= 'Yas' AND name < 'Yat'", "glob": "SELECT * FROM users WHERE name GLOB 'Yas*'"}.items()}
    con.execute("CREATE INDEX idx_name_nc ON users(name COLLATE NOCASE)")
    p["like_nc"] = _plan(con, "SELECT * FROM users WHERE name LIKE 'Yas%'")
    p["like_any_nc"] = _plan(con, "SELECT * FROM users WHERE name LIKE '%Yas%'")
    con.execute("CREATE INDEX idx_age ON users(age)")
    p["between"] = _plan(con, "SELECT * FROM users WHERE age BETWEEN 20 AND 30")
    p["expr"] = _plan(con, "SELECT * FROM users WHERE age + 1 = 31")
    p["eq_age"] = _plan(con, "SELECT * FROM users WHERE age = 30")
    p["order"] = _plan(con, "SELECT * FROM users ORDER BY age LIMIT 5")
    try:
        con.execute("CREATE INDEX h ON users USING HASH (name)")
        hash_err = "no error"
    except sqlite3.OperationalError:
        hash_err = "syntax error"
    con.execute("CREATE TABLE t (a INT, b INT, c INT, d INT)")
    con.executemany("INSERT INTO t VALUES (?,?,?,?)", [(rnd.randint(1, 20), rnd.randint(1, 50), rnd.randint(1, 100), i) for i in range(50_000)])
    con.execute("CREATE INDEX idx_abc ON t(a, b, c)")
    comp = {w: _plan(con, f"SELECT * FROM t WHERE {w}") for w in ("a=1 AND b=2 AND c=3", "a=1 AND b=2", "a=1", "a=1 AND c=3", "b=2", "b=2 AND c=3")}
    con.execute("ANALYZE")
    skip = _plan(con, "SELECT * FROM t WHERE b=2")
    # write cost
    con.execute("CREATE TABLE w0 (id INTEGER PRIMARY KEY, a INT, b INT, c INT)")
    con.execute("CREATE TABLE w3 (id INTEGER PRIMARY KEY, a INT, b INT, c INT)")
    for c_ in "abc":
        con.execute(f"CREATE INDEX w3{c_} ON w3({c_})")
    data = [(i, rnd.randint(0, 10 ** 6), rnd.randint(0, 10 ** 6), rnd.randint(0, 10 ** 6)) for i in range(100_000)]
    t0 = time.perf_counter()
    con.executemany("INSERT INTO w0 VALUES (?,?,?,?)", data)
    t0w = time.perf_counter() - t0
    t0 = time.perf_counter()
    con.executemany("INSERT INTO w3 VALUES (?,?,?,?)", data)
    t3w = time.perf_counter() - t0
    fan = {f: (f ** 3, math.ceil(math.log(1e9, f))) for f in (100, 500)}
    ok = (before == ["SCAN users"] and after == ["SEARCH users USING INDEX idx_name (name=?)"] and t_scan / t_idx > 20
          and p["like"] == ["SCAN users"] and p["like_any"] == ["SCAN users"] and p["range"] == ["SEARCH users USING INDEX idx_name (name>? AND name<?)"] and p["glob"] == p["range"]
          and p["like_nc"] == ["SEARCH users USING INDEX idx_name_nc (name>? AND name<?)"] and p["like_any_nc"] == ["SCAN users"]
          and p["between"] == ["SEARCH users USING INDEX idx_age (age>? AND age<?)"] and p["expr"] == ["SCAN users"] and p["eq_age"] == ["SEARCH users USING INDEX idx_age (age=?)"]
          and p["order"] == ["SCAN users USING INDEX idx_age"] and hash_err == "syntax error"
          and comp["a=1 AND b=2 AND c=3"] == ["SEARCH t USING INDEX idx_abc (a=? AND b=? AND c=?)"] and comp["a=1 AND b=2"] == ["SEARCH t USING INDEX idx_abc (a=? AND b=?)"]
          and comp["a=1"] == ["SEARCH t USING INDEX idx_abc (a=?)"] and comp["a=1 AND c=3"] == ["SEARCH t USING INDEX idx_abc (a=?)"] and comp["b=2"] == ["SCAN t"] and comp["b=2 AND c=3"] == ["SCAN t"]
          and "ANY(a)" in skip[0] and t3w / t0w > 2 and fan == {100: (1_000_000, 5), 500: (125_000_000, 4)})
    good = all(s in t for s in ("`SCAN users` (reads all 200,000 rows)", "`SEARCH users USING INDEX idx_name (name=?)`", "(plain index is not used)",
                                "-- SEARCH users USING INDEX idx_name_nc (name>? AND name<?)", "`SCAN t` (full scan)", "`SEARCH ... (a=?)`", "SQLite has no hash index", "$100^3 = 1{,}000{,}000$", "more than $10^9$ rows"))
    return ok and good, (f"200,000 rows: without index {before}, with index {after}, scan/index time ratio {t_scan / t_idx:.0f}x; LIKE 'Yas%' on a plain index -> {p['like']}, on a NOCASE index -> {p['like_nc']}, range rewrite and GLOB use the index; "
                         f"'%Yas%' always scans; BETWEEN {p['between']}; age + 1 = 31 -> {p['expr']}; ORDER BY uses the index order: {p['order']}; USING HASH -> {hash_err}; compound index (a,b,c): "
                         f"{ {k: ('scan' if v[0].startswith('SCAN') else v[0].split('(')[1][:-1]) for k, v in comp.items()} }; after ANALYZE b=2 -> {skip[0].split('INDEX ')[1]}; 100,000 inserts: {t0w:.3f}s vs {t3w:.3f}s with 3 indexes (x{t3w / t0w:.1f}); "
                         f"B-tree fanout arithmetic {fan}; notes show these plans: {good}")


def sql_join_and_nosql():
    t = note("7-SQL-web.md")
    c2 = sqlite3.connect(":memory:")
    c2.executescript("""
    CREATE TABLE Users (user_id TEXT PRIMARY KEY, name TEXT);
    CREATE TABLE Books (book_id TEXT PRIMARY KEY, title TEXT);
    CREATE TABLE Borrow (user_id TEXT, book_id TEXT);
    INSERT INTO Users VALUES ('1','Baskaran'),('2','Puneet');
    INSERT INTO Books VALUES ('B1','DBMS'),('B2','Python');
    INSERT INTO Borrow VALUES ('1','B1'),('1','B2'),('2','B1');
    """)
    join = c2.execute("SELECT u.name, b.title FROM Users u JOIN Borrow br ON u.user_id = br.user_id JOIN Books b ON b.book_id = br.book_id WHERE u.user_id = '1'").fetchall()
    out = {"join": join}
    try:
        import fakeredis
        import mongomock
    except ImportError:
        SKIPPED.append("Redis / MongoDB examples skipped (fakeredis / mongomock missing)")
        return join == [("Baskaran", "DBMS"), ("Baskaran", "Python")], f"only the SQL join was run: {join}"
    r = fakeredis.FakeStrictRedis(decode_responses=True)
    r.execute_command("SET", "user:1", '{"name": "Puneet", "books": ["B1", "B2"]}')
    out["get"] = r.execute_command("GET", "user:1")
    r.execute_command("SET", "session:9", "x", "EX", "30")
    out["ttl"] = r.ttl("session:9")
    out["by_value"] = r.keys("*Puneet*")
    db = mongomock.MongoClient().library
    db.users.insert_many([{"user_id": "1", "name": "Baskaran", "books": [{"book_id": "B1", "title": "DBMS"}, {"book_id": "B2", "title": "Python"}]},
                          {"user_id": "2", "name": "Puneet", "books": [{"book_id": "B1", "title": "DBMS"}]}])
    out["find_one_user"] = [d["name"] for d in db.users.find({"user_id": "1"})]
    out["find_by_title"] = sorted(d["name"] for d in db.users.find({"books.title": "DBMS"}))
    db2 = mongomock.MongoClient().college
    db2.students.insert_many([{"student_id": "S1", "name": "Asha", "hostel": {"block": "B", "mess": "Mess-2"}}, {"student_id": "S2", "name": "Ravi", "day_scholar": {"vehicle_gate_pass": "GP-17"}}])
    out["shapes"] = [sorted(set(d) - {"_id"}) for d in db2.students.find({})]
    out["s2"] = [d["name"] for d in db2.students.find({"student_id": "S2"})]
    # duplicated title in the document design
    out["dup_titles"] = sum(1 for d in db.users.find({}) for b in d["books"] if b["title"] == "DBMS")
    ok = (join == [("Baskaran", "DBMS"), ("Baskaran", "Python")] and out["get"] == '{"name": "Puneet", "books": ["B1", "B2"]}' and 0 < out["ttl"] <= 30 and out["by_value"] == []
          and out["find_one_user"] == ["Baskaran"] and out["find_by_title"] == ["Baskaran", "Puneet"] and out["shapes"] == [["hostel", "name", "student_id"], ["day_scholar", "name", "student_id"]]
          and out["s2"] == ["Ravi"] and out["dup_titles"] == 2)
    good = all(s in t for s in ("`Baskaran / DBMS` and `Baskaran / Python`", "duplicated data", "The book title `DBMS` is stored inside the document of *every* user", 'db.users.find({ user_id: "1" })', "SET session:9", "EX 30",
                                "MEAN(books_borrowed)", "memcached"))
    bad = "No data duplication possible" in t
    return ok and good and not bad, (f"join -> {join}; Redis GET -> {out['get']}, TTL {out['ttl']}, searching the value with KEYS finds {out['by_value']} (keys only); MongoDB: user 1 -> {out['find_one_user']}, books.title DBMS -> {out['find_by_title']}; "
                                     f"documents of different shape in one collection: {out['shapes']}; the title DBMS is stored {out['dup_titles']} times (duplication); the old wrong claim 'No data duplication possible' is gone: {not bad}; notes say: {good}")


def sharding_and_replication():
    t = note("7-SQL-web.md")
    shard_range = lambda u: 1 if u <= 1000 else 2
    shard_hash = lambda u, n=3: u % n
    primary, replica, log = {}, {}, []

    def write(k, v, at):
        primary[k] = v
        log.append((at, k, v))

    def replicate(upto):
        for at, k, v in log:
            if at <= upto:
                replica[k] = v
    write("balance", 100, 0)
    replicate(0)
    write("balance", 80, 1)
    t1 = (primary["balance"], replica["balance"])
    replicate(2)
    t2 = (primary["balance"], replica["balance"])
    ok = ([shard_range(u) for u in (1, 1000, 1001, 2000)] == [1, 1, 2, 2] and [shard_hash(u) for u in range(1, 8)] == [1, 2, 0, 1, 2, 0, 1] and t1 == (80, 100) and t2 == (80, 80))
    good = all(s in t for s in ("ids 1, 2, 3, 4, 5, 6, 7 go to shards 1, 2, 0, 1, 2, 0, 1 with three shards", "| t = 1: balance set to 80 | balance = **80** | still 100 (copy not arrived) | **100** (stale) |", "| t = 2: copy arrives | 80 | **80** | 80 |"))
    return ok and good, f"range sharding 1/1000/1001/2000 -> {[shard_range(u) for u in (1, 1000, 1001, 2000)]}; hash sharding of ids 1..7 on 3 shards -> {[shard_hash(u) for u in range(1, 8)]}; replica lag: t=1 primary/replica {t1}, t=2 {t2}; notes show them: {good}"


def cap_and_slide_wording():
    t = note("7-SQL-web.md")
    wrong = ["(success or failure)", "No data duplication possible", "Memcache,", "grafana\n", "impossible to guarantee all three properties simultaneously"]
    present = [s for s in wrong if s in t]
    need = ["non-error", "must choose between consistency and availability", "is **not** the \"C\" of ACID", "Not only SQL", "**Long text fields and binary data are not good index columns.**", "only possible **without partitions**",
            "Redundancy** means keeping", "**Replication** means", "eventual consistency"]
    missing = [s for s in need if s not in t]
    return not present and not missing, f"corrected statements (availability = a non-error answer, a choice only during a partition, C of CAP is not C of ACID, no 'no duplication' claim) present; old wrong wording still there: {present or 'none'}; missing: {missing or 'none'}"


# =========================================================================== #
# 7-web-security.md
# =========================================================================== #
def sql_injection():
    t = note("7-web-security.md")
    con = sqlite3.connect(":memory:")
    con.executescript("""
    CREATE TABLE Users (id INTEGER PRIMARY KEY, Name TEXT, Pass TEXT, role TEXT);
    INSERT INTO Users (Name, Pass, role) VALUES ('admin', 's3cret', 'admin'), ('alice', 'pw1', 'user'), ('bob', 'pw2', 'user');
    """)

    def bad(name, pswd):
        sql = 'SELECT * FROM Users WHERE Name ="' + name + '" AND Pass ="' + pswd + '"'
        return sql, con.execute(sql).fetchall()

    def good_(name, pswd):
        return con.execute("SELECT * FROM Users WHERE Name = ? AND Pass = ?", (name, pswd)).fetchall()
    s1, r1 = bad("abcd", "pass")
    s2, r2 = bad('" or ""="', '" or ""="')
    s3, r3 = bad('admin" --', "anything")
    try:
        con.execute('SELECT * FROM Users WHERE Name ="' + 'x"; DROP TABLE Users; --' + '" AND Pass =""')
        stacked = "no error"
    except sqlite3.Error as e:
        stacked = f"{type(e).__name__}: {e}"
    still = con.execute("SELECT count(*) FROM Users").fetchone()[0]
    union = con.execute("SELECT id, Name FROM Users WHERE Name = '" + "x' UNION SELECT id, Pass FROM Users --" + "'").fetchall()
    numeric = con.execute("SELECT Name FROM Users WHERE id = " + "1 OR 1=1").fetchall()
    safe = [good_("abcd", "pass"), good_('" or ""="', '" or ""="'), good_("admin' --", "x"), good_("alice", "pw1")]
    obrien = con.execute("SELECT ?", ("O'Brien",)).fetchone()[0]
    try:
        con.execute("SELECT * FROM ?", ("Users",))
        table_param = "no error"
    except sqlite3.OperationalError:
        table_param = "syntax error"
    ok = (s1 == 'SELECT * FROM Users WHERE Name ="abcd" AND Pass ="pass"' and r1 == [] and s2 == 'SELECT * FROM Users WHERE Name ="" or ""="" AND Pass ="" or ""=""' and len(r2) == 3 and r2[0][1] == "admin"
          and s3 == 'SELECT * FROM Users WHERE Name ="admin" --" AND Pass ="anything"' and r3 == [(1, "admin", "s3cret", "admin")] and "You can only execute one statement at a time" in stacked and still == 3
          and union == [(1, "s3cret"), (2, "pw1"), (3, "pw2")] and len(numeric) == 3 and safe[:3] == [[], [], []] and len(safe[3]) == 1 and obrien == "O'Brien" and table_param == "syntax error")
    texts = all(s in t for s in ('SELECT * FROM Users WHERE Name ="" or ""="" AND Pass ="" or ""=""', 'SELECT * FROM Users WHERE Name ="admin" --" AND Pass ="anything"', "all three users are returned", "ProgrammingError: You can only execute one statement at a time",
                                 "returns **all passwords**", 'SELECT * FROM Users WHERE Name ="x"; DROP TABLE Users; --" AND Pass =""', "`1 OR 1=1`", "`SELECT * FROM ?` is a syntax error"))
    return ok and texts, (f"login with normal input -> {len(r1)} rows; `\" or \"\"=\"` -> {len(r2)} rows (first user {r2[0][1]}); `admin\" --` -> logged in as {r3[0][1]}; '; DROP TABLE' -> {stacked.split(':')[0]} and the table still has {still} rows; "
                         f"UNION leaks {[x[1] for x in union]}; `1 OR 1=1` returns {len(numeric)} users; parameterised: attacks -> {safe[:3]}, normal login -> {len(safe[3])} row, O'Brien stays {obrien!r}; table names cannot be parameters ({table_param}); notes show them: {texts}")


def orm_and_flask_demo():
    from flask import Flask, request
    from sqlalchemy import String, create_engine, select, text
    from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column
    t = note("7-web-security.md")

    class Base(DeclarativeBase):
        pass

    class User(Base):
        __tablename__ = "users"
        id: Mapped[int] = mapped_column(primary_key=True)
        name: Mapped[str] = mapped_column(String(30))
        pw: Mapped[str] = mapped_column(String(30))
    eng = create_engine("sqlite://")
    Base.metadata.create_all(eng)
    evil = "' OR '1'='1"
    with Session(eng) as s:
        s.add_all([User(name="admin", pw="s3cret"), User(name="alice", pw="pw1")])
        s.commit()
        orm = s.scalars(select(User).where(User.name == evil)).all()
        stmt = select(User).where(User.name == evil)
        compiled = " ".join(str(stmt.compile()).split())
        params = stmt.compile().params
        raw_f = s.execute(text(f"SELECT name FROM users WHERE name = '{evil}'")).all()
        raw_b = s.execute(text("SELECT name FROM users WHERE name = :n"), {"n": evil}).all()
    # a Flask login route, vulnerable and safe, attacked over real HTTP with curl
    con = sqlite3.connect(":memory:", check_same_thread=False)
    con.executescript("CREATE TABLE Users (id INTEGER PRIMARY KEY, Name TEXT, Pass TEXT); INSERT INTO Users (Name, Pass) VALUES ('admin','s3cret'),('alice','pw1');")
    app = Flask("sqli")

    @app.route("/login", methods=["POST"])
    def login():
        name, pswd = request.form["name"], request.form["password"]
        rows = con.execute('SELECT * FROM Users WHERE Name ="' + name + '" AND Pass ="' + pswd + '"').fetchall()
        return ("Welcome " + rows[0][1]) if rows else ("Login failed", 401)

    @app.route("/login-safe", methods=["POST"])
    def login_safe():
        rows = con.execute("SELECT * FROM Users WHERE Name = ? AND Pass = ?", (request.form["name"], request.form["password"])).fetchall()
        return ("Welcome " + rows[0][1]) if rows else ("Login failed", 401)
    attack = {"name": '" or ""="', "password": '" or ""="'}
    c = app.test_client()
    bad_resp, safe_resp = c.post("/login", data=attack).get_data(as_text=True), c.post("/login-safe", data=attack).status_code
    curl_out = None
    if shutil.which("curl"):
        from werkzeug.serving import make_server
        port = free_port()
        srv = make_server("127.0.0.1", port, app)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        r1 = subprocess.run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "-X", "POST", f"http://127.0.0.1:{port}/login", "--data-urlencode", "name=" + "A" * 5000, "--data-urlencode", "password="], capture_output=True, text=True).stdout
        r2 = subprocess.run(["curl", "-s", "-X", "POST", f"http://127.0.0.1:{port}/login", "--data-urlencode", 'name=" or ""="', "--data-urlencode", 'password=" or ""="'], capture_output=True, text=True).stdout
        srv.shutdown()
        curl_out = (r1, r2)
    import re as _re

    def valid_username(s):
        return _re.fullmatch(r"[A-Za-z0-9_]{3,20}", s) is not None
    from werkzeug.security import check_password_hash, generate_password_hash
    h1, h2 = generate_password_hash("pw1"), generate_password_hash("pw1")
    sha_equal = hashlib.sha256(b"pw1").hexdigest() == hashlib.sha256(b"pw1").hexdigest()
    ok = (orm == [] and compiled == "SELECT users.id, users.name, users.pw FROM users WHERE users.name = :name_1" and params == {"name_1": evil} and len(raw_f) == 2 and raw_b == []
          and bad_resp == "Welcome admin" and safe_resp == 401 and (curl_out is None or curl_out == ("401", "Welcome admin")) and valid_username("alice_01") and not valid_username('" or ""="')
          and h1 != h2 and check_password_hash(h1, "pw1") and not check_password_hash(h1, "pw2") and h1.startswith("scrypt:") and sha_equal)
    good = all(s in t for s in ("WHERE users.name = :name_1", "INJECTABLE, returned 2 rows", "safe, returned 0 rows", "valid_username(\"alice_01\")` is `True`", "scrypt:32768:8:1$<random salt>$<hash>", "`scrypt`"))
    return ok and good, (f"SQLAlchemy ORM with the injection string -> {orm} (SQL: {compiled}, bound parameter {params}); text() with an f-string -> {len(raw_f)} rows (injectable), with a bound parameter -> {len(raw_b)}; Flask login attacked with the injection -> "
                         f"'{bad_resp}', safe version -> {safe_resp}; over real HTTP with curl: a 5000-character name is processed anyway (status {curl_out[0] if curl_out else 'n/a'}), the injection logs in as '{curl_out[1] if curl_out else 'n/a'}'; "
                         f"valid_username examples ok; two hashes of 'pw1' differ ({h1 != h2}) and verify, format {h1.split('$')[0]}; plain sha256 is identical every time ({sha_equal}); notes show them: {good}")


def xss_autoescape():
    from flask import Flask, render_template_string
    t = note("7-web-security.md")
    app = Flask("x")
    with app.test_request_context():
        out = render_template_string("{{ comment }}", comment="<script>alert(1)</script>")
        out_safe = render_template_string("{{ comment|safe }}", comment="<script>alert(1)</script>")
    return out == "&lt;script&gt;alert(1)&lt;/script&gt;" and out_safe == "<script>alert(1)</script>" and "&lt;script&gt;alert(1)&lt;/script&gt;" in t, f"Flask escapes {{{{ comment }}}} -> {out}; |safe does not -> {out_safe}"


def tls_claims():
    t = note("7-web-security.md")
    if not shutil.which("openssl"):
        SKIPPED.append("TLS demonstration skipped (openssl missing)")
        return True, "skipped (openssl not available)"
    d = Path(tempfile.mkdtemp(prefix="w7tls"))

    def make_cert(cn, san, name):
        subprocess.run(["openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes", "-keyout", str(d / f"{name}.key"), "-out", str(d / f"{name}.pem"), "-days", "2", "-subj", f"/CN={cn}", "-addext", f"subjectAltName={san}"],
                       capture_output=True, check=True)
    make_cert("localhost", "DNS:localhost,IP:127.0.0.1", "good")
    make_cert("other.example", "DNS:other.example", "other")

    class H(http.server.BaseHTTPRequestHandler):
        def do_POST(self):
            self.rfile.read(int(self.headers.get("Content-Length", 0)))
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"ok")

        def log_message(self, *a):
            pass
    servers = []

    def start(cert=None):
        port = free_port()
        s = http.server.HTTPServer(("127.0.0.1", port), H)
        if cert:
            ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            ctx.load_cert_chain(d / f"{cert}.pem", d / f"{cert}.key")
            s.socket = ctx.wrap_socket(s.socket, server_side=True)
        threading.Thread(target=s.serve_forever, daemon=True).start()
        servers.append(s)
        return port

    def proxy(target):
        log, ls = [], socket.socket()
        ls.bind(("127.0.0.1", 0))
        ls.listen(5)

        def pipe(a, b):
            try:
                while True:
                    data = a.recv(65536)
                    if not data:
                        break
                    log.append(data)
                    b.sendall(data)
            except OSError:
                pass
            finally:
                with contextlib.suppress(OSError):
                    b.shutdown(socket.SHUT_WR)

        def run():
            while True:
                try:
                    cs, _ = ls.accept()
                except OSError:
                    return
                up = socket.create_connection(("127.0.0.1", target))
                threading.Thread(target=pipe, args=(cs, up), daemon=True).start()
                threading.Thread(target=pipe, args=(up, cs), daemon=True).start()
        threading.Thread(target=run, daemon=True).start()
        return ls.getsockname()[1], log, ls
    p_http, p_tls, p_other = start(), start("good"), start("other")
    pp_http, log_http, ls1 = proxy(p_http)
    pp_tls, log_tls, ls2 = proxy(p_tls)
    time.sleep(0.3)
    body = "name=alice&password=TOPSECRET123"
    c = http.client.HTTPConnection("127.0.0.1", pp_http)
    c.request("POST", "/", body)
    c.getresponse().read()
    c.close()
    c = http.client.HTTPSConnection("localhost", pp_tls, context=ssl.create_default_context(cafile=str(d / "good.pem")))
    c.request("POST", "/", body)
    sock = c.sock
    version, cipher = sock.version(), sock.cipher()[0]
    c.getresponse().read()
    c.close()
    time.sleep(0.3)
    seen_http, seen_tls = b"".join(log_http), b"".join(log_tls)
    errors = {}
    for label, cafile, port in (("untrusted", None, p_tls), ("mismatch", str(d / "other.pem"), p_other)):
        try:
            cc = http.client.HTTPSConnection("localhost", port, context=ssl.create_default_context(cafile=cafile))
            cc.connect()
            errors[label] = "no error"
        except ssl.SSLCertVerificationError as e:
            errors[label] = str(e)
    for s in servers:
        s.shutdown()
    for ls in (ls1, ls2):
        ls.close()
    ok = (b"TOPSECRET123" in seen_http and b"POST / HTTP" in seen_http and b"TOPSECRET123" not in seen_tls and b"POST" not in seen_tls and version.startswith("TLSv1.")
          and "self-signed certificate" in errors["untrusted"] and "mismatch" in errors["mismatch"].lower())
    good = all(s in t for s in ("`POST / HTTP` and `TOPSECRET123`", "**neither** the password **nor** the word `POST`", "TLS 1.3", "SSLCertVerificationError: certificate verify failed: self-signed certificate", "hostname mismatch"))
    return ok and good, (f"a recording proxy between client and server: over HTTP it saw the password ({b'TOPSECRET123' in seen_http}) and the request line ({b'POST / HTTP' in seen_http}); over HTTPS ({version}, {cipher}) it saw the password "
                         f"({b'TOPSECRET123' in seen_tls}) and the word POST ({b'POST' in seen_tls}); an unknown (self-signed) certificate -> '{errors['untrusted'][:60]}...'; a certificate for another name -> '{errors['mismatch'][:70]}...'; notes say so: {good}")


# =========================================================================== #
# 7-logging.md
# =========================================================================== #
def logging_snippets():
    t = note("7-logging.md")
    out = {}
    # basic setup
    code = block_with(t, "basicConfig(level=logging.DEBUG, filename='app.log'", "logging.critical('This is a critical message')")
    d, p = run_py(code)
    lines = read(d).splitlines()
    out["basic"] = ([re.sub(TS, "<ts>", l) for l in lines], p.stdout + p.stderr)
    # divide example (level=20)
    d, p = run_py(block_with(t, "def divide(a, b):", "logging.basicConfig(level=20"))
    out["divide"] = [strip_ts(l) for l in read(d).splitlines()]
    # exception
    ex = block_with(t, "logging.exception('Division failed')")
    d, p = run_py("import logging\nlogging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')\n" + ex)
    out["exception"] = p.stderr.splitlines()
    # default behaviour, basicConfig twice
    d, p = run_py("import logging\nlogging.debug('d'); logging.info('i'); logging.warning('w'); logging.error('e')\nprint(logging.getLogger().level)")
    out["default"] = (p.stdout.strip(), p.stderr.splitlines())
    d, p = run_py("import logging, os\nlogging.basicConfig(level=logging.INFO, filename='first.log')\nlogging.basicConfig(level=logging.DEBUG, filename='second.log')\nlogging.debug('x')\nprint(sorted(f for f in os.listdir('.') if f.endswith('.log')), logging.getLogger().level)\n"
                  "logging.basicConfig(level=logging.DEBUG, filename='third.log', force=True)\nprint(sorted(f for f in os.listdir('.') if f.endswith('.log')))")
    out["twice"] = p.stdout.splitlines()
    # lazy formatting
    d, p = run_py("""
        import logging
        logging.basicConfig(level=logging.INFO)
        calls = []
        class Costly:
            def __str__(self):
                calls.append(1); return 'costly'
        logging.debug('value %s', Costly())
        a = len(calls)
        logging.debug(f'value {Costly()}')
        print(a, len(calls))
    """)
    out["lazy"] = p.stdout.strip()
    # flask example
    fl = block_with(t, "app.logger.debug(f'Dividing {a} by {b}')", "logging.basicConfig(level=logging.DEBUG, filename='app.log'")
    d, p = run_py(fl + "\nc = app.test_client()\nc.get('/divide?a=10&b=4'); c.get('/divide?a=1&b=0')\nprint(app.logger.handlers)\n")
    out["flask"] = ([strip_ts(l) for l in read(d).splitlines()], p.stdout.strip(), p.stderr.strip())
    for label, extra, code2 in (("flask_plain", "", "from flask import Flask\napp = Flask(__name__)\n@app.route('/x')\ndef x():\n    app.logger.debug('dbg'); app.logger.info('info'); app.logger.warning('warn')\n    return 'ok'\napp.test_client().get('/x')\n"),
                                ("flask_debug", "", "from flask import Flask\napp = Flask(__name__); app.debug = True\n@app.route('/x')\ndef x():\n    app.logger.debug('dbg'); app.logger.info('info'); app.logger.warning('warn')\n    return 'ok'\napp.test_client().get('/x')\n")):
        d, p = run_py(code2)
        out[label] = [re.sub(r"\[.*?\]", "[ts]", l) for l in p.stderr.splitlines()]
    # logger / handler / formatter
    d, p = run_py(block_with(t, "logging.getLogger('my_logger')", "console_handler.setLevel(logging.INFO)"))
    out["handlers"] = ([strip_ts(l) for l in p.stderr.splitlines()], [strip_ts(l) for l in read(d).splitlines()])
    # propagation
    d, p = run_py(block_with(t, "getLogger('app.sub')"))
    out["propagate"] = p.stderr.splitlines()
    # rotating
    d, p = run_py(block_with(t, "RotatingFileHandler('app.log', maxBytes=2000, backupCount=5)", "for i in range(120)") + "\nimport os\nprint(sorted((f, os.path.getsize(f)) for f in os.listdir('.') if f.startswith('app.log')))\n")
    out["rotating"] = eval(p.stdout.strip().splitlines()[-1])
    first_new = read(d).splitlines()[-1]
    ok = (out["basic"][0] == [f"<ts> - {lv} - This is a{'n' if lv in ('INFO', 'ERROR') else ''} {lv.lower()} message" for lv in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")] and out["basic"][1] == ""
          and out["divide"] == ["<ts> - INFO - Result of division: 5.0", "<ts> - ERROR - Attempt to divide by zero", "<ts> - INFO - Result of division: None"]
          and out["exception"][0] == "ERROR - Division failed" and out["exception"][1].startswith("Traceback") and out["exception"][-1] == "ZeroDivisionError: division by zero"
          and out["default"] == ("30", ["WARNING:root:w", "ERROR:root:e"]) and out["twice"][0] == "['first.log'] 20" and out["twice"][1] == "['first.log', 'third.log']" and out["lazy"] == "0 1"
          and out["flask"][0] == ["<ts> - DEBUG - Dividing 10 by 4", "<ts> - INFO - Result of division: 2.5", "<ts> - DEBUG - Dividing 1 by 0", "<ts> - ERROR - Attempt to divide by zero"] and out["flask"][1] == "[]" and out["flask"][2] == ""
          and out["flask_plain"] == ["[ts] WARNING in t: warn"] and out["flask_debug"] == ["[ts] DEBUG in t: dbg", "[ts] INFO in t: info", "[ts] WARNING in t: warn"]
          and out["handlers"][0] == [f"<ts> - my_logger - {lv} - This is a{'n' if lv in ('INFO', 'ERROR') else ''} {lv.lower()} message" for lv in ("INFO", "WARNING", "ERROR", "CRITICAL")] and len(out["handlers"][1]) == 5
          and out["handlers"][1][0].endswith("my_logger - DEBUG - This is a debug message") and out["propagate"] == ["CHILD hello", "ROOT hello", "CHILD no propagation"]
          and [f for f, _ in out["rotating"]] == ["app.log", "app.log.1", "app.log.2", "app.log.3", "app.log.4", "app.log.5"] and all(s <= 2000 for _, s in out["rotating"]) and first_new.endswith("message number 119 with some padding text to fill the file"))
    good = all(s in t for s in ("`WARNING:root:w`", "leaves the level at INFO and creates only `first.log`", "`force=True`", "**0 times**", "app.log.1", "(`CHILD hello`" if False else "CHILD hello", "WARNING in app: warn"))
    return ok and good, (f"every code block of the note was run: basic setup -> {len(out['basic'][0])} lines in app.log and nothing on the console; divide example -> {out['divide'][1:]}; logging.exception adds the traceback; default level {out['default'][0]} "
                         f"(only 'w' and 'e' shown); basicConfig twice -> {out['twice']}; lazy formatting __str__ calls (lazy, f-string) = {out['lazy']}; Flask + basicConfig -> {len(out['flask'][0])} lines in the file, console empty; Flask without basicConfig {out['flask_plain']}, "
                         f"debug mode {len(out['flask_debug'])} lines; handlers -> console {len(out['handlers'][0])} lines / file {len(out['handlers'][1])} lines; propagation {out['propagate']}; rotating files {out['rotating']}; notes show them: {good}")


def email_logging():
    import logging
    import logging.handlers
    t = note("7-logging.md")
    try:
        import flask_mail
        from aiosmtpd.controller import Controller
    except ImportError:
        SKIPPED.append("e-mail logging example skipped (flask_mail / aiosmtpd missing)")
        return True, "skipped (flask-mail / aiosmtpd not installed)"
    box = []

    class Handler:
        async def handle_DATA(self, server, session, envelope):
            box.append(envelope.content.decode("utf8", "replace"))
            return "250 OK"
    port = free_port()
    ctl = Controller(Handler(), hostname="127.0.0.1", port=port)
    ctl.start()
    try:
        block = block_with(t, "SMTPHandler(", "mail_handler.setLevel(logging.CRITICAL)")
        setup = block.split("@app.route")[0]
        setup = setup.replace("('smtp.gmail.com', 587)", f"('127.0.0.1', {port})")
        setup = re.sub(r"\n\s*credentials=.*", "", setup)
        setup = re.sub(r"\n\s*secure=.*", "", setup)
        setup = setup.replace("logging.getLogger().addHandler(mail_handler)", "logging.getLogger().setLevel(logging.DEBUG)\nlogging.getLogger().addHandler(mail_handler)")
        code = setup + "\nlogging.debug('d'); logging.error('e'); logging.critical('Attempt to divide by zero')\n"
        d, p = run_py(code)
        time.sleep(0.5)
        with_level = list(box)
        box.clear()
        code_no_level = code.replace("mail_handler.setLevel(logging.CRITICAL)", "pass").replace("; logging.critical('Attempt to divide by zero')", "")
        run_py(code_no_level)
        time.sleep(0.5)
        without = len(box)
    finally:
        ctl.stop()
    import logging.handlers as lh
    ok = (not hasattr(flask_mail, "SMTPHandler") and hasattr(lh, "SMTPHandler") and len(with_level) == 1 and "Subject: Critical Error in Application" in with_level[0] and "Attempt to divide by zero" in with_level[0]
          and without == 2 and "flask_mail.SMTPHandler" not in t)
    good = all(s in t for s in ("`logging.handlers.SMTPHandler`", "it does not contain an `SMTPHandler`", "`mail_handler.setLevel(logging.CRITICAL)` is essential", "mails **every** record", "app password"))
    return ok and good, (f"flask_mail has SMTPHandler: {hasattr(flask_mail, 'SMTPHandler')}; the standard library has it: {hasattr(lh, 'SMTPHandler')}; the note's handler against a local mail server: with setLevel(CRITICAL) {len(with_level)} mail (subject "
                         f"'Critical Error in Application'), without the level {without} mails for 2 log calls (debug + error); the wrong `flask_mail.SMTPHandler` is gone from the note: {'flask_mail.SMTPHandler' not in t}; notes say so: {good}")


# =========================================================================== #
# debugging.md
# =========================================================================== #
def debugging_traceback_and_print():
    t = note("debugging.md")
    code = block_with(t, "def average(numbers):", "report([[4, 8], []])")
    d, p = run_py(code)
    shown = block_with(t, "Traceback (most recent call last):", lang="text")
    norm = lambda s: [l for l in s.splitlines() if not re.fullmatch(r"\s*[~^]+\s*", l)]
    real = norm(p.stdout + p.stderr)
    real = [l.replace(str(d / "t.py"), "t.py") for l in real]
    p2 = subprocess.run([sys.executable, "-c", "total = 24\nprint(f'{total=}')"], capture_output=True, text=True).stdout.strip()
    ok = real == norm(shown) and p2 == "total=24"
    return ok and "`ZeroDivisionError: division by zero`" in t, f"the traceback of the note equals the real one (the ~~^^ markers of newer Python versions ignored): {real == norm(shown)}; f\"{{total=}}\" prints {p2}"


def pdb_claims():
    t = note("debugging.md")
    code = block_with(t, "def average(numbers):", "breakpoint()", "print(average([4, 8, 12]))")
    d = Path(tempfile.mkdtemp(prefix="w7pdb"))
    (d / "calc.py").write_text(code)
    p = subprocess.run([sys.executable, "calc.py"], cwd=d, input="p total\np numbers\nn\np total / len(numbers)\nc\n", capture_output=True, text=True, env=dict(os.environ, PYTHONBREAKPOINT=""))
    p0 = subprocess.run([sys.executable, "calc.py"], cwd=d, capture_output=True, text=True, env=dict(os.environ, PYTHONBREAKPOINT="0"))
    p1 = subprocess.run([sys.executable, "calc.py"], cwd=d, input="l\nw\nb 6\nq\n", capture_output=True, text=True)
    (d / "crash.py").write_text("def f(xs):\n    return xs[5]\nf([1, 2])\n")
    p2 = subprocess.run([sys.executable, "-m", "pdb", "crash.py"], cwd=d, input="c\np xs\nq\n", capture_output=True, text=True)
    (d / "old.py").write_text("import pdb\ndef f():\n    x = 41\n    pdb.set_trace()\n    return x + 1\nprint(f())\n")
    p3 = subprocess.run([sys.executable, "old.py"], cwd=d, input="p x\nc\n", capture_output=True, text=True)
    out = p.stdout
    ok = ("(Pdb) 24" in out and "(Pdb) [4, 8, 12]" in out and "-> return total / len(numbers)" in out and "(Pdb) 8.0" in out and p0.stdout == "8.0\n" and "(Pdb)" not in p0.stdout
          and "breakpoint()" in p1.stdout and "calc.py(8)<module>()" in p1.stdout and "Breakpoint 1 at" in p1.stdout
          and "Uncaught exception. Entering post mortem debugging" in p2.stdout and "[1, 2]" in p2.stdout and "(Pdb) 41" in p3.stdout)
    good = all(s in t for s in ("(Pdb) p total\n24", "[4, 8, 12]", "`PYTHONBREAKPOINT=0`", "Uncaught exception. Entering post mortem debugging", "`b 12`", "| `w` (where) |"))
    return ok and good, (f"pdb session of the note: p total -> 24, p numbers -> [4, 8, 12], n moves to the return line, p total / len(numbers) -> 8.0; PYTHONBREAKPOINT=0 skips the stop and prints {p0.stdout.strip()}; l / w / b work; "
                         f"`python -m pdb` on a crashing script enters post-mortem mode with the variables available; pdb.set_trace() works the same; notes show them: {good}")


def flask_debug_and_shell():
    t = note("debugging.md")
    flask_bin = Path(sys.executable).parent / "flask"
    if not flask_bin.exists():
        SKIPPED.append("flask shell / debug-mode checks skipped (flask command not found next to the interpreter)")
        return True, "skipped (flask CLI not found)"
    d = Path(tempfile.mkdtemp(prefix="w7flask"))
    (d / "app.py").write_text(textwrap.dedent("""\
        from flask import Flask
        app = Flask(__name__)
        COUNTER = 42
        @app.route('/')
        def home():
            return 'hi'
        @app.route('/boom')
        def boom():
            x = 10
            return 1 / (x - 10)
        @app.route('/total/<int:n>')
        def total(n):
            s = sum(range(n))
            breakpoint()
            return f'total={s}'
        """))
    env = dict(os.environ, PATH=f"{flask_bin.parent}:{os.environ['PATH']}")
    sh_ = subprocess.run(["flask", "--app", "app", "shell"], cwd=d, env=env, capture_output=True, text=True,
                         input="app\nfrom app import COUNTER\nCOUNTER\napp.test_client().get('/').data\nfrom flask import current_app\ncurrent_app.name\n")
    auto = subprocess.run(["flask", "shell"], cwd=d, env=env, capture_output=True, text=True, input="app\n")

    def serve(args, extra=None, stdin=False):
        port = free_port()
        proc = subprocess.Popen(["flask", "--app", "app", "run", "--port", str(port)] + args, cwd=d, env=dict(env, **(extra or {})), stdin=subprocess.PIPE if stdin else None,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, start_new_session=True)
        for _ in range(80):
            try:
                socket.create_connection(("127.0.0.1", port), 0.2).close()
                break
            except OSError:
                time.sleep(0.1)
        return proc, port

    def get(port, path):
        try:
            r = urllib.request.urlopen(f"http://127.0.0.1:{port}{path}", timeout=10)
            return r.status, r.read().decode()
        except urllib.error.HTTPError as e:
            return e.code, e.read().decode()

    def stop(proc):
        with contextlib.suppress(ProcessLookupError):
            os.killpg(proc.pid, signal.SIGKILL)
        return proc.communicate()[0]
    res = {}
    for label, args, extra in (("plain", [], {}), ("flask_env", [], {"FLASK_ENV": "development"}), ("debug", ["--debug"], {}), ("flask_debug", [], {"FLASK_DEBUG": "1"})):
        proc, port = serve(args, extra)
        status, body = get(port, "/boom")
        out = stop(proc)
        res[label] = (status, "Debug mode: on" in out, "Debugger PIN" in out, re.findall(r"<title>(.*?)</title>", body, re.S)[:1], "console" in body.lower(), "(x - 10)" in body)
    proc, port = serve([], stdin=True)
    got = {}
    th = threading.Thread(target=lambda: got.update(body=get(port, "/total/5")[1]))
    th.start()
    time.sleep(1.0)
    waiting = th.is_alive()
    proc.stdin.write("p n\np s\nc\n")
    proc.stdin.flush()
    th.join(10)
    pdb_out = stop(proc)
    ok = (">>> <Flask 'app'>" in sh_.stdout and "42" in sh_.stdout and "b'hi'" in sh_.stdout and "'app'" in sh_.stdout and "App: app" in sh_.stderr and "App: app" in auto.stderr and "<Flask 'app'>" in auto.stdout
          and res["plain"][:3] == (500, False, False) and res["plain"][3] == ["500 Internal Server Error"] and res["flask_env"][:3] == (500, False, False) and res["flask_env"][3] == ["500 Internal Server Error"]
          and res["debug"][:3] == (500, True, True) and res["flask_debug"][:3] == (500, True, True) and res["debug"][3][0].startswith("ZeroDivisionError: division by zero") and res["debug"][3][0].rstrip().endswith("Werkzeug Debugger")
          and res["debug"][4] and res["debug"][5] and waiting and got.get("body") == "total=10" and "(Pdb) 5" in pdb_out and "(Pdb) 10" in pdb_out)
    good = all(s in t for s in ("`export FLASK_ENV=development` no longer works", "removed in Flask 2.3", "ZeroDivisionError: division by zero // Werkzeug Debugger", "**`app` is already defined**", "`p n` prints `5`, `p s` prints `10`", "total=10", "Debugger PIN"))
    return ok and good, (f"flask shell: `app` is predefined ({'<Flask' in sh_.stdout}), `flask shell` without --app finds app.py ({'App: app' in auto.stderr}), current_app works; a failing route: normal run -> {res['plain'][0]} '{res['plain'][3][0]}'; FLASK_ENV=development -> still debug off, "
                         f"'{res['flask_env'][3][0]}'; --debug and FLASK_DEBUG=1 -> debugger active with PIN, page '{res['debug'][3][0].strip()[:60]}', console and source line shown; breakpoint() in a route: the request waits while paused ({waiting}) "
                         f"and returns {got.get('body')!r} after `c`; notes say so: {good}")


# =========================================================================== #
# structure and hygiene
# =========================================================================== #
def index_lists_everything():
    t = note("week7-index.md")
    files = sorted(f.name for f in NOTES.glob("*.md") if f.name != "week7-index.md")
    linked = set(re.findall(r"\]\(([^)#]+\.md)\)", t))
    missing = [f for f in files if f not in linked]
    broken = [f for f in linked if not (NOTES / f).exists()]
    return not missing and not broken and "<SessionResources" not in t, f"the index links all {len(files)} topic files ({files}); not linked: {missing or 'none'}; broken: {broken or 'none'}; VitePress component removed: {'<SessionResources' not in t}"


def md_files():
    return sorted(NOTES.glob("*.md"))


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
            if re.match(r"^\s*:::|^== |</?[A-Z]\w+[^>]*/?>", line) or "SessionResources" in line or "<SQLinjection" in line:
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
        for m in re.finditer(r"\\=|\\text\{[^}]*\$", t):
            bad.append(f"{f.name}: LaTeX problem {m.group(0)!r}")
    return not bad, f"fences closed cleanly, no LaTeX typos: {bad or 'ok'}"


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
                cells = len(re.split(r"(?<!\\)\|", line.rstrip().rstrip("|")[1:]))
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
    if not (js and Path(js).exists() and node):
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
        env = dict(os.environ, NODE_PATH=subprocess.run(["npm", "root", "-g"], capture_output=True, text=True).stdout.strip())
        p = subprocess.run([node, str(Path(d, "r.js")), js, str(Path(d, "in.json"))], capture_output=True, text=True, env=env)
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
        bad += [f"{f.name}: {m}" for m in re.findall(r"[\w.+-]+@[\w-]+\.[\w.]+|Downloaded by|quizpractice", t) if not m.endswith(("example.com",))]
    return not bad, f"no e-mail address of a person / source watermark in the notes (example.com addresses of the e-mail logging example are placeholders): {bad or 'none'}"


# =========================================================================== #
if __name__ == "__main__":
    DS, MA, SQ, WS, LG, DB, IX = ("7-data-search-algo.md", "7-memory-architecture.md", "7-SQL-web.md", "7-web-security.md", "7-logging.md", "debugging.md", "week7-index.md")
    print("=" * 78 + "\nWeek 7 claim checker\n" + "=" * 78 + "\n")
    check(DS, "Big-O numbers: growth table, binary search steps (20 / 30 / 21), matmul N^3, subsets 2^N, Fibonacci calls and memoisation", big_o_numbers)
    check(DS, "binary-search traces of the note, shifting cost of array insertion, list resizing, list vs bisect vs set timings", search_and_arrays)
    check(DS, "BST example (search path, in-order), skewed vs random height, hash collisions", bst_and_hash)
    check(DS, "the growth-rate picture exists and is used", growth_chart)
    check(MA, "bandwidth formula, average access time, latency scaling, disk rotation, practice answers", memory_numbers)
    check(MA, "the figures and orderings of the lecture slides are kept", slide_figures)
    check(MA, "cache locality: column-wise access is slower than row-wise (measured)", locality_experiment)
    check(SQ, "every index claim: query plans, LIKE and NOCASE, compound-index rule, speed-up, write cost, no hash index in SQLite", sqlite_index_claims)
    check(SQ, "JOIN example, Redis commands, MongoDB queries, documents of different shapes, data duplication in documents", sql_join_and_nosql)
    check(SQ, "sharding examples and the replica-lag table", sharding_and_replication)
    check(SQ, "corrected wording: CAP availability / partition choice, C of CAP vs ACID, no 'no duplication' claim", cap_and_slide_wording)
    check(WS, "SQL injection: login bypass, comment, UNION, numeric, stacked statement; parameterised queries", sql_injection)
    check(WS, "SQLAlchemy bound parameters vs text() f-string, Flask login attacked with curl, password hashing", orm_and_flask_demo)
    check(WS, "Flask / Jinja2 escapes script tags (XSS)", xss_autoescape)
    check(WS, "HTTPS: an eavesdropper reads HTTP but not HTTPS; untrusted and mismatching certificates are refused", tls_claims)
    check(LG, "every logging code block of the note, its output files and the Flask logging table", logging_snippets)
    check(LG, "e-mail logging: SMTPHandler is in the standard library (not flask_mail) and needs setLevel", email_logging)
    check(DB, "the traceback of the note equals a real one; f\"{x=}\"", debugging_traceback_and_print)
    check(DB, "pdb: breakpoint(), commands, PYTHONBREAKPOINT=0, post-mortem, set_trace", pdb_claims)
    check(DB, "flask shell, FLASK_ENV no longer works, --debug / FLASK_DEBUG, Werkzeug debugger page, breakpoint() in a route", flask_debug_and_shell)
    check(IX, "the index links every topic file", index_lists_everything)
    check("week7/*.md", "no VitePress-only syntax (:::, == tabs, components)", no_vitepress_syntax)
    check("week7/*.md", "no HTML that GitHub strips (style, class, div, pre, table cards)", no_stripped_html)
    check("week7/*.md", "alerts, <details> and <summary> written correctly", alerts_and_details)
    check("week7/*.md", "fences are closed cleanly, no LaTeX typos", fences_and_latex)
    check("week7/*.md", "every table row has the same number of cells as its header", tables_consistent)
    check("week7/*.md", "every local link, #anchor and image resolves", links_resolve)
    check("week7/*.md", "no personal data in the notes", no_personal_data)
    m = mermaid_renders()
    if m is not None:
        check("week7/*.md", "mermaid diagrams render without literal markup", lambda: m)

    wrong = [f for ok, f in RESULTS if not ok]
    print("=" * 78)
    print(f"{len(RESULTS)} checks, {len(RESULTS) - len(wrong)} OK, {len(wrong)} WRONG")
    if wrong:
        print("files with WRONG statements:", ", ".join(sorted(set(wrong))))
    print("\nNOT VERIFIABLE HERE (kept because they are standard, but not executed):")
    for s in SKIPPED + [
        "typical-today hardware values and latencies of the memory hierarchy (vendor figures / rules of thumb) and the cold-storage retrieval times of AWS / Google / Azure (provider documentation)",
        "MySQL behaviour quoted from the lecture slides (LIKE 'Pat%' and compound-index OR rules, in-memory hash indexes, skip scan) and PostgreSQL hash indexes / GEQO",
        "Cypher (Neo4j), CQL (Cassandra), InfluxQL queries, MySQL GRANT and the Gmail app-password procedure (the services are not available here)",
        "CAP theorem and consistency-model statements (theory), BASE / ACID classification of products, the claim that shared caches cannot store HTTPS responses",
        "XSS / CSRF / buffer-overflow descriptions beyond the Jinja2 escaping that was run (Week 9 covers CSRF)",
        "external images (miro.medium.com, cs186berkeley.net, serverwatch.com) and the YouTube / pdsaiitm / MySQL / SQLite / PostgreSQL / ml4devs links (blocked from this sandbox)",
    ]:
        print("  -", s)
    sys.exit(1 if wrong else 0)
