"""
Week 1 notes -- claim checker.

Every check takes one statement (or formula / diagram) from the week1 notes,
runs it for real -- exact arithmetic, a local HTTP server, real sockets, the
`ipaddress` module, the RFC 1071 checksum, the mermaid renderer -- and reports
whether the notes are right:

    OK     -> the notes say what actually happens
    WRONG  -> the notes say something that does not happen (the evidence shows what does)

A check usually has two halves:
    1. the FACT        -> measured here
    2. the NOTE TEXT   -> the markdown contains the correct statement and not the wrong one

The claims are written as the notes state them *after* the accuracy fixes, so a
clean run ends with "0 WRONG". If something changes, the affected check turns
WRONG and points to the note that needs updating.

Run (from anywhere):
    python week1/verify_week1_claims.py
    python week1/verify_week1_claims.py -v

Optional: to also render the mermaid diagrams as GitHub does, install
    npm install mermaid@11        (and have `playwright` for node available)
and run with  MERMAID_JS=/path/to/node_modules/mermaid/dist/mermaid.min.js
Without it that one check is skipped and listed at the end.

Checked against CPython 3.13 on Linux. Statements that need the internet,
Windows, or a standards document are listed under "NOT VERIFIABLE HERE".
"""
import http.client
import http.server
import ipaddress
import json
import os
import re
import shutil
import socket
import struct
import subprocess
import sys
import tempfile
import threading
from fractions import Fraction
from http import HTTPStatus
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
VERBOSE = "-v" in sys.argv
RESULTS = []
SKIPPED = []


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def note(name):
    return (HERE / name).read_text(encoding="utf-8")


def check(file, claim, fn):
    """fn() returns (notes_are_correct: bool, evidence: str)."""
    try:
        ok, evidence = fn()
    except Exception as e:
        ok, evidence = False, f"raised {type(e).__name__}: {str(e).splitlines()[0][:150]}"
    RESULTS.append((ok, file))
    print(f"[{'OK   ' if ok else 'WRONG'}] {file}\n        claim   : {claim}\n        actual  : {evidence}\n")


def has(text, pattern, flags=re.I | re.S):
    return re.search(pattern, text, flags) is not None


def md_files():
    return sorted(HERE.glob("*.md"))


def github_slug(heading):
    """GitHub's anchor for a heading: lower-case, drop punctuation/emoji, spaces -> '-'."""
    s = re.sub(r"[`*_]", "", heading.strip().lower())
    s = re.sub(r"[^\w\- ]", "", s, flags=re.UNICODE)
    return s.replace(" ", "-")


# --------------------------------------------------------------------------- #
# 1-2-latency-bandwidth.md
# --------------------------------------------------------------------------- #
def latency_numbers():
    F = Fraction
    c_fibre = F(2 * 10**8)
    ns_per_m = 1 / c_fibre * 10**9
    ms_per_1000km = F(10**6) / c_fibre * 10**3
    one_way = F(2000 * 10**3) / c_fibre            # seconds
    rtt = 2 * one_way
    rps = 1 / rtt
    reqs = 1000 * 2
    kb_s = reqs * F("18.2")
    mb_s = kb_s / 1000
    mbps = mb_s * 8
    gb = 50_000 * 4 / 1000
    ok = (ns_per_m == 5 and ms_per_1000km == 5 and one_way == F(1, 100) and rtt == F(1, 50)
          and rps == 50 and kb_s == 36_400 and mb_s == F("36.4") and mbps == F("291.2") and gb == 200
          and F("18") + F("0.2") == F("18.2"))
    return ok, (f"{ns_per_m} ns/m, {ms_per_1000km} ms/1000 km, one-way {float(one_way)*1e3:g} ms, RTT {float(rtt)*1e3:g} ms, "
                f"{rps} req/s; 2000 req/s x 18.2 KB = {kb_s} KB/s = {float(mb_s):g} MB/s = {float(mbps):g} Mbps; 50,000 x 4 MB = {float(gb):g} GB")


