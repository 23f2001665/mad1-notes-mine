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
import signal
import tempfile
import textwrap
import threading
import time
from fractions import Fraction
from http import HTTPStatus
from pathlib import Path
from urllib.parse import urljoin

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
# 1-5-curl-http-server-netcat.md  (curl, python -m http.server, index.html, nc)
#
# The commands are taken from the note itself (fenced blocks), the example ports
# 8000 / 8080 / 9000 are swapped for free ones, and they are run for real.
# --------------------------------------------------------------------------- #
NET = "1-5-curl-http-server-netcat.md"
_SHIM = []


def fenced(text, lang=None):
    """Bodies of the fenced code blocks (indented fences inside list items are dedented)."""
    out = []
    for m in re.finditer(r"^[ \t]*```(\w*)[^\n]*\n(.*?)^[ \t]*```[ \t]*$", text, re.S | re.M):
        if lang is None or m.group(1) == lang:
            out.append(textwrap.dedent(m.group(2)))
    return out


def block_with(text, needle, lang="bash"):
    for b in fenced(text, lang):
        if needle in b:
            return b
    raise LookupError(f"no ```{lang} block containing {needle!r} in the note")


def shim_env():
    """PATH where `python` is this interpreter (the note writes `python -m http.server`)."""
    if not _SHIM:
        d = Path(tempfile.mkdtemp(prefix="w1shim"))
        (d / "python").symlink_to(sys.executable)
        _SHIM.append(d)
    return dict(os.environ, PATH=f"{_SHIM[0]}:{os.environ['PATH']}")


def free_ports(n=3):
    socks = [socket.socket() for _ in range(n)]
    for s in socks:
        s.bind(("127.0.0.1", 0))
    ports_ = [s.getsockname()[1] for s in socks]
    for s in socks:
        s.close()
    return ports_


def subst(text, mapping):
    """Replace the example ports (8000, 8080, 9000) used in the note by free ones."""
    return re.sub(r"\b(8000|8080|9000)\b", lambda m: str(mapping[m.group(1)]), text)


def listening(port):
    """Hex local addresses of the sockets that LISTEN on `port` (from /proc, so nothing connects)."""
    out = []
    for line in Path("/proc/net/tcp").read_text().splitlines()[1:]:
        f = line.split()
        addr, pt = f[1].split(":")
        if int(pt, 16) == port and f[3] == "0A":
            out.append(addr)
    return out


