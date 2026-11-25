# WebAssembly and Browser Security

A web page is **code from a stranger that your browser runs on your computer**. The browser must make that safe, while still letting the code do useful, even heavy, work. This page covers the two sides: what the browser can run (including **WebAssembly**), and how it keeps you safe, plus the attacks that remain (malicious scripts, crypto-mining, DoS) and their defences (SRI, rate limiting, CAPTCHA).

## WebAssembly (WASM)

**WebAssembly** is a compact **binary instruction format** that browsers execute alongside JavaScript. You do not write it by hand: you write C, C++ or Rust and a compiler produces a `.wasm` file.

* **Compiler**: **Emscripten** compiles C/C++ to WebAssembly (plus the JavaScript glue code to load it). It maps OpenGL calls to the browser's WebGL, so graphics-heavy programs and simulations written for the desktop can run in a page.
* **Fast**: the binary is already close to machine code, small to download and quick to start, so heavy computations (image/video processing, games, simulations, CAD) can run at *near-native* speed.
* **Safe**: it runs in the same **sandbox** as JavaScript. By itself a WebAssembly module can only compute on its own memory; it cannot open files, use the network or touch the page unless the host JavaScript **gives it functions to call** (imports).
* **Not a replacement for JavaScript**: WebAssembly cannot modify the DOM directly. JavaScript loads the module, passes data in and reads results out. For ordinary page logic JavaScript remains the right tool, and WebAssembly adoption is still much smaller.