def latency_wording():
    t = note("1-2-latency-bandwidth.md")
    good = (has(t, r"one-way") and has(t, r"round[- ]trip") and has(t, r"propagation")
            and has(t, r"processing|queuing|queueing"))
    bad_def = has(t, r"^Latency is the time delay between sending a request and receiving the response\.", re.M)
    return good and not bad_def, ("latency defined as one-way delay, RTT = request+response, and the problems use propagation delay only "
                                  f"(real latency also has processing/queuing): note says so: {good}; old mixed definition still present: {bad_def}")


def bandwidth_wording():
    t = note("1-2-latency-bandwidth.md")
    good = has(t, r"291\.2") and has(t, r"round(ed)? up") and not has(t, r"at least \*\*300 Mbps")
    return good, f"minimum is 291.2 Mbps (300 Mbps is only a rounded-up figure), not 'at least 300': {good}"


def latex_safe():
    t = note("1-2-latency-bandwidth.md")
    bad_eq = has(t, r"\\=")                       # \= is MathJax's macron accent, not an equals sign
    dollar_in_text = has(t, r"\\text\{[^}]*\$")   # $...$ nested inside \text{} inside $$...$$
    return not bad_eq and not dollar_in_text, f"'\\=' typo present: {bad_eq}; '$' nested in \\text{{}}: {dollar_in_text}"


def latency_exercise_answered():
    t = note("1-2-latency-bandwidth.md")
    ok = has(t, r"Increasing bandwidth does not always reduce page loading time.{0,600}(round[- ]trip|handshake|latency)")
    typos = [p for p in (r"a a \*\*4 MB", r"doesnt", r"needs to be store") if has(t, p)]
    typos += [p for p in (r"MBps",) if re.search(p, t)]          # case-sensitive: Mbps (bits) is correct, MBps is ambiguous
    return ok and not typos, f"'why more bandwidth does not always speed up a page' has an answer: {ok}; leftover typos: {typos or 'none'}"


# --------------------------------------------------------------------------- #
# 1-3-network-history-TCP.md
# --------------------------------------------------------------------------- #
class _H(http.server.BaseHTTPRequestHandler):
    seen = {}

    def do_GET(self):
        type(self).seen = dict(self.headers)
        body = b"<h1>hi</h1>"
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "max-age=60")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):
        pass