class Bg:
    """A background shell command in its own process group; stop() returns everything it printed."""

    def __init__(self, cmd, cwd=None):
        self.p = subprocess.Popen(["bash", "-c", cmd], cwd=cwd, env=shim_env(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                  start_new_session=True, text=True)

    def wait_listen(self, port, timeout=6):
        end = time.time() + timeout
        while time.time() < end:
            if listening(port):
                return self
            if self.p.poll() is not None:
                break
            time.sleep(0.05)
        raise RuntimeError(f"nothing listens on {port}: {self.stop().strip()[:200]!r}")

    def stop(self):
        try:
            os.killpg(self.p.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        try:
            return self.p.communicate(timeout=3)[0]
        except subprocess.TimeoutExpired:
            return ""


def curl(*args, timeout=10):
    return subprocess.run(["curl", *args], capture_output=True, text=True, timeout=timeout)


def bash(cmd, cwd=None, timeout=15):
    return subprocess.run(["bash", "-c", cmd], cwd=cwd, env=shim_env(), capture_output=True, text=True, timeout=timeout)


class Raw:
    """Tiny one-shot TCP server (where the claim is about *curl*, whichever `nc` is installed).
    Records the request it gets; answers with `reply`, or stays silent for `hang` seconds."""

    def __init__(self, reply=b"", hang=0):
        self.srv = socket.create_server(("127.0.0.1", 0))
        self.port = self.srv.getsockname()[1]
        self.request = b""
        self.reply, self.hang = reply, hang
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        try:
            conn, _ = self.srv.accept()
            with conn:
                conn.settimeout(3)
                data = b""
                while b"\r\n\r\n" not in data:
                    chunk = conn.recv(4096)
                    if not chunk:
                        break
                    data += chunk
                m = re.search(rb"Content-Length: (\d+)", data)
                if m:
                    need = int(m.group(1)) - len(data.split(b"\r\n\r\n", 1)[1])
                    while need > 0:
                        chunk = conn.recv(4096)
                        if not chunk:
                            break
                        data, need = data + chunk, need - len(chunk)
                self.request = data
                if self.hang:
                    time.sleep(self.hang)
                else:
                    conn.sendall(self.reply)
        except OSError:
            pass
        finally:
            self.srv.close()


def norm(line):
    line = line.rstrip("\r")
    line = re.sub(r"^(Date|Last-Modified): .*", r"\1: <v>", line)
    line = re.sub(r"^([<>]? ?)(Date|Last-Modified): .*", r"\1\2: <v>", line)
    line = re.sub(r"Python/[\d.]+", "Python/<v>", line)
    line = re.sub(r"curl/[\d.]+", "curl/<v>", line)
    return re.sub(r"localhost:\d+", "localhost:<port>", line)


class demo:
    """Builds the `demo` folder with the note's own set-up block and serves nothing yet."""

    def __enter__(self):
        self.tmp = tempfile.TemporaryDirectory()
        r = bash(block_with(note(NET), "mkdir demo"), cwd=self.tmp.name)
        if r.returncode:
            raise RuntimeError("the set-up block of the note failed: " + r.stderr)
        self.root = Path(self.tmp.name)
        self.dir = self.root / "demo"
        return self

    def __exit__(self, *a):
        self.tmp.cleanup()


def serve_default(d):
    """The note's `python -m http.server` block, as written (port 8000 if free, otherwise the same command + a free port)."""
    cmd = block_with(note(NET), "python -m http.server\n").strip()
    port = 8000
    if listening(8000):
        port = free_ports(1)[0]
        cmd += f" {port}"
    return Bg(cmd, cwd=d).wait_listen(port), port


# ---- curl ----------------------------------------------------------------- #
def curl_options():
    t = note(NET)
    with demo() as d:
        srv, p = serve_default(d.dir)
        u = f"localhost:{p}"
        try:
            body = curl("-s", f"{u}/a.txt").stdout
            i = curl("-s", "-i", f"{u}/a.txt").stdout
            head = curl("-s", "-I", f"{u}/a.txt").stdout
            v = curl("-s", "-v", f"{u}/a.txt")
            meter_on = "% Total" in curl(f"{u}/a.txt").stderr
            meter_off = "% Total" in curl("-s", f"{u}/a.txt").stderr
            out = Path(d.root, "saved.txt")
            curl("-s", "-o", str(out), f"{u}/a.txt")
            cwd_save = subprocess.run(["curl", "-sO", f"{u}/a.txt"], cwd=d.root, capture_output=True)
            no_follow = curl("-s", f"{u}/sub")
            follow = curl("-sL", f"{u}/sub").stdout
            code = curl("-s", "-o", "/dev/null", "-w", "%{http_code}\n", f"{u}/nope").stdout.strip()
            e404, e404f = curl("-s", "-o", "/dev/null", f"{u}/nope").returncode, curl("-sf", "-o", "/dev/null", f"{u}/nope").returncode
            hdr_add = curl("-s", "-H", "X-Test: 1", f"{u}/a.txt").returncode
            put = curl("-s", "-i", "-X", "PUT", f"{u}/a.txt").stdout.splitlines()[0]
            log = srv.stop()
        finally:
            srv.stop()
        saved = out.read_text() == "plain\n" and (d.root / "a.txt").read_text() == "plain\n"
    conds = {"GET body": body == "plain\n", "-i": i.startswith("HTTP/1.0 200 OK") and i.endswith("\n\nplain\n"),
             "-I": head.startswith("HTTP/1.0 200 OK") and head.endswith("\n\n") and "Content-Length: 6" in head and '"HEAD /a.txt HTTP/1.1" 200' in log,
             "-v": "> GET /a.txt HTTP/1.1" in v.stderr and "< HTTP/1.0 200 OK" in v.stderr and v.stdout == "plain\n",
             "progress meter": meter_on and not meter_off, "-o/-O": saved, "-L": no_follow.stdout == "" and follow == "<h1>Sub</h1>\n",
             "-w": code == "404", "-f": e404 == 0 and e404f == 22, "-H": hdr_add == 0, "-X": put.startswith("HTTP/1.0 501")}
    ok = all(conds.values())
    failed = [k for k, v_ in conds.items() if not v_]
    need = [r"`curl -i URL`\s*\|\s*\*\*i\*\*nclude the response headers", r"`curl -I URL`\s*\|\s*send a `HEAD` request", r"`curl -v URL`.*`>`.*`<`",
            r"progress meter", r"`curl -L URL`.*follow redirects", r"`curl -f URL`.*exit code `22`", r"the method becomes `POST`.*application/x-www-form-urlencoded"]
    return ok and all(has(t, n) for n in need), (
        f"against the note's own `python -m http.server`: plain GET prints the body only; -i adds the headers; -I sends HEAD (server log shows HEAD, no body, Content-Length 6); "
        f"-v shows '> GET /a.txt HTTP/1.1' and '< HTTP/1.0 200 OK'; progress meter appears when output is piped ({meter_on}) and -s hides it ({not meter_off}); "
        f"-o and -O save the body ({saved}); /sub without -L has an empty body, -L prints {follow.strip()!r}; -w gives {code}; 404 exits {e404} without -f and {e404f} with -f; -X PUT -> {put}; "
        f"the note's option table says so: {all(has(t, n) for n in need)}" + (f"; FAILED: {failed}" if failed else ""))


def curl_verbose_sample():
    t = note(NET)
    sample = [norm(l) for l in block_with(t, "* Connected to localhost", "txt").splitlines() if l[:1] in "<>"]
    with demo() as d:
        srv, p = serve_default(d.dir)
        try:
            r = curl("-sv", f"localhost:{p}/a.txt")
        finally:
            srv.stop()
    real = [norm(l) for l in r.stderr.splitlines() if l[:1] in "<>"]
    # the note shows an empty request line as '>' (no trailing space); compare ignoring trailing spaces
    same = [s.rstrip() for s in sample] == [x.rstrip() for x in real]
    return same, f"the '>' / '<' lines of the note's curl -v example equal the real ones (Date, Last-Modified, versions and port normalised): {same}" + ("" if same else f"; note {sample} vs real {real}")


def curl_exit_codes():
    t = note(NET)
    with demo() as d:
        srv, p = serve_default(d.dir)
        try:
            c404 = curl("-s", "-o", "/dev/null", f"localhost:{p}/nope").returncode
            c22 = curl("-sf", "-o", "/dev/null", f"localhost:{p}/nope").returncode
        finally:
            srv.stop()
    c6 = curl("-s", "http://no-such-host.invalid/").returncode
    c7 = curl("-s", f"localhost:{free_ports(1)[0]}").returncode
    hang = Raw(hang=4)
    c28 = curl("-s", "-m", "1", f"127.0.0.1:{hang.port}").returncode
    short = Raw(reply=b"HTTP/1.1 200 OK\r\nContent-Length: 20\r\n\r\nHello, world")
    r18 = curl("-sS", f"127.0.0.1:{short.port}")
    ok = (c404, c22, c7, c28, r18.returncode) == (0, 22, 7, 28, 18) and c6 == 6
    good = all(has(t, rf"\| `{code}` \|") for code in (0, 6, 7, 18, 22, 28))
    return ok and good, (f"404 without -f -> {c404}; unresolvable host -> {c6}; nothing listening -> {c7}; -m 1 on a silent server -> {c28}; Content-Length 20 but 12 bytes -> {r18.returncode} "
                         f"({r18.stderr.strip().splitlines()[-1] if r18.stderr.strip() else ''}); with -f on a 404 -> {c22}; the note's exit-code table lists all of them: {good}")


def curl_post_on_the_wire():
    t = note(NET)
    cases = {}
    for label, args in (("d", ["-d", "name=Ada&age=20"]), ("hdr", ["-H", "Content-Type: application/json", "-d", '{"name":"Ada"}']),
                        ("put", ["-X", "PUT", "-d", "x=1"]), ("head", ["-I"])):
        r = Raw(reply=b"HTTP/1.1 200 OK\r\nContent-Length: 0\r\nConnection: close\r\n\r\n")
        curl("-s", *args, f"127.0.0.1:{r.port}/api")
        time.sleep(0.2)
        cases[label] = r.request.decode()
    ok = (cases["d"].startswith("POST /api HTTP/1.1") and "Content-Length: 15" in cases["d"] and "Content-Type: application/x-www-form-urlencoded" in cases["d"]
          and cases["d"].endswith("\r\n\r\nname=Ada&age=20") and "Content-Type: application/json" in cases["hdr"] and cases["put"].startswith("PUT /api")
          and cases["head"].startswith("HEAD /api"))
    good = has(t, r"`POST / HTTP/1\.1` request with `Content-Length: 15`, `Content-Type: application/x-www-form-urlencoded` and the body `name=Ada&age=20`")
    return ok and good, (f"curl -d 'name=Ada&age=20' really sends {cases['d'].splitlines()[0]!r} + Content-Length 15 + form content type + that body; -H replaces the content type; "
                         f"-X PUT -> {cases['put'].splitlines()[0]!r}; -I -> {cases['head'].splitlines()[0]!r}; note says it: {good}")


# ---- python -m http.server ---------------------------------------------- #
def http_server_basics():
    t = note(NET)
    pa, pb, pc, pd = free_ports(4)
    ev = []
    with demo() as d:
        (d.dir / ".env").write_text("SECRET=1\n")
        srv, p = serve_default(d.dir)
        try:
            addr = listening(p)
            r_txt = curl("-s", "-i", f"localhost:{p}/a.txt").stdout
            r_301 = curl("-s", "-i", f"localhost:{p}/sub").stdout
            r_404 = curl("-s", "-i", f"localhost:{p}/nope").stdout.splitlines()[0]
            r_trav = curl("-s", "--path-as-is", "-o", "/dev/null", "-w", "%{http_code}", f"localhost:{p}/../../etc/passwd").stdout
            r_env = curl("-s", f"localhost:{p}/.env").stdout
            methods = {m: curl("-s", "-i", "-X", m, f"localhost:{p}/").stdout.splitlines()[0] for m in ("POST", "PUT", "DELETE")}
            curl("-s", "-I", f"localhost:{p}/a.txt")
            log = srv.stop()
        finally:
            srv.stop()
        # second server on the same port
        s1 = Bg(f"python -m http.server {pa}", cwd=d.dir).wait_listen(pa)
        s2 = Bg(f"python -m http.server {pa}", cwd=d.dir)
        time.sleep(1)
        in_use = s2.stop()
        s1.stop()
        # options
        s = Bg(subst("python -m http.server 9000", {"9000": pb, "8000": 0, "8080": 0}), cwd=d.dir).wait_listen(pb)
        opt_port = listening(pb)
        s.stop()
        s = Bg(f"python -m http.server {pc} -b 127.0.0.1", cwd=d.dir).wait_listen(pc)
        opt_bind = listening(pc)
        s.stop()
        s = Bg(f"python -m http.server {pd} -d demo", cwd=d.root).wait_listen(pd)
        opt_dir = curl("-s", f"localhost:{pd}/").stdout
        s.stop()
        s = Bg(f"python -m http.server {pa} --protocol HTTP/1.1", cwd=d.dir).wait_listen(pa)
        opt_proto = curl("-s", "-i", f"localhost:{pa}/a.txt").stdout.splitlines()[0]
        s.stop()
        s = Bg("python -m http.server 0", cwd=d.dir)
        time.sleep(1)
        p0 = re.search(r"Serving HTTP on 0\.0\.0\.0 port (\d+)", s.stop())
    start = re.match(r"Serving HTTP on 0\.0\.0\.0 port %d \(http://0\.0\.0\.0:%d/\) \.\.\." % (p, p), log)
    hdr = all(h in r_txt for h in ("Server: SimpleHTTP/0.6 Python/", "Content-type: text/plain", "Content-Length: 6", "Last-Modified: "))
    logs = (re.search(r'127\.0\.0\.1 - - \[\d\d/\w{3}/\d{4} [\d:]+\] "GET /a\.txt HTTP/1\.1" 200 -', log) and "code 404, message File not found" in log
            and re.search(r'"GET /sub HTTP/1\.1" 301 -', log))
    ok = (addr == ["00000000"] and start and r_txt.startswith("HTTP/1.0 200 OK") and hdr and r_301.startswith("HTTP/1.0 301 Moved Permanently") and "Location: /sub/" in r_301
          and r_404.startswith("HTTP/1.0 404 File not found") and r_trav == "404" and r_env == "SECRET=1\n" and all("501 Unsupported method" in v for v in methods.values())
          and logs and "Address already in use" in in_use and opt_port == ["00000000"] and opt_bind == ["0100007F"] and opt_dir == "<h1>Home</h1>\n"
          and opt_proto.startswith("HTTP/1.1 200 OK") and p0)
    good = (has(t, r"Serving HTTP on 0\.0\.0\.0 port 8000 \(http://0\.0\.0\.0:8000/\) \.\.\.") and has(t, r"Default port is \*\*8000\*\*") and has(t, r"`501 Unsupported method`")
            and has(t, r"The status line says `HTTP/1\.0` by default") and has(t, r"`GET /\.\./\.\./etc/passwd` \| `404`") and has(t, r"including hidden ones such as `\.env`")
            and has(t, r"OSError: \[Errno 98\] Address already in use"))
    return bool(ok) and good, (
        f"default command listens on 0.0.0.0 (hex {addr[0] if addr else None}) and prints the startup line of the note ({bool(start)}); status line HTTP/1.0, headers Server/Content-type/Content-Length/Last-Modified ({hdr}); "
        f"/sub -> 301 Location /sub/; /nope -> 404; ../ traversal -> {r_trav}; .env is served ({r_env.strip()!r}); POST/PUT/DELETE -> 501; access-log lines as shown ({bool(logs)}); "
        f"second server on a used port -> 'Address already in use' ({'Address already in use' in in_use}); positional port, -b 127.0.0.1 (listens on {opt_bind}), -d, --protocol HTTP/1.1 ({opt_proto}) and port 0 (picks {p0.group(1) if p0 else None}) work; note says so: {good}")


def index_html_behaviour():
    t = note(NET)
    p = free_ports(1)[0]
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        for name, files in {"one": {"index.html": "<p>html</p>"}, "none": {"x.txt": "x"}, "htm": {"index.htm": "<p>htm</p>"},
                            "both": {"index.html": "<p>html</p>", "index.htm": "<p>htm</p>"}, "caps": {"Index.html": "<p>caps</p>"},
                            "sub": {"index.html": "<p>sub page</p>"}}.items():
            (root / name).mkdir()
            for f, c in files.items():
                (root / name / f).write_text(c)
        srv = Bg(f"python -m http.server {p}", cwd=root).wait_listen(p)
        try:
            get = lambda path, *a: curl("-s", *a, f"localhost:{p}{path}").stdout
            one = get("/one/", "-i")
            nonexist = get("/none/")
            htm, both, caps = get("/htm/"), get("/both/"), get("/caps/")
            sub_slash = get("/sub/")
            sub_noslash = get("/sub", "-i")
        finally:
            srv.stop()
    rel = (urljoin("http://h/sub/", "page2.html"), urljoin("http://h/sub", "page2.html"))
    ok = (one.startswith("HTTP/1.0 200 OK") and "Content-type: text/html" in one and one.endswith("<p>html</p>") and "<title>Directory listing for /none/</title>" in nonexist and 'href="x.txt"' in nonexist
          and htm == "<p>htm</p>" and both == "<p>html</p>" and "Directory listing for /caps/" in caps and 'href="Index.html"' in caps
          and sub_slash == "<p>sub page</p>" and sub_noslash.startswith("HTTP/1.0 301") and "Location: /sub/" in sub_noslash
          and rel == ("http://h/sub/page2.html", "http://h/page2.html"))
    good = (has(t, r"\| `index\.html` \| the page itself \(`200`, `Content-type: text/html`\) \|") and has(t, r'automatic listing\*\* titled "Directory listing for /"')
            and has(t, r"only `index\.htm` \| `index\.htm` is served \(it is the second choice\)") and has(t, r"both `index\.html` and `index\.htm` \| `index\.html` wins")
            and has(t, r"`Index\.html` \(capital `I`\) on Linux \| \*\*not recognised\*\*") and has(t, r"a link `page2\.html` on `/sub/` means `/sub/page2\.html`, but on `/sub` it would mean `/page2\.html`"))
    return ok and good, (f"GET / -> index.html (200, text/html); no index -> 'Directory listing for /none/' with a link to every file; only index.htm -> served; both -> index.html wins; "
                         f"Index.html (capital I) -> listing, not the page; /sub/ -> sub/index.html; /sub -> 301 to /sub/; relative link page2.html resolves to {rel[0]} on '/sub/' and {rel[1]} on '/sub' (urllib.parse.urljoin); note says it: {good}")


NET_BROWSER_JS = r"""
const { chromium } = require('playwright'); const { spawn } = require('child_process'); const fs = require('fs');
const sleep = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  const inp = JSON.parse(fs.readFileSync(process.argv[2], 'utf8')); const out = { cases: [] };
  const b = await chromium.launch(); const page = await b.newPage();
  const probe = async () => ({ color: await page.evaluate(() => getComputedStyle(document.getElementById('h')).color), title: await page.title() });
  await page.goto('file://' + inp.web + '/index.html'); await sleep(500); out.file = await probe();
  const srv = spawn('python3', ['-m', 'http.server', String(inp.http_port)], { cwd: inp.web, stdio: 'ignore' }); await sleep(1000);
  await page.goto('http://localhost:' + inp.http_port + '/'); await sleep(500); out.http = await probe(); srv.kill();
  for (const c of inp.cases) {
    const nc = spawn('bash', ['-c', c.cmd], { stdio: ['ignore', 'pipe', 'ignore'], detached: true }); let req = ''; nc.stdout.on('data', d => req += d);
    await sleep(600); const p = await b.newPage(); const r = { label: c.label };
    try { const resp = await p.goto('http://localhost:' + c.port + '/', { timeout: 4000 }); r.status = resp.status(); r.text = (await p.evaluate(() => document.body.innerText)).trim(); }
    catch (e) { r.error = e.message.split('\n')[0]; }
    await sleep(300); r.request = req; try { process.kill(-nc.pid, 'SIGKILL'); } catch (e) {} await p.close(); out.cases.push(r);
  }
  console.log(JSON.stringify(out)); await b.close();
})();
"""


def browser_checks():
    node = shutil.which("node")
    if not node or not shutil.which("nc"):
        SKIPPED.append("Chromium checks of the curl / http.server / nc note skipped (needs node + playwright, and nc)")
        print("[SKIP ] " + NET + "  browser checks (node / nc missing)\n")
        return None
    t = note(NET)
    pa, pb, pc = free_ports(3)
    with tempfile.TemporaryDirectory() as tmp:
        web = Path(tmp, "web")
        web.mkdir()
        (web / "index.html").write_text('<!DOCTYPE html><html><head><meta charset="utf-8"><title>T</title><link rel="stylesheet" href="/style.css"></head>'
                                        '<body><h1 id="h">Hello</h1><script>fetch("data.json").then(r=>r.json()).then(j=>{document.title="fetched "+j.n})'
                                        '.catch(e=>{document.title="fetch failed"})</script></body></html>')
        (web / "style.css").write_text("h1{color:rgb(255, 0, 0)}")
        (web / "data.json").write_text('{"n": 7}')
        one_shot = subst(block_with(t, "Hello, world' | nc -l 8080"), {"8000": 0, "8080": pb, "9000": 0}).strip()   # nc's stdout = the request the browser sent
        Path(tmp, "in.json").write_text(json.dumps({"web": str(web), "http_port": pa, "cases": [
            {"label": "one-shot", "cmd": one_shot, "port": pb},
            {"label": "raw", "cmd": f"echo hello | nc -N -l {pc}", "port": pc}]}))
        Path(tmp, "b.js").write_text(NET_BROWSER_JS)
        env = dict(os.environ, NODE_PATH=subprocess.run(["npm", "root", "-g"], capture_output=True, text=True).stdout.strip())
        p = subprocess.run([node, str(Path(tmp, "b.js")), str(Path(tmp, "in.json"))], capture_output=True, text=True, env=env, timeout=120)
        if p.returncode:
            SKIPPED.append("Chromium checks of the curl / http.server / nc note skipped (playwright could not run)")
            print("[SKIP ] " + NET + "  browser checks (playwright could not run)\n")
            return None
        res = json.loads(p.stdout.strip().splitlines()[-1])
    one = next(c for c in res["cases"] if c["label"] == "one-shot")
    raw = next(c for c in res["cases"] if c["label"] == "raw")
    ok = (res["file"]["color"] == "rgb(0, 0, 0)" and res["file"]["title"] == "fetch failed" and res["http"]["color"] == "rgb(255, 0, 0)" and res["http"]["title"] == "fetched 7"
          and one.get("status") == 200 and one.get("text") == "Hello, world" and one["request"].startswith("GET / HTTP/1.1") and f"Host: localhost:{pb}" in one["request"]
          and "ERR_INVALID_HTTP_RESPONSE" in raw.get("error", ""))
    good = (has(t, r"`/style\.css` \(root-relative link\) \| looked for `file:///style\.css`: \*\*style not applied\*\*") and has(t, r"`fetch\('data\.json'\)` \| \*\*blocked\*\* by the browser")
            and has(t, r"\| Chromium \| `net::ERR_INVALID_HTTP_RESPONSE` \|") and has(t, r"the text appears"))
    return ok and good, (f"Chromium: page opened from file:// -> h1 colour {res['file']['color']} (the /style.css link failed), title '{res['file']['title']}'; from the served folder -> {res['http']['color']}, '{res['http']['title']}'; "
                         f"the note's one-line nc string server shows '{one.get('text')}' in the browser and nc printed the browser's request ({one['request'].splitlines()[0] if one['request'] else None!r}); "
                         f"a bare string via nc -> {raw.get('error')}; note says so: {good}")


# ---- nc ------------------------------------------------------------------- #
def nc_variants():
    t = note(NET)
    HL = r"printf 'HTTP/1.1 200 OK\r\nContent-Length: 6\r\nConnection: close\r\n\r\nlength'"
    H = r"printf 'HTTP/1.1 200 OK\r\nConnection: close\r\n\r\nno length'"
    found, rows = {}, {}

    def attempt(label, cmd, port):
        s = Bg(cmd)
        time.sleep(0.8)
        try:
            t0 = time.time()
            r = curl("-s", "-m", "2", f"localhost:{port}")
            return r.returncode, r.stdout.strip(), round(time.time() - t0, 1)
        finally:
            s.stop()

    for name, exe, plain, withp, fix in (("OpenBSD", "nc.openbsd", "nc.openbsd -l {p}", "nc.openbsd -l -p {p}", "nc.openbsd -N -l {p}"),
                                         ("traditional", "nc.traditional", "nc.traditional -l {p}", "nc.traditional -l -p {p}", "nc.traditional -q 0 -l -p {p}"),
                                         ("ncat", "ncat", "ncat -l {p}", "ncat -l -p {p}", None)):
        if not shutil.which(exe):
            SKIPPED.append(f"netcat variant '{name}' ({exe}) is not installed here: its row of the variant table was not executed")
            continue
        a, b, c = free_ports(3)
        res = {"plain": attempt(name, f"{HL} | " + plain.format(p=a), a), "with_p": attempt(name, f"{HL} | " + withp.format(p=b), b)}
        d, e = free_ports(2)
        res["no_cl"] = attempt(name, f"{H} | " + withp.format(p=d), d)
        if fix:
            res["fixed"] = attempt(name, f"{H} | " + fix.format(p=e), e)
        rows[name] = res
    exp = {"OpenBSD": {"plain": 0, "with_p": 0, "no_cl": 28, "fixed": 0}, "traditional": {"plain": 7, "with_p": 0, "no_cl": 28, "fixed": 0}, "ncat": {"plain": 0, "with_p": 0, "no_cl": 0}}
    ok = bool(rows) and all({k: v[0] for k, v in r.items()} == exp[n] for n, r in rows.items())
    good = (has(t, r"\*\*OpenBSD netcat\*\*.*\| yes \| yes \(Debian / Ubuntu build\) \| \*\*no\*\*, unless `-N` is given") and has(t, r"\*\*Traditional netcat\*\*.*\| \*\*no\*\*, it needs `-p`.*\| yes \| \*\*no\*\*, unless `-q 0` is given")
            and has(t, r"\*\*Ncat\*\*.*\| yes \| yes \| yes \|"))
    return ok and good, ("curl exit codes per variant ('plain' = nc -l PORT, 'with_p' = nc -l -p PORT, both with Content-Length; 'no_cl' = no Content-Length; 'fixed' = -N / -q 0): "
                         + "; ".join(f"{n}: " + ", ".join(f"{k}={v[0]}" for k, v in r.items()) for n, r in rows.items()) + f"; note's variant table matches: {good}")


def nc_client_by_hand():
    t = note(NET)
    with demo() as d:
        pa, pb = free_ports(2)
        srv = Bg(f"python -m http.server {pa}", cwd=d.dir).wait_listen(pa)
        block = subst(block_with(t, "printf 'GET / HTTP/1.1"), {"8000": pa, "8080": 0, "9000": 0})
        r = bash(block, timeout=10)
        shown = [norm(l) for l in block_with(t, "HTTP/1.0 200 OK\nServer: SimpleHTTP", "txt").splitlines()]
        real = [norm(l) for l in r.stdout.splitlines()]
        no_blank = bash(f"printf 'GET / HTTP/1.1\\r\\nHost: localhost\\r\\nConnection: close\\r\\n' | timeout 2 nc localhost {pa}")
        srv.stop()
        s11 = Bg(f"python -m http.server {pb} --protocol HTTP/1.1", cwd=d.dir).wait_listen(pb)
        t0 = time.time()
        keep = bash(f"printf 'GET / HTTP/1.1\\r\\nHost: localhost\\r\\n\\r\\n' | timeout 2 nc localhost {pb}")
        closed = bash(f"printf 'GET / HTTP/1.1\\r\\nHost: localhost\\r\\nConnection: close\\r\\n\\r\\n' | timeout 2 nc localhost {pb}")
        s11.stop()
    dash = subprocess.run(["sh", "-c", 'echo -e "a\\r\\nb"'], capture_output=True).stdout
    is_dash = os.path.realpath("/bin/sh").endswith("dash")
    ok = (r.returncode == 0 and real == shown and no_blank.returncode == 124 and no_blank.stdout == "" and keep.returncode == 124 and closed.returncode == 0
          and closed.stdout.startswith("HTTP/1.0") is False and closed.stdout.startswith("HTTP/1.1 200 OK")
          and (dash.startswith(b"-e ") or not is_dash))
    good = (has(t, r"Without that empty line the server keeps waiting") and has(t, r"`echo -e \"a\\r\\nb\"` prints a literal `-e` first") and has(t, r"Use \*\*`printf`\*\*"))
    return ok and good, (f"the note's `printf 'GET / ...' | nc localhost 8000` prints exactly the response shown in the note ({real == shown}); without the final empty line the server never answers (exit {no_blank.returncode}, no output); "
                         f"a keep-alive HTTP/1.1 server without 'Connection: close' leaves nc waiting (exit {keep.returncode} = timeout), with it nc returns ({closed.returncode}); "
                         f"in dash `echo -e` prints a literal '-e': {dash.startswith(b'-e ')} (/bin/sh is {'dash' if is_dash else 'not dash here'}); note says it: {good}")


def nc_string_server():
    t = note(NET)
    if "OpenBSD netcat" not in subprocess.run(["bash", "-c", "nc -h 2>&1 | head -1"], capture_output=True, text=True).stdout:
        SKIPPED.append("the `nc` on PATH is not OpenBSD netcat: the string-server examples were not executed with it")
        return True, "skipped: `nc` on PATH is not OpenBSD netcat"
    pa, pb, pc, pd = free_ports(4)
    m = lambda port: {"8000": 0, "8080": port, "9000": 0}
    template = block_with(t, "Hello, world' | nc -l 8080")
    one = subst(template, m(pa))
    s = Bg(one).wait_listen(pa)
    r = curl("-s", "-i", f"localhost:{pa}")
    time.sleep(0.3)
    second = curl("-s", "-m", "3", f"localhost:{pa}").returncode
    request = s.stop()
    shown_resp = [l for l in block_with(t, "Content-Length: 12\n", "txt").splitlines()]
    shown_req = [l for l in block_with(t, "GET / HTTP/1.1\nHost: localhost:8080", "txt").splitlines()]
    resp_ok = [x.rstrip("\r") for x in r.stdout.splitlines()] == shown_resp
    req_ok = [norm(x) for x in request.splitlines()][:len(shown_req)] == [norm(x) for x in shown_req]
    # Content-Length lies
    def lie(n, flag=""):
        cmd = template.replace("Content-Length: 12", f"Content-Length: {n}").replace("| nc -l", f"| nc {flag}-l")
        s2 = Bg(subst(cmd, m(pb))).wait_listen(pb)
        rr = curl("-sS", "-m", "2", f"localhost:{pb}")
        s2.stop()
        return rr
    r5, r20_plain, r20 = lie(5), lie(20), lie(20, "-N ")
    # the loop of the note
    loop = subst(block_with(t, "while true"), m(pc))
    s3 = Bg(loop).wait_listen(pc)
    t_start = time.time()
    time.sleep(2.2)
    a1 = curl("-s", "-m", "3", f"localhost:{pc}")
    t_first = time.time()
    time.sleep(2.2)
    a2 = curl("-s", "-m", "3", f"localhost:{pc}")
    s3.stop()

    def secs(x):
        h, mi, se = map(int, re.search(r"(\d\d):(\d\d):(\d\d)", x).groups())
        return h * 3600 + mi * 60 + se
    tod = lambda ts: (lambda g: g.tm_hour * 3600 + g.tm_min * 60 + g.tm_sec)(time.gmtime(ts))
    stale1 = abs(secs(a1.stdout) - tod(t_start)) <= 1 and tod(t_first) - secs(a1.stdout) >= 2        # first reply: the moment the loop started
    stale2 = abs(secs(a2.stdout) - tod(t_first)) <= 1 and tod(t_first + 2.2) - secs(a2.stdout) >= 2  # second reply: the moment the first request was answered
    # no Content-Length: hang, and the -N fix; week-5 style loop
    nocl = "printf 'HTTP/1.1 200 OK\\r\\nContent-Type: text/plain\\r\\nConnection: close\\r\\n\\r\\nno length'"
    h1 = Bg(nocl + f" | nc -l {pd}").wait_listen(pd)
    hang = curl("-s", "-m", "2", f"localhost:{pd}")
    h1.stop()
    pe = free_ports(1)[0]
    h2 = Bg(nocl + f" | nc -N -l {pe}").wait_listen(pe)
    fixed = curl("-s", "-m", "2", f"localhost:{pe}")
    h2.stop()
    pf = free_ports(1)[0]
    w5 = Bg(f'echo -e "HTTP/1.1 200 OK\\r\\n\\r\\n$(date)" | nc -l -p {pf}').wait_listen(pf)
    w5r = curl("-s", "-m", "2", f"localhost:{pf}")
    w5.stop()
    # -k
    pg = free_ports(1)[0]
    k = Bg(f"printf 'HTTP/1.1 200 OK\\r\\nConnection: close\\r\\nContent-Length: 2\\r\\n\\r\\nhi' | timeout 6 nc -k -l {pg}").wait_listen(pg)
    k1, k2 = curl("-s", "-m", "2", f"localhost:{pg}"), curl("-s", "-m", "2", f"localhost:{pg}")
    k.stop()
    # a bare string is not HTTP (every client gets its own server and port)
    def raw(client, flag="-N "):
        port = free_ports(1)[0]
        b = Bg(f"echo hello | nc {flag}-l {port}").wait_listen(port)
        try:
            return client(port)
        finally:
            b.stop()
    r_plain = raw(lambda port: curl("-sS", "-m", "3", f"localhost:{port}"))
    r_http09 = raw(lambda port: curl("-s", "--http0.9", "-m", "3", f"localhost:{port}"))
    r_nc = raw(lambda port: bash(f"timeout 5 nc localhost {port} </dev/null"))
    r_nc_wait = raw(lambda port: bash(f"timeout 2 nc localhost {port} </dev/null"), flag="")     # plain nc -l never closes: the client prints hello, then waits
    # who can connect
    pi, pj = free_ports(2)
    b1 = Bg(f"sleep 3 | nc -l {pi}").wait_listen(pi)
    b2 = Bg(f"sleep 3 | nc -l 127.0.0.1 {pj}").wait_listen(pj)
    bind_all, bind_lo = sorted(set(listening(pi))), sorted(set(listening(pj)))
    b1.stop(), b2.stop()
    bytes_ = bash("printf 'é' | wc -c; printf %s 'Hello, world' | wc -c").stdout.split()
    ok = (r.returncode == 0 and resp_ok and req_ok and second == 7 and r5.stdout == "Hello" and r5.returncode == 0
          and r20.stdout == "Hello, world" and r20.returncode == 18 and "8 bytes remaining" in r20.stderr
          and r20_plain.stdout == "Hello, world" and r20_plain.returncode == 28
          and a1.returncode == a2.returncode == 0 and stale1 and stale2
          and hang.returncode == 28 and hang.stdout == "no length" and fixed.returncode == 0 and fixed.stdout == "no length" and w5r.returncode == 28 and w5r.stdout.startswith("HTTP/") is False
          and k1.stdout == "hi" and k2.returncode == 28 and k2.stdout == ""
          and r_plain.returncode == 1 and "Received HTTP/0.9 when not allowed" in r_plain.stderr and r_http09.stdout.strip() == "hello" and r_nc.stdout.strip() == "hello"
          and r_nc_wait.stdout.strip() == "hello" and r_nc_wait.returncode == 124
          and bind_all == ["00000000"] and bind_lo == ["0100007F"] and bytes_ == ["2", "12"])
    good = (has(t, r"\*\*`nc` serves one connection and exits\.\*\*") and has(t, r"prints only `Hello`, the rest is ignored") and has(t, r"curl: \(18\) transfer closed with 8 bytes remaining to read")
            and has(t, r"curl keeps waiting for the 8 missing bytes")
            and has(t, r"curl prints the date and then hangs until `Ctrl\+C`") and has(t, r"the second client gets no response \(curl waits until it times out\)")
            and has(t, r"curl: \(1\) Received HTTP/0\.9 when not allowed") and has(t, r"`nc -l 127\.0\.0\.1 8080`") and has(t, r"then waits; stop it with `Ctrl\+C`") and has(t, r"`é` is 2 bytes in UTF-8") and has(t, r"`\$\(date\)` runs when the loop round \*\*starts\*\*"))
    return bool(ok) and good, (
        f"the note's one-line string server: curl -i prints exactly the response shown ({resp_ok}); nc printed the request shown ({req_ok}); a second curl -> exit {second} (served once, then gone); "
        f"Content-Length 5 -> {r5.stdout!r}; 20 with a plain nc -> {r20_plain.stdout!r} then curl waits (exit {r20_plain.returncode} = timeout), with nc -N the connection closes -> exit {r20.returncode} ('{r20.stderr.strip().splitlines()[-1] if r20.stderr.strip() else ''}'); the note's while-loop answers repeatedly, but each time shown is the moment its round started, not the moment of the request (loop started, first curl 2.2 s later got {a1.stdout.strip()!r}; the next reply shows when the first request was answered: {a2.stdout.strip()!r}): {stale1 and stale2}; "
        f"no Content-Length: body arrives but curl waits (exit {hang.returncode}), with nc -N exit {fixed.returncode}; the week-5 style loop (echo -e ... | nc -l -p) hangs too (exit {w5r.returncode}); nc -k: 1st {k1.stdout!r}, 2nd exit {k2.returncode}; "
        f"bare string: curl exit {r_plain.returncode} ('{r_plain.stderr.strip().splitlines()[-1] if r_plain.stderr.strip() else ''}'), --http0.9 -> {r_http09.stdout.strip()!r}, nc client -> {r_nc.stdout.strip()!r} (and with a plain nc -l server it then waits: exit {r_nc_wait.returncode} = timeout); "
        f"nc -l PORT listens on 0.0.0.0 ({bind_all}), nc -l 127.0.0.1 PORT on loopback ({bind_lo}); 'é' = {bytes_[0]} bytes; note says all of this: {good}")


def python_socket_server():
    t = note(NET)
    p = free_ports(1)[0]
    code = subst(block_with(t, "socket.create_server", "python"), {"8000": 0, "8080": p, "9000": 0})
    with tempfile.TemporaryDirectory() as tmp:
        Path(tmp, "srv.py").write_text(code)
        s = Bg(f"python srv.py", cwd=tmp).wait_listen(p)
        t0 = time.time()
        r1, r2 = curl("-s", "-i", "-m", "3", f"localhost:{p}"), curl("-s", "-m", "3", f"localhost:{p}")
        dt = time.time() - t0
        addr = listening(p)
        s.stop()
    ok = (r1.returncode == 0 and r1.stdout.replace("\r\n", "\n") == "HTTP/1.1 200 OK\nContent-Type: text/plain\nContent-Length: 12\nConnection: close\n\nHello, world"
          and r2.stdout == "Hello, world" and dt < 2 and addr == ["0100007F"])
    good = has(t, r"leaving the `with` block closes the connection \(so there is no hang\)") and has(t, r"`socket\.create_server`|socket\.create_server")
    return ok and good, (f"the note's socket server answers repeatedly ({r1.stdout.splitlines()[0]!r}, body {r2.stdout!r}), needs no Content-Length workaround and nobody hangs (2 requests in {dt:.1f}s); "
                         f"it listens on 127.0.0.1 only ({addr}); note says it: {good}")


def exercises_and_lab():
    t = note(NET)
    answers = re.findall(r"<summary>Answer</summary>\n\n(.*?)\n\n</details>", t, re.S)
    pa, pb = free_ports(2)
    with tempfile.TemporaryDirectory() as tmp:
        site = Path(tmp, "site")
        site.mkdir()
        (site / "index.html").write_text("<p>site</p>")
        cmd = subst(block_with(answers[0], "http.server 9000", "bash"), {"9000": pa, "8000": 0, "8080": 0}).strip()
        s = Bg(cmd, cwd=tmp).wait_listen(pa)
        ex1 = (listening(pa), curl("-s", f"localhost:{pa}/").stdout)
        s.stop()
    with demo() as d:
        srv = Bg(f"python -m http.server {pb}", cwd=d.dir).wait_listen(pb)
        plain = curl("-s", f"localhost:{pb}/sub")
        i = curl("-s", "-i", f"localhost:{pb}/sub").stdout
        followed = curl("-sL", f"localhost:{pb}/sub").stdout
        direct = curl("-s", f"localhost:{pb}/sub/").stdout
        srv.stop()
    ex2 = plain.stdout == "" and "301 Moved Permanently" in i and "Location: /sub/" in i and followed == direct == "<h1>Sub</h1>\n"
    ok = ex1 == (["0100007F"], "<p>site</p>") and ex2 and len(answers) == 4
    good = (len(answers) == 4 and "`--bind 127.0.0.1` restricts it to this machine" in answers[0] and "`Location: /sub/`" in answers[1] and "`curl -L localhost:8000/sub`" in answers[1]
            and "prints `Hello`" in answers[2] and "keeps waiting for the 8 missing bytes" in answers[2] and "exit code 18" in answers[2] and "`ERR_INVALID_HTTP_RESPONSE`" in answers[3] and "raw TCP client" in answers[3])
    return ok and good, (f"exercise 1: the note's command listens on {ex1[0]} (loopback only) and serves the `site` folder ({ex1[1]!r}); exercise 2: /sub gives an empty body, curl -i shows 301 + Location: /sub/, "
                         f"-L and /sub/ both print the page ({ex2}); exercises 3 and 4 were run in the nc checks above; all 4 answers say this: {good}")


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
    if shutil.which("curl") and shutil.which("nc") and Path("/proc/net/tcp").exists():
        check(NET, "curl options of the table (-i -I -v -s -o -O -L -w -f -X), progress meter, 404 does not fail without -f", curl_options)
        check(NET, "the curl -v example equals the real request / response lines", curl_verbose_sample)
        check(NET, "curl exit codes 0 / 6 / 7 / 18 / 22 / 28 as listed", curl_exit_codes)
        check(NET, "curl -d / -H / -X / -I put exactly the shown bytes on the wire (POST + Content-Length 15 + form content type)", curl_post_on_the_wire)
        check(NET, "python -m http.server: default 0.0.0.0:8000, options, URL table (301 / 404 / 501), headers, log lines, .env served, port in use", http_server_basics)
        check(NET, "index.html: default document, listing without it, index.htm, case, /sub -> /sub/, relative links", index_html_behaviour)
        b = browser_checks()
        if b is not None:
            check(NET, "Chromium: file:// vs http:// (root-relative CSS, fetch), the browser's request printed by nc, bare string -> ERR_INVALID_HTTP_RESPONSE", lambda: b)
        check(NET, "netcat variants: `-l PORT` vs `-l -p PORT`, who closes the connection (OpenBSD / traditional / ncat)", nc_variants)
        check(NET, "nc as a client: the typed request prints the shown response; empty line needed; Connection: close; echo -e vs printf", nc_client_by_hand)
        check(NET, "nc as a string server: one-line server, request seen by nc, Content-Length 5 / 20, loop, -N / no Content-Length hang, -k, bare string, bind address", nc_string_server)
        check(NET, "the pure-Python string server of the note works and does not hang", python_socket_server)
        check(NET, "the four practice exercises and their answers", exercises_and_lab)
    else:
        SKIPPED.append("curl / nc / python -m http.server checks skipped (needs curl, nc and Linux /proc)")
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
        "1-5: Apache `DirectoryIndex`, nginx `index`, GitHub Pages serving index.html, production servers answering 403 / 404 instead of a listing (server documentation, not run here)",
        "1-5: ports below 1024 need administrator rights (this sandbox runs as root), Windows specifics (py -m http.server, no nc by default, WSL), `OSError: [Errno 98]` is the Linux error number, macOS / non-Debian nc builds",
        "1-5: docs.python.org / everything.curl.dev / MDN links (blocked from this sandbox)",
    ]:
        print("  -", s)
    sys.exit(1 if wrong else 0)