> [!NOTE]
> The slides mention file-system access, camera, sensors and payments next to WebAssembly. Those are **Web APIs that JavaScript calls** (each needing user permission, see [Permissions](#permissions)), not features of WebAssembly itself. WebAssembly's job is fast computation.

### A stack machine

WebAssembly code runs on a **stack-based virtual machine**: instructions do not name registers; they **push values onto a stack and pop operands off it**. The text form (**WAT**) of a function that adds two integers:

```wat
(module
  (func (export "add") (param i32 i32) (result i32)
    local.get 0      ;; push the first parameter
    local.get 1      ;; push the second parameter
    i32.add))        ;; pop two values, push their sum (the result)
```

Assembled with the WebAssembly Binary Toolkit (`wat2wasm`), this module is **41 bytes**. Here are the bytes:

```text
00 61 73 6d  01 00 00 00     magic number "\0asm", then version 1
01 07 01 60 02 7f 7f 01 7f   type section: one function type (i32, i32) -> i32
03 02 01 00                  function section: one function, using type 0
07 07 01 03 61 64 64 00 00   export section: the name "add" (61 64 64) -> function 0
0a 09 01 07 00               code section: body of 7 bytes, no locals
   20 00   local.get 0
   20 01   local.get 1
   6a      i32.add
   0b      end
```

Because it is just bytes, you can load it from JavaScript with no tooling at all. This ran unchanged in Node.js and in Chromium:

```javascript
const bytes = new Uint8Array([
  0x00, 0x61, 0x73, 0x6d, 0x01, 0x00, 0x00, 0x00,
  0x01, 0x07, 0x01, 0x60, 0x02, 0x7f, 0x7f, 0x01, 0x7f,
  0x03, 0x02, 0x01, 0x00,
  0x07, 0x07, 0x01, 0x03, 0x61, 0x64, 0x64, 0x00, 0x00,
  0x0a, 0x09, 0x01, 0x07, 0x00, 0x20, 0x00, 0x20, 0x01, 0x6a, 0x0b,
]);

WebAssembly.instantiate(bytes, {}).then(({ instance }) => {
  console.log(instance.exports.add(2, 3));   // 5
});
```

(Real projects load a file instead: `WebAssembly.instantiateStreaming(fetch("add.wasm"), imports)`.) The second argument `{}` is the **import object**, the only things the module is allowed to call. Its list of imports can be read before running it: for this module, `WebAssembly.Module.imports(module)` is empty, so it has **no way to reach anything outside itself**.

### What the engine guarantees

Checked with real modules in Node.js (V8):

| Claim | Observed |
| ----- | -------- |
| The binary is validated before it runs | A corrupted module is rejected with `CompileError`, nothing executes |
| Integers are fixed-width and wrap around | `i32` addition of `2147483647 + 1` gives `-2147483648` |
| Memory is a bounded array | Reading beyond the 65,536-byte page raises a **trap** (`RuntimeError: memory access out of bounds`) instead of reading someone else's memory |
| It can be a real program | A recursive `fac(10)` function in WebAssembly returns `3628800` |

This is what "sandboxed with controlled access" means in practice.

## The browser sandbox

The browser runs page scripts in a **restricted execution environment**:

* No access to your **files** and **operating system**: a page cannot read `/etc/passwd`. In a test, `fetch("file:///etc/passwd")` from a page failed with a `TypeError`, and Node-style objects such as `require` or `process` do not exist in page JavaScript.
* No running programs, no raw network sockets. A page can only make **HTTP(S) and WebSocket** requests, and those are limited by the same-origin policy below.
* It can keep **limited data per origin** in `localStorage`, `sessionStorage` and IndexedDB (see [Web storage](8-async-dom.md#web-storage)).
* Powerful features (location, camera, microphone, notifications) require **permission**.
* A runaway script cannot take down the browser or other sites: modern browsers run sites in separate processes, so one slow tab is not another's problem, but a page can still burn CPU *within its own tab* (see [DoS](#denial-of-service-dos)).

The sandbox is much like a virtual machine, but at a higher level: instead of emulating a computer, it restricts which *APIs* are available. A sandbox is only as strong as the browser's code: bugs in the browser or the JavaScript engine can let a malicious page **escape** it, which is why you keep your browser **updated**.

### Same-origin policy and CORS

An **origin** is the combination of **scheme + host + port** (`http://localhost:5000` and `http://127.0.0.1:5000` are different origins, even though both reach the same machine). By default, JavaScript on a page may **read** responses only from its own origin. Otherwise any page you visit could silently read your webmail or bank pages in other tabs.

A server can opt in to being read from other origins with a header:

```text
Access-Control-Allow-Origin: *          (any origin)   or   https://myapp.example   (one origin)
```

This is **CORS** (*Cross-Origin Resource Sharing*). In a test with a page on `127.0.0.1` fetching from `localhost`:

| Server response | `fetch` result in the page |
| --------------- | -------------------------- |
| no `Access-Control-Allow-Origin` header | `TypeError: Failed to fetch` |
| `Access-Control-Allow-Origin: *` | works, the JSON can be read |
| same origin (any headers) | works |

> [!WARNING]
> CORS is enforced **by the browser, to protect the user**, not by the server to protect itself. The request is still *sent* and the server still *runs* the handler; the browser only withholds the response from your script. `curl` ignores CORS entirely. So CORS can never replace authentication and validation on the server.

### Permissions

Browser APIs that touch the user's private world are **blocked until the user agrees**, per origin, through a prompt:

* location (`navigator.geolocation`), camera and microphone (`getUserMedia`), notifications, clipboard, and so on
* they work only in a **secure context**: pages served over **HTTPS** (or `localhost`/`127.0.0.1` for development). `window.isSecureContext` tells you.

In a test with no permission granted, the geolocation permission state was `"prompt"` and a request failed with error code 1 (*permission denied*); in a browser profile where the user had granted it, the same call returned the coordinates. This is the trade-off mentioned for "native-like" web apps: the more a page can do, the more a user's careless "Allow" can cost them.

## Threats and defences

### Third-party scripts and Subresource Integrity (SRI)

Pages often load libraries from a **CDN**. If that file is changed (the CDN is hacked, or a popular library publishes a bad version), **every site that includes it runs the attacker's code**: it could redirect all those users to hit one target server (a DoS), steal what they type, or mine cryptocurrency.

**Subresource Integrity** protects against this. You put the file's expected **hash** in the tag; the browser downloads the file, hashes it, and **refuses to run it if the hash differs**.

```html
<script src="https://cdn.example.com/lib.js"
        integrity="sha384-BASE64HASH"
        crossorigin="anonymous"></script>
```

Compute the value of `integrity` (replace the base64 text) with:

```bash
echo "sha384-$(openssl dgst -sha384 -binary lib.js | openssl base64 -A)"
```

In a test: with the correct hash the script ran; with the **same URL after the file was tampered with**, the browser **blocked** it (`onerror` fired and the console reported an integrity failure); with no `integrity` attribute the tampered script ran without complaint.

### Crypto-mining

JavaScript can perform arbitrary computation, and the user does not see it happen. A malicious or compromised page can run a **hidden miner** that spends your CPU/GPU on cryptocurrency puzzles and sends results to the attacker's server through asynchronous requests (`fetch`, WebSockets). Symptoms: fans spinning, battery draining, a slow device, a tab with high CPU in the browser's Task Manager. Defences: content/script blockers, a strict Content Security Policy, SRI for third-party code, and closing suspicious tabs.

### Denial of Service (DoS)

A **denial-of-service** attack makes a service unusable by overloading it. Two forms appear in a browser setting:

* **Against the client**: a script that hogs the CPU. JavaScript is single-threaded, so a tight loop freezes the page; in a test a 300 ms busy loop meant a 10 ms timer ticked **0 times**. A page like this can be hard to close and slow the whole device.
* **Against a server (distributed, DDoS)**: a script served to *many* users' browsers makes each of them send requests to one target. If 10,000 browsers each send one request per second, the target receives 10,000 requests per second; a server built for 100 per second is overwhelmed and legitimate users are refused. (The numbers are illustrative arithmetic.)

### Rate limiting

The main server-side defence is to **limit how fast any one client can send requests**, and answer excess requests with **`429 Too Many Requests`** (often with a `Retry-After` header).

```python
import time
from flask import Flask, jsonify, request

app = Flask(__name__)
WINDOW = 1.0      # seconds
LIMIT = 5         # allowed requests per client per window
counters = {}     # client address -> (window start, count)


@app.route("/api")
def api():
    ip = request.remote_addr
    now = time.time()
    start, count = counters.get(ip, (now, 0))
    if now - start >= WINDOW:                  # a new window begins
        start, count = now, 0
    count += 1
    counters[ip] = (start, count)
    if count > LIMIT:
        return jsonify(error="Too Many Requests"), 429, {"Retry-After": str(int(WINDOW))}
    return jsonify(ok=True)
```

In a test with 8 requests in quick succession the status codes were `200, 200, 200, 200, 200, 429, 429, 429`; after the window passed, requests were accepted again.

Limits of this simple version: counting per IP address punishes everyone behind a shared address (a campus or office), an attacker can use many addresses, and a counter in one process's memory is not shared between several workers (production systems keep counters in a shared store such as Redis, or use a library like Flask-Limiter, or a reverse proxy such as Nginx).

### CAPTCHA

**Problem**: scripts can send huge numbers of requests (booking tickets or appointment slots the moment they open, creating fake accounts), taking resources and slots from real people. Sites such as railway Tatkal booking and vaccine-appointment portals such as CoWin face exactly this.

**Solution**: make each request prove it came from a person.

1. The page embeds the CAPTCHA provider's widget; the user solves the challenge (or the provider decides from behaviour that no challenge is needed).
2. The **provider** gives the browser a signed **token**.
3. The browser sends the token with the form.
4. The **server verifies the token with the provider** (a server-to-server call) and rejects requests whose token is missing, invalid or already used.

The check must happen on the **server**: a client-side check alone would be bypassed like any client-side validation. CAPTCHA is not perfect (paid solving services exist), so it is combined with rate limiting.

## Summary

| Risk | What goes wrong | Defence |
| ---- | --------------- | ------- |
| Browser/engine bug | Page escapes the sandbox | Keep the browser updated; site isolation |
| Tampered third-party script | Everyone using the library runs attacker code | **SRI** hashes, trusted sources, fewer dependencies |
| Cross-site reading | One page reads another site's data | Same-origin policy; CORS only where needed |
| Powerful APIs | Location/camera misuse | Permission prompts, HTTPS-only |
| Crypto-mining | Your CPU does the attacker's work | Script blockers, CSP, SRI |
| Client DoS | Page freezes / device slows | Workers for heavy work; close the tab |
| Server DoS / bots | Server overwhelmed, slots grabbed | **Rate limiting**, CAPTCHA, CDN/caching |

More on web security (authentication, cookies, HTTPS, logging) is in [Week 9](../week9/9-week-index.md).

## Practice questions

<details>
<summary>1. Why can a WebAssembly module not read your files, even though it is "near native" code?</summary>

A module can only use its own memory and the functions that JavaScript passes in as imports. A module with no imports (like `add`) has no operations that reach files, the network or the DOM, and the browser sandbox blocks those APIs for page code anyway.
</details>

<details>
<summary>2. A page on <code>https://a.example</code> fetches JSON from <code>https://b.example</code> and gets <code>Failed to fetch</code>. What is the fix, and where is it made?</summary>

The two are different origins. The server **b.example** must send `Access-Control-Allow-Origin` (for `https://a.example` or `*`). Changing the page's JavaScript cannot fix it.
</details>

<details>
<summary>3. Does CORS stop an attacker from calling your API with <code>curl</code>?</summary>

No. CORS is enforced only by browsers, to protect users. The server still needs authentication, validation and rate limiting.
</details>

<details>
<summary>4. How does <code>integrity="sha384-..."</code> protect a site that loads a library from a CDN?</summary>

The browser hashes the downloaded file and compares it with the attribute. If the CDN's copy has been modified, the hashes differ and the browser refuses to run the script.
</details>

<details>
<summary>5. A ticket-booking API receives 10,000 requests per second from bots. Name two defences.</summary>

Rate limiting per client (responding `429`) and a CAPTCHA whose token the server verifies. Caching and a CDN for read-only pages also reduce load.
</details>