def http_headers():
    srv = http.server.HTTPServer(("127.0.0.1", 0), _H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        conn = http.client.HTTPConnection("127.0.0.1", srv.server_port)
        conn.request("GET", "/", headers={"Accept": "text/html", "Accept-Language": "en", "Accept-Encoding": "gzip"})
        r = conn.getresponse()
        resp_headers = {k.lower() for k, _ in r.getheaders()}
        status = (r.status, r.reason)
    finally:
        srv.shutdown()
    req_headers = {k.lower() for k in _H.seen}
    fact = ({"accept", "accept-language", "accept-encoding"} <= req_headers
            and not ({"accept", "accept-language", "accept-encoding"} & resp_headers)
            and {"content-type", "cache-control"} <= resp_headers and "status" not in resp_headers and status == (200, "OK"))
    t = note("1-3-network-history-TCP.md")
    good = (has(t, r"status line") and has(t, r"Content-Type") and has(t, r"Accept-Language")
            and not has(t, r"\*\*Response Header\*\* contains:\s*\n\s*- acceptable content types"))
    return fact and good, (f"client sent {sorted(h for h in req_headers if h.startswith('accept'))}; response headers were {sorted(resp_headers)}; "
                           f"status {status} is in the status line, not a header; note separates request headers / status line / response headers: {good}")


def inet_checksum(data: bytes) -> int:
    if len(data) % 2:
        data += b"\0"
    s = sum(struct.unpack(f"!{len(data)//2}H", data))
    while s >> 16:
        s = (s & 0xFFFF) + (s >> 16)
    return ~s & 0xFFFF


def tcp_checksum():
    data = b"GET /index.html HTTP/1.1\r\nHost: example.com\r\n\r\n"
    c = inet_checksum(data)
    receiver_ok = inet_checksum(data + struct.pack("!H", c)) == 0 if len(data) % 2 == 0 else inet_checksum(data + b"\0" + struct.pack("!H", c)) == 0
    flipped = bytearray(data)
    flipped[5] ^= 0x01
    detects_bitflip = inet_checksum(bytes(flipped) + (b"\0" if len(data) % 2 else b"") + struct.pack("!H", c)) != 0
    w = bytearray(data if len(data) % 2 == 0 else data + b"\0")
    w[0:4] = w[2:4] + w[0:2]                      # swap two 16-bit words
    swap_same = inet_checksum(bytes(w)) == inet_checksum(data)
    forged = bytearray(data)
    forged[5] ^= 0x01
    t = note("1-3-network-history-TCP.md")
    good = has(t, r"accidental") and has(t, r"not (a )?security|not .{0,20}tamper|does not (protect|stop)")  \
        and not has(t, r"Request Resend") and has(t, r"retransmit")
    fact = receiver_ok and detects_bitflip and swap_same
    return fact and good, (f"16-bit one's-complement checksum {c:#06x}: receiver recomputes -> 0 ({receiver_ok}); single bit flip detected ({detects_bitflip}); "
                           f"swapping two 16-bit words gives the SAME checksum ({swap_same}) so it catches accidents, not tampering; "
                           f"note says 'accidental', not a security feature, sender retransmits (no 'Request Resend' from receiver): {good}")


def ports():
    ok16 = struct.pack("!H", 65535) and True
    try:
        struct.pack("!H", 65536)
        over = False
    except struct.error:
        over = True
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    assigned = s.getsockname()[1]
    s.close()
    t = note("1-3-network-history-TCP.md")
    good = has(t, r"65,?\s?536|65\{,\}536") and has(t, r"0 to 65,?535|0.{1,3}65[,{}]*535")
    return ok16 and over and assigned > 0 and 2**16 == 65536 and good, (
        f"16 bits hold 2^16 = 65,536 values = 0..65,535 (65536 does not fit: {over}); bind(port 0) -> OS picked {assigned}; note states 65,536 values / 0..65,535: {good}")


def loopback_and_wildcard():
    def server(host):
        s = socket.socket()
        s.bind((host, 0))
        s.listen()
        return s, s.getsockname()[1]

    def can_connect(host, port):
        try:
            socket.create_connection((host, port), timeout=1).close()
            return True
        except OSError:
            return False

    s_all, p_all = server("0.0.0.0")
    s_lo, p_lo = server("127.0.0.1")
    try:
        all_reach = can_connect("127.0.0.1", p_all) and can_connect("127.0.0.2", p_all)
        lo_only = can_connect("127.0.0.1", p_lo) and not can_connect("127.0.0.2", p_lo)
    finally:
        s_all.close()
        s_lo.close()
    block_loop = ipaddress.ip_address("127.0.0.2").is_loopback and ipaddress.ip_address("127.255.255.254").is_loopback
    t = note("1-3-network-history-TCP.md")
    good = not has(t, r"virtual machine") and has(t, r"127\.0\.0\.0/8|127\.x\.x\.x|whole `?127")
    return all_reach and lo_only and block_loop and good, (
        f"bound to 0.0.0.0 -> reachable via 127.0.0.1 and 127.0.0.2: {all_reach}; bound to 127.0.0.1 -> only 127.0.0.1: {lo_only}; "
        f"the whole 127.0.0.0/8 block is loopback: {block_loop}; note no longer calls loopback a 'virtual machine' and mentions 127.0.0.0/8: {good}")


def ip_addresses():
    a = ipaddress.IPv4Address("172.16.10.25")
    hexes = [f"{o:02X}" for o in a.packed]
    groups = [hexes[0] + hexes[1], hexes[2] + hexes[3]]
    mapped = ":".join(f"{g:04x}" for g in struct.unpack("!8H", b"\x00" * 10 + b"\xff\xff" + a.packed))   # IPv4-mapped IPv6 address
    v6 = ipaddress.IPv6Address("::1").exploded.split(":")
    fact = (hexes == ["AC", "10", "0A", "19"] and groups == ["AC10", "0A19"]
            and (10 * 16 + 12, 1 * 16 + 0, 0 * 16 + 10, 1 * 16 + 9) == (172, 16, 10, 25)
            and ipaddress.IPv4Address(0).max_prefixlen == 32 and ipaddress.IPv6Address(0).max_prefixlen == 128
            and len(v6) == 8 and all(len(g) == 4 for g in v6) and mapped == "0000:0000:0000:0000:0000:ffff:ac10:0a19")
    t = note("1-3-network-history-TCP.md")
    good = has(t, r"0000:0000:AC10:0A19") and has(t, r"eight|8 groups") and has(t, r"::ffff:") and has(t, r"B\)")
    return fact and good, (f"172.16.10.25 -> AC 10 0A 19 -> AC10:0A19 (answer B holds for the question's 4-group format); real IPv6 always has 8 groups, "
                           f"the IPv4-mapped form is {mapped}; IPv4 = 32 bits, IPv6 = 128 bits; note mentions the real 8-group / ::ffff: form: {good}")


def status_table():
    t = note("1-3-network-history-TCP.md")
    sec = t.split("## Status codes", 1)[1].split("\n## ", 1)[0]
    rows, cat, bad, started = 0, None, [], False
    for line in sec.splitlines():
        if started and not line.startswith("|"):
            break                                  # only the first table is the status-code table
        if not line.startswith("|") or set(line.replace("|", "").strip()) <= set("- :"):
            continue
        started = True
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if cells[0].lower() == "category":
            if len(cells) != 4:
                bad.append("header must have 4 columns")
            continue
        if len(cells) != 4:
            bad.append(f"row has {len(cells)} columns: {cells}")
            continue
        if cells[0]:
            cat = int(re.search(r"\d", cells[0]).group())
        code = re.fullmatch(r"\d{3}", cells[1])
        if not code:
            bad.append(f"code cell is not a bare 3-digit code: {cells[1]!r}")
            continue
        code = int(cells[1])
        rows += 1
        if code // 100 != cat:
            bad.append(f"{code} listed under {cat}xx")
        if cells[2] != HTTPStatus(code).phrase:
            bad.append(f"{code}: note '{cells[2]}' vs standard '{HTTPStatus(code).phrase}'")
    cont = has(t, r"100.{0,120}(may|can) (continue|send)") or has(t, r"Expect: 100-continue")
    return rows >= 14 and not bad and cont, f"{rows} status rows: names match http.HTTPStatus and sit under the right 1xx..5xx category: {bad or 'yes'}; 100 Continue explained correctly: {cont}"


def tcp_ip_steps():
    t = note("1-3-network-history-TCP.md")
    good = has(t, r"three-way handshake|3-way handshake|SYN") and has(t, r"TLS handshake")
    order = t.find("DNS") < t.find("handshake") < t.find("HTTPS request") if good else False
    return good and order, f"'opening a website' lists the TCP handshake and the TLS handshake before the HTTPS request: {good and order}"


def unrenderable_terms():
    t = note("1-3-network-history-TCP.md")
    bad = [p for p in (r"Ethernet each had", r"network of servers", r"HTTPSecure", r"digital \"fingerprint\"", r"\(AC,,10\)") if has(t, p)]
    return not bad, f"wrong/garbled phrases still present: {bad or 'none'}"


# --------------------------------------------------------------------------- #
# 1-1 / 1-4 wording
# --------------------------------------------------------------------------- #
def intro_wording():
    t = note("1-1-intro-to-applications.md")
    bad = [p for p in (r"Originally referred to any mobile or desktop", r"Android\*? SDK, \*Swift\*") if has(t, p)]
    good = has(t, r"iOS SDK") and has(t, r"## Platforms")
    return not bad and good, f"'app' history sentence fixed, Swift is a language (iOS SDK + Swift), heading renamed: {good}; leftovers {bad or 'none'}"


def architecture_wording():
    t = note("1-4-types-architecture.md")
    bad = [p for p in (r"browser accessing a local database", r"Distributed file systems\*") if has(t, p)]
    good = has(t, r"distributed.{0,80}(peer-to-peer|P2P).{0,80}(kind|type|one)") or has(t, r"P2P is one (kind|type)")
    return not bad and good, f"browsers do not talk to a database directly; 'distributed' is broader than P2P: {good}; leftovers {bad or 'none'}"


# --------------------------------------------------------------------------- #
# markdown / GitHub hygiene (what we did for week5 and week0)
# --------------------------------------------------------------------------- #
def no_vitepress_syntax():
    found = []
    for f in md_files():
        for i, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if re.match(r"^\s*:::|^== |^```\w+ \[|</?[A-Z]\w+[^>]*/?>", line) or "StatusCodeSimulator" in line:
                found.append(f"{f.name}:{i}")
    return not found, f"VitePress-only syntax (::: / == / ```lang [Label] / <Component/>): {found or 'none'}"


def no_stripped_html():
    found = []
    for f in md_files():
        for i, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if re.search(r"style\s*=|&emsp;|<font|<center", line):
                found.append(f"{f.name}:{i}")
    return not found, f"HTML GitHub removes or ignores (style=, &emsp;, <font>, <center>): {found or 'none'}"


def alerts_valid():
    bad = []
    for f in md_files():
        lines = f.read_text(encoding="utf-8").splitlines()
        for i, line in enumerate(lines, 1):
            m = re.match(r"^> \[!(\w+)\]\s*$", line)
            if m and m.group(1) not in {"NOTE", "TIP", "IMPORTANT", "WARNING", "CAUTION"}:
                bad.append(f"{f.name}:{i} {line}")
            if re.match(r"^>\s*\[!\w+\]\S", line):
                bad.append(f"{f.name}:{i} text after [!TYPE] on same line")
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
                bad.append(f"{f.name}: backticks inside <summary> do not render ({m.group(1)[:40]!r})")
    return not bad, f"unbalanced <details> or backticks in <summary>: {bad or 'none'}"


def links_resolve():
    bad = []
    for f in md_files():
        text = re.sub(r"```.*?```", "", f.read_text(encoding="utf-8"), flags=re.S)
        for m in re.finditer(r"!?\[[^\]]*\]\(([^)\s]+)\)", text):
            url = m.group(1)
            if re.match(r"(https?:|mailto:|#)", url):
                continue
            path, _, anchor = url.partition("#")
            target = (f.parent / path).resolve()
            if not target.exists():
                bad.append(f"{f.name}: {url} (file not found)")
            elif anchor and target.suffix == ".md":
                slugs = {github_slug(h) for h in re.findall(r"^#{1,6}\s+(.*)$", target.read_text(encoding="utf-8"), re.M)}
                if anchor not in slugs:
                    bad.append(f"{f.name}: {url} (no such heading; have e.g. {sorted(slugs)[:3]})")
        for m in re.finditer(r'<img[^>]*src="([^"]+)"', text):
            if not m.group(1).startswith("http") and not (f.parent / m.group(1)).resolve().exists():
                bad.append(f"{f.name}: image {m.group(1)}")
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
                if "[" in m.group(2):
                    bad.append(f"{f.name}:{i} {line!r}")
            else:
                open_ = False
                if m.group(1) or m.group(2).strip():
                    bad.append(f"{f.name}:{i} closing fence {line!r}")
        if open_:
            bad.append(f"{f.name}: unclosed fence")
    return not bad, f"labelled / badly closed / unclosed fences: {bad or 'none'}"


def mermaid_renders():
    js = os.environ.get("MERMAID_JS")
    node = shutil.which("node")
    if not (js and Path(js).exists() and node):
        SKIPPED.append("mermaid render check skipped (set MERMAID_JS=.../mermaid.min.js, needs node + playwright)")
        RESULTS.append((True, "week1/*.md"))
        print("[SKIP ] week1/*.md  mermaid render (not installed)\n")
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
            lit = [t for t in r["text"] if re.search(r"\*\*|&lt;|&gt;|<br|</?b>", t)]
            if lit:
                bad.append(f"{w}: literal markup in labels {lit[:2]}")
    return not bad, f"{len(diagrams)} mermaid diagrams rendered with real mermaid; syntax errors / literal ** or <br> in labels: {bad or 'none'}"


# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    A, L, T, W = "1-1-intro-to-applications.md", "1-2-latency-bandwidth.md", "1-3-network-history-TCP.md", "1-4-types-architecture.md"
    print("=" * 78 + "\nWeek 1 claim checker\n" + "=" * 78 + "\n")
    check(A, "'app' history, SDK examples (Swift is a language, iOS has the SDK) and heading are accurate", intro_wording)
    check(L, "all numerical results (5 ns/m, 10 ms one-way, 20 ms RTT, 50 req/s, 36.4 MB/s, 291.2 Mbps, 200 GB) are exactly right", latency_numbers)
    check(L, "latency = one-way delay, RTT = there and back, propagation delay only (no processing/queuing)", latency_wording)
    check(L, "minimum bandwidth is 291.2 Mbps (300 Mbps is a rounded-up figure)", bandwidth_wording)
    check(L, "LaTeX is safe for GitHub (no '\\=', no '$' nested in \\text{})", latex_safe)
    check(L, "the open exercise is answered; no typos", latency_exercise_answered)
    check(T, "Accept* are REQUEST headers; the status code is in the status line; Content-Type/Cache-Control are RESPONSE headers", http_headers)
    check(T, "TCP checksum detects accidental corruption (not tampering); the sender retransmits", tcp_checksum)
    check(T, "16-bit ports = 65,536 values (0..65,535); bind(0) lets the OS choose", ports)
    check(T, "127.0.0.0/8 is loopback (not a VM); 0.0.0.0 listens on all interfaces", loopback_and_wildcard)
    check(T, "IPv4/IPv6 sizes and the hex-conversion MCQ (real IPv6 has 8 groups)", ip_addresses)
    check(T, "status-code table: names/categories match the standard; 100 Continue explained", status_table)
    check(T, "opening a website mentions the TCP and TLS handshakes before the HTTPS request", tcp_ip_steps)
    check(T, "no wrong/garbled phrases (Ethernet protocol suite, 'network of servers', HTTPSecure, checksum 'fingerprint', ',,')", unrenderable_terms)
    check(W, "browser-vs-database wording, 'distributed' vs P2P", architecture_wording)
    check("week1/*.md", "no VitePress-only syntax (:::, ==, <Component/>)", no_vitepress_syntax)
    check("week1/*.md", "no HTML that GitHub strips (style=, &emsp;, <font>)", no_stripped_html)
    check("week1/*.md", "GitHub alerts are written correctly", alerts_valid)
    check("week1/*.md", "<details> balanced and no backticks inside <summary>", details_balanced)
    check("week1/*.md", "every local link, #anchor and image resolves", links_resolve)
    check("week1/*.md", "code fences are labelled/closed cleanly", fences_clean)
    m = mermaid_renders()
    if m is not None:
        check("week1/*.md", "mermaid diagrams render on GitHub's renderer without literal markup", lambda: m)

    wrong = [f for ok, f in RESULTS if not ok]
    print("=" * 78)
    print(f"{len(RESULTS)} checks, {len(RESULTS) - len(wrong)} OK, {len(wrong)} WRONG")
    if wrong:
        print("files with WRONG statements:", ", ".join(sorted(set(wrong))))
    print("\nNOT VERIFIABLE HERE (kept because they are standard, but not executed):")
    for s in SKIPPED + [
        "TCP receivers only ACK; loss is repaired by sender timeout / duplicate ACKs (RFC 9293) and TLS/TCP handshake order (needs packet capture / the RFCs)",
        "HTTP method semantics (PUT replaces, PATCH partially updates) and status-code meanings beyond their names (RFC 9110)",
        "DNS example www.google.com -> 142.250.x.x (needs internet DNS; the address changes over time)",
        "Web 1.0 / 2.0 / 3 eras and the external imgur image (dates are conventional; imgur is blocked from this sandbox)",
        "MDN / drive.google.com / em360tech links (blocked from this sandbox)",
    ]:
        print("  -", s)
    sys.exit(1 if wrong else 0)
