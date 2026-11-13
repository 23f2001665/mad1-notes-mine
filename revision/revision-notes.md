# MAD 1: Revision Session (2 hours)

> [!NOTE]
> **This page is not part of the main notes.** It is a teach-and-drill plan for a **120-minute revision session** on 14 topics. Every topic has (1) the few ideas to *say*, (2) **real past-year questions (PYQs) to solve together**, and (3) a collapsed box with extra detail and traps. The PYQs come from four quiz papers; their answers were checked by **running the code** (see [`verify_revision_claims.py`](verify_revision_claims.py)). Links at the end of every topic lead to the **full notes**.

## How to run the session

| Min | # | Topic | PYQs solved in this block |
| --- | --- | --- | --- |
| 0-5 | | [What the exam asks](#what-the-four-papers-ask) | |
| 5-11 | 1 | [What is a web app](#1-what-is-a-web-app) (6) | M26 Q11, O25 Q12, M26 Q9 |
| 11-23 | 2 | [Latency and bandwidth](#2-latency-and-bandwidth-questions) (12) | M26 Q1, J26 Q5, J26 Q12, J25 Q11, J25 Q12 |
| 23-31 | 3, 5 | [IP, TCP, UDP](#3-ip-tcp-udp) and [IP addresses](#5-ip-addresses) (8) | quick checks |
| 31-38 | 4 | [Number systems](#4-number-system-conversion) (7) | J26 Q13, M26 Q10 |
| 38-45 | 6 | [HTML basics](#6-html-basics-p-h-a-img-link-table) (7) | J25 Q2, J26 Q2, O25 Q4, O25 Q13 |
| 45-59 | 7 | [CSS: specificity and box model](#7-css-selector-specificity-and-box-model) (14) | J26 Q1, J25 Q8, J25 Q4, M26 Q2, O25 Q10, M26 Q14, M26 Q15, J26 Q15 |
| 59-73 | 8 | [Jinja2](#8-jinja2-variable-for-if-filters) (14) | M26 Q5, M26 Q7, J26 Q14, J25 Q9, J26 Q16, O25 Q2, M26 Q13, J25 Q6, M26 Q6 |
| 73-82 | 9 | [`string.Template` and Jinja2 mixed questions](#9-stringtemplate-and-jinja2-mixed-questions) (9) | **J25 Q5**, O25 Q8, M26 Q16, J26 Q8 |
| 82-88 | 10 | [pyhtml and `sys.argv`](#10-pyhtml-basics-and-sysargv) (6) | O25 Q7, M26 Q12, O25 Q6, J25 Q10, J26 Q11, J25 Q13-15 |
| 88-100 | 11 | [Flask basics](#11-flask-basics-app-url_map-path-and-query-parameters) (12) | M26 Q3, M26 Q4, M26 Q8, J26 Q9, J26 Q10, O25 Q5, J26 Q7, J26 Q6, O25 Q9, O25 Q14-17 |
| 100-106 | 12 | [Forms: `request.form`](#12-forms-in-flask-requestform) (6) | J26 Q3-4, O25 Q11, J25 Q16-17 |
| 106-112 | 13 | [`url_for`, `redirect`, `render_template`, `abort`](#13-url_for-redirect-render_template-abort) (6) | J25 Q7, J25 Q3, M26 Q6 |
| 112-115 | 14 | [MVC](#14-overview-of-mvc) (3) | |
| 115-120 | | [Rapid-fire checklist](#rapid-fire-checklist) and questions | |

**Suggested rhythm for each block:** explain the idea in 2-3 minutes, then let the audience solve the PYQs before revealing the answer.

---

## What the four papers ask

| Code | Paper |
| --- | --- |
| **J25** | 13 Jul 2025 exam (QDD3) |
| **O25** | 26 Oct 2025 exam (QIM4) |
| **M26** | Modern Application Development I, 15 Mar 26 |
| **J26** | Modern Application Development I, 16 Jul 26 |

Each paper has 16-19 questions and 50 marks. Where the questions come from (counted by topic):

| Topic | Appears as | Where |
| --- | --- | --- |
| **Flask** (routes, converters, query strings, forms, methods, errors) | output / "will it error?" questions | all four papers, about a third of all questions |
| **Jinja2** (filters, loops, `set`, macros, with `sys.argv`) | "what is rendered?" | all four papers |
| **`string.Template`** (alone or mixed with Jinja2) | `KeyError` or not, output | all four papers |
| **CSS** (specificity, box width, `display`, flex) | rendered colours / sizes | all four papers |
| **Latency, bandwidth, bits** | numericals | M26, J26, J25 (none in O25) |
| **`sys.argv`** | output / which command | all four papers (often inside a Jinja2 or Flask question) |
| HTML (`dl`, block vs inline, `img` `alt`) | short MCQ | J25, J26, O25, M26 |
| Web app, URL parts, `curl -v` | concept MCQ | M26, O25 |
| pyhtml | matching question | O25 |
| IP / TCP / UDP, number systems, MVC | **not asked directly** in these four papers (only "bits needed" in J26) | still in the course, keep them short |

> [!TIP]
> Spend the time where the marks are: **Flask, Jinja2, `string.Template`, CSS and the numericals** (blocks 2, 7, 8, 9, 11 = 61 of the 120 minutes).

---

## 1. What is a web app

⏱ **6 min.** *Say:*

- An **app** is a program for a specific task. A **web app runs inside a browser**: the browser is the client (the user interface), the data and the heavy work are on a **server**.
- Three components in every app: **Storage, Compute, Presentation**. A web app typically has a **front end, a back end and a database**.
- **Client-server:** the client sends an HTTP *request* (GET / POST), the server returns an HTTP *response* (data + status). HTTP is **stateless**: the server remembers nothing unless cookies, sessions or tokens are used.

| | Desktop | Mobile | **Web app** |
| --- | --- | --- | --- |
| Runs | installed | installed, often talks to servers | **in a browser** |
| Data | mostly local | limited local | **mostly server-side** |
| Built with | OS SDK | Android / iOS SDK, Flutter | front end (*Vue*, *React*) + back end (*Flask*, *Django*) |

- **URL parts:** `http://localhost:5000/path?x=1`: *protocol* `http`, *host* `localhost`, *port* `5000`, *path* `/path`, *query string* `?x=1`.
- **`curl`:** `-i` includes the response headers, `-I` sends HEAD, **`-v` shows the request and the response with headers** (`>` request, `<` response).

**PYQ drill**

| | Question | Answer |
| --- | --- | --- |
| **M26 Q11** (MSQ) | True about web applications? A. all run entirely in the browser without a server; B. can use backend services through APIs; C. typically have front end, back end and database; D. cannot be accessed unless installed | **B, C** |
| **O25 Q12** (MSQ) | URL `http://localhost:5000/`: which is true? A. http is the protocol; B. 5000 is the port number; C. the trailing `/` represents the base URL (path); D. 5000 is the status code | **A, B, C** |
| **M26 Q9** | Which command shows detailed information about the HTTP request and response, including headers, to debug with curl? A. `curl -i <URL>`, B. `curl -v <URL>`, C. `curl --headers <URL>`, D. `curl -X GET <URL>` | **B** (`-v`) |

<details>
<summary>More detail and traps</summary>

- A web app is **not** installed on the user's device: that is the main difference from desktop and mobile apps. It does **not** run "entirely in the browser without a server" (M26 Q11 option A).
- **Distributed / peer-to-peer** is the other architecture: peers are equals, each is client and server (BitTorrent, blockchain, IPFS).
- Client and server can be on the **same machine** (a browser opening a Flask server on `localhost`).
- **SDK** = libraries/APIs + compiler/build tools + debugger + documentation + emulators.
- More `curl` and `python -m http.server` basics: [1-5 curl, http.server, nc](../week1/1-5-curl-http-server-netcat.md).

</details>

**Full notes:** [1-1 Intro to applications](../week1/1-1-intro-to-applications.md), [1-4 Types of architecture](../week1/1-4-types-architecture.md), [1-3 HTTP](../week1/1-3-network-history-TCP.md#hypertext-transfer-protocol-http), [curl in Week 5](../week5/5-curl-server.md#curl-commands).

---

## 2. Latency and bandwidth questions

⏱ **12 min** (the most predictable marks: every paper has one to three of these). *Say:*

| Quantity | Meaning | Formula |
| --- | --- | --- |
| **Latency** (one-way) | time to get from A to B | $t = \dfrac{\text{distance}}{\text{speed}}$ |
| **RTT** | there **and** back | $\text{RTT} = 2t$ |
| Max requests/s (each waits for the previous response) | | $\dfrac{1}{\text{RTT}}$ |
| **Bandwidth** | bits per second the link carries | $\text{requests/s} \times \text{size} \times 8$ (size in bytes) |
| Memory for $N$ users at once | | $N \times \text{buffer per user}$ |

- Speed in cable $\approx 2\times10^{8}$ m/s (vacuum $3\times10^{8}$). Rule of thumb: **5 ms per 1000 km**.
- Units: 1 byte = 8 bits; 1 KB = 1000 B; 1 MB = 1000 KB; **Gbps = 1000 Mbps** (the papers state "1KB = 1000 Bytes, 1MB = 1000KB").
- **Recipe:** (1) convert everything to SI units (m, s, bits), (2) apply the formula, (3) convert the answer to the unit asked (ms, MB, Mbps).

**PYQ drill**

| | Question | Working | Answer |
| --- | --- | --- | --- |
| **J26 Q12** | Client and data centre 12,500 km apart, TCP connection already open; RTT in ms (speed $2\times10^8$ m/s) | $\dfrac{12.5\times10^6}{2\times10^8} = 62.5$ ms one way; RTT = $2 \times 62.5$ | **125 ms** |
| **J26 Q5** | Server outgoing bandwidth 6 Gbps, each client needs 2 Mbps: maximum concurrent requests | $\dfrac{6000 \text{ Mbps}}{2 \text{ Mbps}}$ | **3000** |
| **J25 Q11** | 2 Gbps between client and server: maximum document size (MB) sent per second | $2000 \text{ Mbps} \div 8$ | **250 MB** |
| **J25 Q12** | Client 3000 km from the server. The request travels on cable, then the cable breaks and the response goes through air (speed $3\times10^8$ m/s), with an extra 47 ms at the server. Total wait? | request $\dfrac{3\times10^6}{2\times10^8} = 15$ ms; extra $47$ ms; response $\dfrac{3\times10^6}{3\times10^8} = 10$ ms | **72 ms** |
| **M26 Q1** | A train moves away from a tower (range 4.5 km, 5 Mbps) at 180 km/h, starting next to the tower. Data (MB) used before it leaves the coverage? | time $= \dfrac{4.5}{180}$ h $= 0.025$ h $= 90$ s; data $= 5 \times 90 = 450$ Mb; $450 \div 8$ | **56.25 MB** |

<details>
<summary>More worked problems and traps</summary>

| Problem (from the notes) | Answer |
| --- | --- |
| Chennai-Delhi 2000 km: one-way, RTT, requests/s | 10 ms, 20 ms, **50** |
| 1000 students × 2 requests/s × 18.2 KB | 36.4 MB/s = **291.2 Mbps** |
| 50,000 viewers × 4 MB buffer | **200 GB** |

- **RTT is twice the one-way latency**; requests/s use the RTT.
- Bandwidth is in **bits** (Mbps), sizes in **bytes** (MB): multiply by 8.
- Latency limits requests/s only for requests sent **one after another**. More bandwidth does not shorten the round trips of DNS, TCP and TLS, so it barely speeds up small pages.
- If "the TCP connection is already established", do **not** add handshake round trips (J26 Q12).

</details>

**Full notes:** [1-2 Latency and bandwidth](../week1/1-2-latency-bandwidth.md), [units in Week 0](../week0/0-metrics.md).

---

## 3. IP, TCP, UDP

⏱ **5 min** (with section 5: 8 min). No PYQ in these four papers, so keep it to the table. *Say:*

| Layer | Protocol | Question it answers |
| --- | --- | --- |
| Application | **HTTP** (SMTP, SSH, SFTP) | *what* does the data mean? |
| Transport | **TCP** (reliable) or **UDP** (fast) | *how* does it arrive? |
| Network | **IP** | *where* does it go? |

| | **TCP** | **UDP** |
| --- | --- | --- |
| Connection | connection-oriented, **three-way handshake** (SYN, SYN-ACK, ACK) | connectionless |
| Delivery | **guaranteed**: ACKs, retransmission | **no guarantee** |
| Order | packets reassembled in **order** | not guaranteed |
| Speed | slower (accuracy over speed) | faster (speed over reliability) |
| Controls | flow control and congestion control | none |

- **IP** addresses devices and **routes** packets hop by hop; it does **not** guarantee delivery or order, TCP adds that.
- **Ports:** 16-bit, so $2^{16} = 65{,}536$ values, **0 to 65,535**. IP = which machine, port = which service. **80** HTTP, **443** HTTPS, **25** SMTP. Port 0: "OS, pick a free one".
- **Checksum** (16 bits): the receiver recomputes it; on mismatch the packet is dropped and the sender retransmits. It catches **accidents**, not attackers.
- **Loopback** `127.0.0.1` (the whole `127.0.0.0/8`): the traffic never leaves the machine. **`0.0.0.0`** as a bind address = all interfaces.

<details>
<summary>What happens when you open https://example.com (in order)</summary>

1. **DHCP** gave the device its IP, gateway and DNS server (once)
2. **DNS** turns the name into an IP address
3. **TCP** connects to port 443 (three-way handshake)
4. **TLS** handshake (HTTPS only)
5. the browser sends the **HTTPS request**; TCP segments it, IP routes the packets
6. the receiver reorders, checks checksums and acknowledges; the server answers with a status code and content

**Traps:** TCP adds reliability **on top of** unreliable IP; the largest port is **65,535**, not 65,536.

</details>

**Full notes:** [1-3 TCP](../week1/1-3-network-history-TCP.md#transmission-control-protocol), [Ports](../week1/1-3-network-history-TCP.md#ports), [IP](../week1/1-3-network-history-TCP.md#internet-protocol), and the *TCP, UDP, Proxy...* box at the end of that page for UDP.

---

## 4. Number system conversion

⏱ **7 min.** *Say:*

| System | Base | Digits | Bits per digit |
| --- | --- | --- | --- |
| Binary | 2 | 0 1 | 1 |
| Octal | 8 | 0-7 | **3** |
| Decimal | 10 | 0-9 | |
| Hexadecimal | 16 | 0-9, A-F (`A`=10 ... `F`=15) | **4** |

- $n$ bits give $2^n$ values, from $0$ to $2^n - 1$.
- **Any base → decimal:** digit × base$^{\text{position}}$, position 0 on the right, add.
- **Decimal → other base:** divide by the base repeatedly, read the **remainders bottom to top**.
- **Binary ↔ octal / hex:** **group** bits (3 or 4) **from the right**, convert each group. No division.
- **Fraction → binary:** multiply by 2, note the integer part, read **top to bottom**.

| Question | Working | Answer |
| --- | --- | --- |
| $110101_2 \to$ decimal | $32+16+4+1$ | $53$ |
| $45_{10} \to$ binary | $45 \div 2$: remainders read upwards | $101101_2$ |
| $11101101_2 \to$ hex | $1110\;1101$ = E D | $ED_{16}$ |
| $254_{10} \to$ hex | $254 = 15 \cdot 16 + 14$ | $FE_{16}$ |
| $10111101_2 \to$ octal | $010\;111\;101$ | $275_8$ |
| $624_8 \to$ decimal | $6\cdot64 + 2\cdot8 + 4$ | $404$ |
| $9B_{16} \to$ decimal | $9\cdot16 + 11$ | $155$ |
| $3F_{16} \to$ binary | $0011\;1111$ | $111111_2$ |
| $0.625_{10} \to$ binary | $\times2$: 1.25 (1), 0.5 (0), 1.0 (1) | $0.101_2$ |

> [!TIP]
> Check in Python: `bin(45)`, `oct(254)`, `hex(254)`, `int('101101', 2)`, `int('FE', 16)`.

**PYQ drill**

| | Question | Answer |
| --- | --- | --- |
| **J26 Q13** | A document has only lower-case letters (all 26 occur). Same code length for every letter. Minimum bits per character? | **5** ($2^4 = 16 < 26 \le 32 = 2^5$) |
| **M26 Q10** (MSQ) | True? A. UTF-8 is variable-length and can represent all Unicode characters; B. HTML attribute names are case-insensitive; C. inline CSS is preferred over external CSS for large projects; D. UTF-32 is fixed-length, 4 bytes per character | **A, B, D** (C is false) |

<details>
<summary>Traps</summary>

- Remainders **bottom to top**; fraction digits **top to bottom**.
- Group from the **right** (`10111101` → `010 111 101`).
- 8 bits give 256 values, but the largest is 255.
- ASCII / Unicode / UTF-8: [2-1 ASCII and Unicode](../week2/2-1-ascii-unicode.md).

</details>

**Full notes:** [2-2 Number systems](../week2/2-2-number-systems.md).

---

## 5. IP addresses

⏱ **3 min** (inside the 8-minute block with section 3). *Say:*

| | **IPv4** | **IPv6** |
| --- | --- | --- |
| Size | **32 bits** = 4 bytes | **128 bits** = 16 bytes |
| Written as | 4 numbers 0-255 with dots: `192.168.1.1` | 8 groups of 16 bits (4 hex digits) with colons |
| Count | $2^{32} = 4{,}294{,}967{,}296$ | $2^{128}$ |

- Each IPv4 number is one **byte**: range 0-255. DHCP hands addresses out (for a lease period); DNS maps names to addresses. Private ranges such as `192.168.x.x` repeat in many home networks.

| Dotted decimal | Binary (per byte) | Hex |
| --- | --- | --- |
| `192.168.1.1` | `11000000.10101000.00000001.00000001` | `C0.A8.01.01` |
| `172.16.10.25` | `10101100.00010000.00001010.00011001` | `AC.10.0A.19` |

The notes' MCQ: `172.16.10.25` in the question's 4-group format is `0000:0000:AC10:0A19`. A real IPv6 address has **eight** groups; an IPv4 address is written `::ffff:ac10:0a19` (or `::ffff:172.16.10.25`).

<details>
<summary>Quick checks (not PYQs)</summary>

- How many bits is an IPv4 address? **32.** IPv6? **128.**
- Largest value of one IPv4 number? **255** (8 bits).
- What does `0.0.0.0` mean when a server binds to it? **All network interfaces.**
- Is the port part of the IP address? **No**: IP = machine, port = service.

</details>

**Full notes:** [1-3 IP address](../week1/1-3-network-history-TCP.md#ip-address).

---

## 6. HTML basics: p, h, a, img, link, table

⏱ **7 min.** *Say:* skeleton `<!DOCTYPE html>` → `<html lang>` → `<head>` (`<meta charset>`, `<title>`, `<link>`) → `<body>`.

| Tag | Purpose | Key attributes | Kind |
| --- | --- | --- | --- |
| `<h1>`...`<h6>`, `<p>` | headings (`h1` most important), paragraph | | block |
| `<a>` | hyperlink | **`href`**, `target="_blank"`, `title`; `href="#id"` jumps to an element with that `id` | inline |
| `<img>` | image | **`src`**, **`alt`** (text if it cannot load), `width`, `height` | inline, **void** |
| `<link>` | external resource, usually `<link rel="stylesheet" href="style.css">` | `rel`, `href` | in `<head>`, **void** |
| `<table>`, `<tr>`, `<th>`, `<td>` | table, row, header cell, data cell | **`colspan`**, **`rowspan`** | |
| `<dl>`, `<dt>`, `<dd>` | description list: term and its description | | `dd` is indented by default |

- **Void** elements have no closing tag: `img`, `br`, `hr`, `input`, `link`, `meta`. HTML has no "self-closing" tags (`<div />` does not close the `div`).
- **Block** (`div`, `h1`-`h6`, `p`, `form`, `ul`, `li`): new line, full width. **Inline** (`span`, `a`, `strong`, `em`): same line, only as wide as the content; `width`/`height` do not apply (but they do for `img`).

```html
<table>
  <tr><th>Name</th><th colspan="2">Marks</th></tr>
  <tr><td rowspan="2">Asha</td><td>Maths</td><td>80</td></tr>
  <tr><td>Physics</td><td>90</td></tr>
</table>
```

3 columns: row 1 is `Name` + a header spanning two columns; `Asha` spans two rows, so row 3 starts with `Physics` in column 2.

**PYQ drill**

| | Question | Answer |
| --- | --- | --- |
| **J25 Q2** | Output of `<dl><dt>Flask</dt><dd>A Python web framework.</dd><dt>SQLAlchemy</dt><dd>A database toolkit for Python.</dd></dl>` | each term on its own line, its description on the next line **indented** (browser default `dd` margin) |
| **J26 Q2** | One block-level and one inline element: A. block `<span>`, inline `<div>`; B. block `<div>`, inline `<a>`; C. block `<h1>`, inline `<p>`; D. block `<span>`, inline `<h5>` | **B** |
| **O25 Q4** | S1: `<span>` starts on new lines, `<div>` is inline. S2: `<p>` and `<div>` start on new lines and fill the width, `<span>`, `<strong>`, `<em>` flow inline | **S2 correct, S1 incorrect** |
| **O25 Q13** (MSQ) | `<img src="logo.png" alt="Company Logo" />`: A. if it fails to load the text "Company Logo" is shown; B. a missing file shows a broken image; C. `alt` is mandatory in HTML5; D. only jpeg/jpg allowed | **A, B** |

<details>
<summary>More detail and traps</summary>

- `href` is the destination of a link, `id` only names an element; `id` is unique, `class` groups.
- `border`, `bgcolor`, `cellpadding` on `<table>` are **deprecated**: use CSS.
- `<link>` goes in `<head>` and has no closing tag.
- O25 Q13 C: the exam key treats "alt is mandatory" as **false** (a missing `alt` does not stop the image from loading), although validators still ask for it. `png` is fine (D is false).
- HTML attribute names are case-insensitive (M26 Q10).

</details>

**Full notes:** [2-3 HTML basics](../week2/2-3-html-basics.md) ([block vs inline](../week2/2-3-html-basics.md#block-level-vs-inline-elements)), [2-4 Elements](../week2/2-4-html-elements.md) ([lists](../week2/2-4-html-elements.md#lists), [links](../week2/2-4-html-elements.md#links), [images](../week2/2-4-html-elements.md#images)), [2-5 Tables](../week2/2-5-html-tables.md), [`<link>`](../week2/2-6-css-selector-specificity.md#how-to-add-css).

---

## 7. CSS: selector specificity and box model

⏱ **14 min.** *Say:*

**Adding CSS:** external `<link rel="stylesheet" href="style.css">`, internal `<style>` in `<head>`, inline `style="..."`. With the **same specificity the later rule wins**.

**Specificity** is three counters compared left to right, **not** one number:

`!important` > inline > **(IDs, classes + attributes + pseudo-classes, elements)**

| Selector | (IDs, classes, elements) |
| --- | --- |
| `*` | (0, 0, 0) |
| `p` | (0, 0, 1) |
| `div p` | (0, 0, 2) |
| `.note`, `[type="text"]`, `:first-child` | (0, 1, 0) |
| `p.note`, `p:first-child` | (0, 1, 1) |
| `.container p.highlight` | (0, 2, 1) |
| `#main` | (1, 0, 0) |

A single `#id` beats any number of classes; a class beats any number of element names; combinators and `*` add nothing.

**Box model:** content → padding → border → margin. By default (**`content-box`**) `width` is the **content** only:

$$\text{visible width} = \text{width} + \text{padding}_{L+R} + \text{border}_{L+R} \qquad (\text{margin excluded})$$

With `box-sizing: border-box` the `width` already includes padding and border. **Vertical margins of neighbours collapse** to the larger one (20px above 30px gives a 30px gap). `margin: 0 auto` centres a block that has a width.

**`display`:** `block` takes the full width, starts a new line; `inline` flows in the text and **ignores `width`/`height`**; `inline-block` flows in the line **and** accepts width, height, padding, margin; `none` removes the element from the layout. `flex` lays the children in a **row**; the items **shrink** to fit the container.

**PYQ drill: specificity**

| | Question | Answer |
| --- | --- | --- |
| **J26 Q1** | `div{color:green} .cdiv{color:red} #div1{color:blue}` on `<div id="div1" class="cdiv">` | **blue** (ID) |
| **J25 Q8** | `p{color:blue} #highlight{color:green} .important{color:red}` on `<p class="important" id="highlight">` | **green** (ID) |
| **J25 Q4** | Rules `.container p.highlight {red}`, `.content .special {blue}`, `span.highlight {green}`. Which elements get a red background? | **every `<p class="highlight">` that is a descendant of `.container`**, also the one with `highlight special` ((0,2,1) beats (0,2,0)); the `<span>` is green; a `p.highlight` outside `.container` has no background |
| **M26 Q2** | `p{background:yellow; display:inline-block} div p{background:lightblue} .highlight{background:pink} #special{background:orange}` with three `<p>` in a `div`: first `class="highlight"`, second `class="highlight" id="special"`, third plain | **one line**: pink, orange, lightblue (`inline-block` keeps the paragraphs side by side; class beats `div p`, ID beats class, `div p` beats `p`) |

**PYQ drill: box model and display**

| | Question | Answer |
| --- | --- | --- |
| **O25 Q10** | `div{width:0px;margin:0px} .container{width:200px;padding:15px;border:5px solid black} #box{margin:10px}` on `<div class="container" id="box">`: total width including content, padding and border, **excluding margin**? | **240 px** (the class beats `div` for `width`: $200 + 2\cdot15 + 2\cdot5$) |
| **M26 Q14** (MSQ) | `#container{width:200px;padding:10px;border:2px solid black;margin:15px}`: which are true? A. total width with padding and border is 224px; B. the margin affects the content-box width; C. padding adds internal spacing; D. the border adds to the total width in the standard box model | **A, C, D** ($200+20+4 = 224$) |
| **M26 Q15** (MSQ) | A. `block` always starts on a new line and takes the full width; B. `inline` elements can use `height` and `width`; C. `inline-block` can sit inline and use `height` and `width`; D. `inline` elements cannot use `height` and `width` | **A, C, D** |
| **J26 Q15** | `.container{display:flex; width:250px; border:2px solid black}` with three `.box{width:80px; height:40px; border:1px solid blue; margin:5px}`. Which picture? | **three separate boxes in one row, all inside the container, with small gaps**: $3 \times (80+2+10) = 276 > 250$, so the items **shrink** (each border box is about 73 px) instead of overflowing |

<details>
<summary>More detail and traps</summary>

- Specificity cases of the notes: equal specificity → later wins; `!important` beats everything normal; two `!important` rules are decided by specificity, then order.
- Shorthand order for `margin` / `padding` is **top right bottom left**; 2 values = vertical horizontal.
- `border-width` without `border-style` shows **no border**. Outline and `box-shadow` take **no space**.
- `width: 100%` plus padding and border overflows its parent with `content-box`.
- Percentage `padding` and `margin` are relative to the parent's **width**.
- Flexbox is only introduced in the notes' `display` list; the shrinking behaviour above is what J26 Q15 tests.

</details>

**Full notes:** [2-6 CSS selectors and specificity](../week2/2-6-css-selector-specificity.md) ([adding CSS](../week2/2-6-css-selector-specificity.md#how-to-add-css), [specificity](../week2/2-6-css-selector-specificity.md#css-specificity), [`display`](../week2/2-6-css-selector-specificity.md#css-display-property), [combinators](../week2/2-6-css-selector-specificity.md#css-combinators)), [2-8 Box model](../week2/2-8-css-box-model.md) ([sizes](../week2/2-8-css-box-model.md#2-width-and-height-are-the-size-of-the-content), [margin collapsing](../week2/2-8-css-box-model.md#margin-collapsing), [`box-sizing`](../week2/2-8-css-box-model.md#7-box-sizing-what-do-width-and-height-mean)).

---

## 8. Jinja2: variable, for, if, filters

⏱ **14 min.** *Say:* `{{ expr }}` prints, `{% stmt %}` runs a statement (`if`, `for`, `set`, `macro`), `{# #}` is a comment. `Template(text).render(name=value)` fills it.

- **Variables:** `{{ user.name }}`, `{{ user['name'] }}`, `{{ items[0] }}`; arithmetic `{{ 7 // 2 }}` → `3`, `{{ 7 / 2 }}` → `3.5`; `~` joins strings (`{{ 'a' ~ 1 }}` → `a1`).
- A **missing variable prints nothing**; but an attribute of a missing variable (`{{ user.name }}` with no `user`) raises `UndefinedError`. Extra `render()` arguments are ignored. An HTML comment `<!-- {{ 1+1 }} -->` is **still evaluated**; a Jinja comment is not output.
- **`if`:** `{% if a %}...{% elif b %}...{% else %}...{% endif %}`; `==` compares the **whole** value (`"admin iitm" == "admin"` is false).
- **`for`:** `{% for x in items %}...{% endfor %}`; dictionaries: `{% for k, v in d.items() %}`; **no `while`**. Loop variables: `loop.index` (1-based), `loop.index0`, `loop.revindex`, `loop.first`, `loop.last`, `loop.length`.
- **`set`:** `{% set total = a + b %}` creates a variable from the `set` line on. A `set` inside `for` does not leak out; `if` opens no scope.
- **Filters** (`value | filter`, chainable):

| Filter | Example | Result |
| --- | --- | --- |
| `upper`, `lower`, `title` | `"aLice bob"` | `ALICE BOB`, `alice bob`, `Alice Bob` |
| `length` | `"aLice bob"`, `[1,2,3]` | `9`, `3` |
| `join(sep)` | `[1,2,3]\|join('-')` | `1-2-3` |
| `replace(a, b)` | `"aLice bob"\|replace('a','4')` | `4Lice bob` |
| `default(v)` | missing variable | `v` (but `0` and `""` are kept; `default(v, true)` replaces them too) |
| `sum`, `max`, `first`, `last` | `[1,2,3]\|sum` | `6` |
| **`sort`** | `[5,2,8,1,9]\|sort` | `[1, 2, 5, 8, 9]` (ascending) |
| **`sort(reverse=True)`** | `[6,8,5,2,4]` | `8, 6, 5, 4, 2` |
| **`reject("even")`** | `[10,3,9,8,15]` | `3, 9, 15` (drops the even numbers; `select("even")` keeps them) |
| `groupby('c')` | list of dicts | groups sorted by the key |
| `e` / `safe` | | escape HTML / mark as safe |

> [!NOTE]
> `sort`, `sort(reverse=True)`, `reject("even")`, `sum` and `select` are used in the PYQs and are standard Jinja2 filters, but they are **not** in the main notes. The notes list `upper`, `lower`, `title`, `length`, `default`, `join`, `replace`, `groupby`.

**PYQ drill**

| | Question | Answer |
| --- | --- | --- |
| **O25 Q2** | Syntax to display the number of courses: A. `{{ courses \| len }}`; B. `{{ courses \| length }}`; C. `{{ len(courses) }}`; D. none | **B** (`len` is not a filter and not available as a function) |
| **M26 Q5** | `{% for num in seq \| reject("even") -%}` `{{ num + 2 }}` `{%- endfor %}` with `seq=[10, 3, 9, 8, 15]` | **`51117`** (3→5, 9→11, 15→17; the dashes remove the whitespace between them) |
| **M26 Q7** | `{% set numbers = [5, 2, 8, 1, 9] %}{% for num in numbers\|sort -%}<p>{{ num }}</p>{%- endfor %}` | **`<p>1</p><p>2</p><p>5</p><p>8</p><p>9</p>`** |
| **J26 Q14** | list `[6, 8, 5, 2, 4]` must show 8, 6, 5, 4, 2: A. `{%for item in sl\|sort(reverse=True)%}`; B. `in sl`; C. `in sl\|sort`; D. `in sl.sort()` | **A** (`sl.sort()` returns `None`, so the loop fails with `TypeError`) |
| **J25 Q9** | list `[5, 4, 3, 2, 1]` must show 1, 2, 3, 4, 5 | **`{%for item in sl\|sort%}`** |
| **J26 Q16** | For each student `{% set avg = (student.marks \| sum) / (student.marks \| length) %}`; `avg > 75` Distinction, `avg > 50` Pass, else Fail. Alice [80, 90], Bob [50, 40], Kittu [53, 66], Carol [100]. Who is "Pass"? | **Kittu** (59.5); Alice 85 and Carol 100 are Distinction, Bob 45 is Fail |
| **M26 Q6** | `{% if user == "admin" %}Welcome Admin{% else %}Welcome User{% endif %}`, rendered with `user="admin iitm"` | **Welcome User** |
| **M26 Q13** (MSQ) | `users` = list of dicts `id`, `name`, `role`. An `<ol>` with a link `/show_users/<id>` for each. Which are correct? A. `{{user.id}}`, `{{user.name}}` in a loop; B. `{{user['id']}}`, `{{user['name']}}` in a loop; C. the three items written out with `{{users[0].id}}`...; D. loop with `{{user.name[-1]}}` | **all four** (A and B are the usual styles; D works here because the names end with the id: `user_1`...) |
| **J25 Q6** | `{% macro greet(name) %}Hello, {{ name }}!{% endmacro %}` then `{{ greet("Alice") }}` and `{{ greet("Bob") }}` rendered in Flask | the browser shows **Hello, Alice! Hello, Bob!** (a macro is a reusable function-like block; the line breaks collapse to spaces) |

<details>
<summary>More detail and traps</summary>

- Plain `Template` does **not** escape HTML; Flask turns autoescaping on for `.html` templates. `|safe` only for trusted text.
- `{%-` and `-%}` strip the whitespace before / after a tag.
- `break` / `continue` are not available in a loop without an extension.
- Never render **template text written by a user**; pass user input only as data.

</details>

**Full notes:** [3-4 Jinja2](../week3/3-4-jinja2.md): [syntax](../week3/3-4-jinja2.md#template-syntax-overview), [variables](../week3/3-4-jinja2.md#variable-printing-or-interpolation), [control structures](../week3/3-4-jinja2.md#control-structures), [for loops](../week3/3-4-jinja2.md#for-loops), [loop variables](../week3/3-4-jinja2.md#special-loop-vars), [filters](../week3/3-4-jinja2.md#filters), [autoescaping](../week3/3-4-jinja2.md#autoescaping-html-safety).

---

## 9. `string.Template` and Jinja2 mixed questions

⏱ **9 min.** The classic exam trick: **each engine ignores the other's syntax**, and a template is filled in **one pass only**.

| | `string.Template` | `jinja2.Template` |
| --- | --- | --- |
| Placeholder | `$name`, `${name}`, `$$` = literal `$` | `{{ name }}` |
| Fill with | `.substitute(...)` / `.safe_substitute(...)` | `.render(...)` (a dict or keyword arguments) |
| Missing value | `substitute` → **`KeyError`**; `safe_substitute` leaves the placeholder | prints **nothing** |
| Logic, filters | none | yes |
| `.2f`-style formatting | not possible (`${price:.2f}` is invalid) | `{{ '%.2f'\|format(price) }}`, `{{ price\|round(2) }}` |
| Attribute access | none: `$user.name` only replaces `$user` | `{{ user.name }}` |

```python
from string import Template
from jinja2 import Template as JT

print(Template("{{ name }} $name").safe_substitute(name="Z"))   # {{ name }} Z
print(JT("{{ name }} $name").render(name="Z"))                   # Z $name
```

**PYQ drill**

**J25 Q5** (this is the "question 5" mix question): which statement raises a `KeyError`?

```python
from string import Template as string_template
from jinja2 import Template as jinja_template

template1 = string_template('Hello $name, welcome to $city!')
template2 = jinja_template('{{product}} costs {{price}}')
```

| Option | Result |
| --- | --- |
| A. `template1.substitute(name='Alice')` | **`KeyError: 'city'`** ← the answer |
| B. `template1.substitute(name='Alice', city='Boston', state='Massachusetts')` | `Hello Alice, welcome to Boston!` (the extra `state` is ignored) |
| C. `template2.render({"product": "laptop"})` | `laptop costs ` (missing `price` prints nothing) |
| D. `template2.render({"product": "laptop", "price": "45000", "currency": "rupees"})` | `laptop costs 45000` |

**O25 Q8** (MSQ): what do the two prints show?

```python
from jinja2 import Template as JTemplate
from string import Template as STemplate

data = {'name1': 'Alice', 'name2': 'name1', 'age1': '25', 'age2': 'age1', 'job1': 'Engineer', 'job2': 'job1'}
jt = JTemplate("{{name2}} is {{age2}} years old and works as a {{job2}}.")
result1 = jt.render(data)
print(result1)            # first print
st = STemplate(result1)
result2 = st.substitute(data)
print(result2)            # second print
```

- Jinja2 inserts the **value** of `name2`, which is the *text* `name1` (it does not look `name1` up again): `name1 is age1 years old and works as a job1.`
- `STemplate(result1)` contains **no `$`**, so `substitute` has nothing to replace and returns the same sentence: no `KeyError`, **no** "Alice is 25...".
- Correct: **A** (first print), **C** (Jinja2 uses `{{ }}`), **D** (`string.Template` uses `$`). Wrong: B, E.

**M26 Q16** (MSQ): `template = Template("Hello $name, you have $count messages")`. Which calls do **not** raise `KeyError`?

| Call | Result |
| --- | --- |
| A. `substitute({"name": "Alice"})` | `KeyError: 'count'` |
| B. `safe_substitute({"name": "Alice"})` | `Hello Alice, you have $count messages` ✓ |
| C. `substitute({"name": "Alice", "count": 5})` | `Hello Alice, you have 5 messages` ✓ |
| D. `safe_substitute({"name": "Alice", "count": 5})` | `Hello Alice, you have 5 messages` ✓ |

**J26 Q8:** `for name in ["Siya", "Sunita"]:` a new `Template("Student Name: $name ")` is built each time and `print(template.substitute(name=name))` runs. Output: **`Student Name: Siya`** and **`Student Name: Sunita`** on two lines (the trailing space of the template is part of each line); no `KeyError`.

<details>
<summary>More examples and traps</summary>

| Statement | Result |
| --- | --- |
| `Template("Hi $name, you owe $$${amount}").substitute(name="Ann", amount=5)` | `Hi Ann, you owe $5` |
| `Template("${w}s and $ws").safe_substitute(w="cat")` | `cats and $ws` |
| `Template("$user.name").substitute(user={"name": "A"})` | `{'name': 'A'}.name` |
| `Template("cost $ 5").substitute()` | `ValueError` (invalid placeholder) |
| `Template("$x").substitute({"x": 1}, x=2)` | `2` (keywords override the mapping) |
| `JT("{{ user.name }}").render()` | `UndefinedError` |

- `${name}s` is needed to put letters right after a placeholder; `$names` looks for `names`.
- Say which one the question asks about: `substitute` fails loudly, `safe_substitute` silently, Jinja2 prints nothing.

</details>

**Full notes:** [3-3 `string.Template`](../week3/3-3-string-templating.md) ([placeholder syntax](../week3/3-3-string-templating.md#placeholder-syntax), [`substitute` vs `safe_substitute`](../week3/3-3-string-templating.md#substitute-vs-safe_substitute)), [comparison tables](../week3/3-4-jinja2.md#comparison-tables), [3-2 String formatting](../week3/3-2-string-formatting.md).

---

## 10. pyhtml basics and `sys.argv`

⏱ **6 min.** *Say:* **pyhtml** builds HTML from Python function calls; **`sys.argv`** is the list of command-line arguments.

```python
from pyhtml import html, head, title, body, h1, p, ul, li, a
doc = html(head(title("T")), body(h1("Hi"), ul(li("a"), li("b"))))
print(a(href="https://e.com", id_="l")("link"))
```

```html
<a href="https://e.com" id="l">
  link
</a>
```

- One function per tag; **children are the arguments**. Attributes go in a **first call**, children in a **second**: `tag(attributes)(children)`. A tag takes children or attributes in one call, not both (`AssertionError`).
- `class` is a Python keyword → **`class_`**; a trailing `_` is dropped; other underscores become hyphens (`data_value` → `data-value`). Text is **escaped** (`_safe=True` turns that off). `html(...)` adds `<!DOCTYPE html>`. Install: `pip install pyhtml`.
- **`sys.argv`:** `python main.py a b` → `sys.argv == ['main.py', 'a', 'b']`. `sys.argv[0]` is the **script name**; **every item is a string** (convert with `int()`); the **shell** splits the arguments, quotes keep spaces together; `sys.argv[1:]` skips the script name.

**PYQ drill**

| | Question | Answer |
| --- | --- | --- |
| **O25 Q7** | Match: 1 PyHTML, 2 Jinja2, 3 Template Rendering, 4 String Template Rendering with A. lightweight engine with `$variable`, B. library that builds HTML from Python functions, C. generating dynamic HTML by combining templates with data, D. engine used by Flask with control structures, filters, inheritance | **1→B, 2→D, 3→C, 4→A** |
| **M26 Q12** (MSQ) | `sys.argv`: A. a list of command-line arguments; B. `sys.argv[0]` stores the script name; C. elements are always integers; D. elements are always strings | **A, B, D** |
| **O25 Q6** | `main.py` does `import sys`, `import utils`, then `print('Processing: ' + sys.argv[2])`; `utils.py` does `import sys` and `print('Module: ' + sys.argv[0])`. Run `python main.py data.txt output.txt` | **`Module: main.py`** then **`Processing: output.txt`** (importing `utils` runs it first; `argv[0]` is `main.py`) |
| **J25 Q10** | `process(v)` must return `",".join(v)` and be called as `process(v[1:])` where `v = sys.argv`; run `python main.py 1 2 3 4 5` | prints **`1,2,3,4,5`** (without the script name) |
| **J26 Q11** (MSQ) | `course = sys.argv[1:]`; the template prints `course[0]` to `course[3]` as `MAD1 => MAD2 => MAD1_Project => MAD2_Project`. Which commands? | **`python main.py MAD1 MAD2 MAD1_Project MAD2_Project`** and the version with quotes around `"MAD1_Project" "MAD2_Project"` (the shell removes the quotes). One big quoted string would be a single argument; `MAD1_ Project` is two |
| **J25 Q13-15** | `webapp.py` with `frameworks = {django: python, react: javascript, flask: python, vue: javascript}` and `languages = {python: server-side, javascript: client-side}`; the template is `{{ framework }} is a {{ lang_type }} {{ language }} framework.`; needs `args[1]` a framework and `args[2] == 'type'` | `python webapp.py flask type` (with or without a 4th word) prints **`flask is a server-side python framework.`**; `python webapp.py react type` prints **`react is a client-side javascript framework.`**; `python webapp.py django python` prints **`Invalid second argument or language not found!`** |
| **J26 Q6** | `MULTIPLIER = int(sys.argv[1]) if len(sys.argv) > 1 else 2`; route `/calculate/<int:value>` returns `f"Result: {value * MULTIPLIER}"`. Run `python app.py 7`, open `/calculate/6` | **`Result: 42`** |

| | pyhtml | Jinja2 |
| --- | --- | --- |
| Syntax | Python function calls | template delimiters |
| Use | simple HTML generation | templates with logic, used by Flask |
| Escaping | always on | off in a plain `Template`, on in Flask for `.html` |

**Full notes:** [3-1 pyhtml and sys](../week3/3-1-pyhtml-sys.md) ([`sys.argv`](../week3/3-1-pyhtml-sys.md#sysargv), [pyhtml](../week3/3-1-pyhtml-sys.md#pyhtml-library), [attributes](../week3/3-1-pyhtml-sys.md#attribute-handling-in-pyhtml)), [0-sys](../week0/0-sys.md).

---

## 11. Flask basics: app, url_map, path and query parameters

⏱ **12 min.** *Say:*

```python
from flask import Flask, request

app = Flask(__name__)                 # create the app

@app.route("/")                       # URL pattern -> view function
def home():
    return "Hello, Flask!"

if __name__ == "__main__":
    app.run(debug=True)               # default http://127.0.0.1:5000, port=... changes it
```

- A view must return a **string, dict/list (→ JSON), a tuple `(body, status)` or a `Response`**; an `int` gives **500**.
- **Path parameter** (in the route): `/user/<username>`, converters `string` (default), `int`, `float`, `path`, `uuid`. A value that does not fit gives **404**. **Query parameter** (after `?`, **not** in the route): `request.args.get("q")`; `request.args.get` returns a **string** (the default is used only if the key is absent).
- `app.url_map` / `flask routes` list the rules. A route `/about/` also answers `/about` (308 redirect); a route `/contact` does **not** answer `/contact/` (404).

| Route | URL | Result |
| --- | --- | --- |
| `/user/<username>` | `/user/john/doe` | **404** (a string stops at `/`) |
| `/post/<int:post_id>` | `/post/12` / `/post/abc`, `/post/1.5`, `/post/-3` | `12` as an `int` / **404** |
| `/price/<float:price>` | `/price/19.99` / `/price/19` | ok / **404** (needs a decimal point) |
| `/files/<path:sub>` | `/files/a/b/c.txt` | `sub = 'a/b/c.txt'` |

**PYQ drill: routes and query strings**

| | Question | Answer |
| --- | --- | --- |
| **M26 Q4** and **O25 Q3** | `app.run(port=0007)` (M26) and `app.run(port=5008)` (O25): on which URL does it run? | M26: **none of these**, `0007` is a **`SyntaxError`** in Python 3 (leading zeros) so it never starts. O25: **`http://localhost:5008/`**. Default is `http://127.0.0.1:5000/`, and `http`, not `https` |
| **M26 Q8** | Routes `/profile/<string:username>` and `/post/<int:post_id>`; open `/post/abc123` | **404** (`abc123` is not an int) |
| **J26 Q9** | Routes `/user/<name>` and `/user/admin`; open `/user/admin` | **`Admin Panel`**: Flask prefers the **more specific (fixed text) rule** (`/user/bob` gives `User: bob`) |
| **J26 Q10** (MSQ) | `/calculate/<int:v1>/<int:v2>` returns `v1 / v2`. Which URLs give "Not Found"? | **`/calculate/3/0.2`** (0.2 is not an int) and **`/calculate?v1=5&v2=2`** (no path parameters). `/calculate/10/5` → `2.0`; `/calculate/3/2?v1=1` → `1.5` (the query string is ignored) |
| **O25 Q5** | Which view returns **404** for `/profile/user123/active/2024`? | the route **`/profile/user/<username>/<status>/<year>`**: its fixed segment `user` is missing from the URL. The other three routes match |
| **J26 Q7** | `price = request.args.get("price", 0)`, `qty = request.args.get("qty", 1)`, `str(price * qty)`; open `/total?price=5&qty=2` | **`TypeError`** (500): both are the **strings** `"5"` and `"2"`, and `"5" * "2"` is invalid. (`/total` without arguments gives `0`: `0 * 1`) |
| **M26 Q3** | `/calculate` reads `a`, `b` (default `2`), `c` (default `"5"`), converts all with `int()` inside `try/except` (→ `Invalid Input`); `a + b == c` → `Sum`, `a * c == b` → `Product`, else `No match`. Match the URLs: 1 `?a=3`, 2 `?a=3&d=5`, 3 `?a=1&b=5`, 4 `?a=1&b=5&c=6` with a `Sum: 6`, b `Invalid Input`, c `Sum: 5`, d `Product: 5` | **1-c, 2-c, 3-d, 4-a** (1 and 2: 3+2=5; 3: 1·5 = b; 4: 1+5=6) |
| **O25 Q9** (MSQ) | URL `/user?username=mad1&role=admin`. Which view functions give **no error**? A. `@app.route('/user')` reading `request.args["username"]`, `["role"]`; B. `@app.route('/user/<username>/<role>')`; C. `@app.route('/user')` returning a fixed dict | **A and C** (B would need `/user/mad1/admin`: here it is **404**) |

**PYQ drill: methods and errors**

| | Question | Answer |
| --- | --- | --- |
| **O25 Q14, Q15** | `@app.route('/api/data', methods=sys.argv[1:])`; the view returns `Data retrieved...` for GET, `...updated...` for PUT, `...deleted...` for DELETE and `<h1>Unsupported operation</h1>` otherwise. Run `python server.py GET PUT POST`. What does `curl -X POST` and `curl -X DELETE` give? | POST: **`<h1>Unsupported operation</h1>`** (allowed, but no branch for it). DELETE: **`405 Method Not Allowed`** (not in `methods`) |
| **O25 Q16** | `@app.route('/login', method="GET")`: what stops the app from running? | the keyword is **`methods=["GET"]`**: `method=` raises **`TypeError`** at start-up ("did you mean 'methods'?") |
| **O25 Q17** | Fixed Q16, but the view is `def login(id)` and the route is `/login`. Open `/login` | **500 `TypeError`**: the route has no `<id>`, so Flask passes no argument for `id` |

<details>
<summary>More detail and traps</summary>

- Query parameters are never part of the route: `@app.route('/search?q=<q>')` is wrong.
- `request.args` always holds the **query string**, even in a POST request; `request.view_args` holds the path parameters.
- `flask --app app run`, `debug=True` (auto reload + debugger, not for production), typical folders `templates/` and `static/`.
- Two routes can share a view with different converters; Flask tries the more specific converter first.

</details>

**Full notes:** [4-3 Flask basics](../week4/4-3-flask-basics.md) ([URL structure and parameters](../week4/4-3-flask-basics.md#url-structure-and-parameters), [debug mode](../week4/4-3-flask-basics.md#debug-mode), [structure](../week4/4-3-flask-basics.md#flask-application-structure)), [4-5 `url_map`](../week4/4-5-more-flask-features.md#appurl_map--flask-routes), [4-7 `request.args`](../week4/4-7-request.md#requestargs), [`request.view_args`](../week4/4-7-request.md#requestview_args).

---

## 12. Forms in Flask: `request.form`

⏱ **6 min.** *Say:*

```html
<form action="/submit" method="post">
  <input type="text" name="name" required>
  <input type="checkbox" name="fruits" value="apple"> Apple
  <input type="checkbox" name="fruits" value="cherry"> Cherry
  <button type="submit">Submit</button>
</form>
```

```python
@app.route("/submit", methods=["GET", "POST"])     # POST must be allowed
def submit():
    if request.method == "POST":
        name = request.form.get("name")            # first value or None
        fruits = request.form.getlist("fruits")    # all checked boxes
        return f"name={name} fruits={fruits}"
    return "form"
```

- `method` is `get` or `post` (only these two). **GET** puts the data in the URL (`request.args`), **POST** in the body (`request.form`). Only fields with a **`name`** are sent.
- `request.form["x"]` on a missing key → **400**; `.get("x")` → `None`. Unchecked checkboxes are not sent. A route without `methods=["POST"]` gives **405** for a POST.
- Opening the URL in the browser is a **GET**; pressing the submit button of a `method="post"` form is a **POST**.

**PYQ drill**

| | Question | Answer |
| --- | --- | --- |
| **J26 Q3** | `numbers.html` has `<form method="POST" action="/">` with a text field `txtn`; the route `/` has `methods=["GET", "POST"]`. S1: opening `http://127.0.0.1:5000` makes a GET request. S2: clicking Submit invokes POST | **both correct** |
| **J26 Q4** | Same app: on POST it does `n = int(request.form["txtn"])`, builds `L` with `for i in range(n): L.append(i)` and returns `str(L)`. Input `5` | **`[0, 1, 2, 3, 4]`** |
| **O25 Q11** | `/` allows GET and POST; on POST it reads `request.form['name']` and returns `render_template_string("Hello, {{ name }}!", name=name)`. Order of events when the user submits `Alice`? | the user opens `/` (**GET**, form shown) → submits (**POST**) → Flask handles the request (`request.form`) → Jinja2 renders **`Hello, Alice!`** |
| **J25 Q16** | `/protein` (GET) reads `gender` and `weight` from `request.args`; `weight` ending in `lb` is multiplied by 0.453592; the intake is `kg × 0.8` for `male`, else `kg × 0.75`, rounded. Open `/protein?gender=FeMaLe&weight=154lb` | shows `Gender: FeMaLe`, `Weight: 154lb`, **`Recommended Intake: 52 grams`** ($154 \times 0.453592 \approx 69.85$ kg, $\times 0.75 \approx 52.4$) |
| **J25 Q17** | Same app, `/protein?gender=FEMALE&weight=60` | `Gender: FEMALE`, `Weight: 60`, **`45 grams`** ($60 \times 0.75$) |

<details>
<summary>More detail and traps</summary>

- `request.args` and `request.form` are **MultiDict**s: `get()` / `[]` give the first value, `getlist()` all, `to_dict(flat=False)` lists.
- A POST to `/submit?name=Q` with the field `name=F`: `request.form.get('name')` is `F`, `request.args.get('name')` is `Q`.
- An input without `name` is not submitted; `method="put"` in a form is sent as GET; POST is not encrypted (HTTPS does that).
- Other parts of `request`: `method`, `headers`, `get_json()`, `data`, `files`.

</details>

**Full notes:** [4-6 HTML forms](../week4/4-6-html-forms.md) ([form tag](../week4/4-6-html-forms.md#form-tag), [input tag](../week4/4-6-html-forms.md#input-tag)), [4-7 Request handling](../week4/4-7-request.md) ([`request.form`](../week4/4-7-request.md#requestform), [MultiDict](../week4/4-7-request.md#multidict-object-and-accessing-multiple-values), [`request.method`](../week4/4-7-request.md#requestmethod)).

---

## 13. `url_for`, `redirect`, `render_template`, `abort`

⏱ **6 min.** *Say:*

| Function | What it does | Example | Result |
| --- | --- | --- | --- |
| **`url_for(endpoint, **values)`** | builds the URL of a view **by function name** | `url_for('home')` | `/` |
| | route variables fill the path, **extra** arguments become the query string | `url_for('profile', username='bob', age=23)` | `/user/bob?age=23` |
| | static files | `url_for('static', filename='css/main.css')` | `/static/css/main.css` |
| **`redirect(url)`** | sends the browser elsewhere (status **302**; `code=301` is permanent) | `redirect(url_for('home'))` | `302`, `Location: /` |
| **`render_template(file, **vars)`** | renders `templates/file` with Jinja2 | `render_template('page.html', title='Hi')` | the HTML |
| **`abort(code)`** | stops with an HTTP error | `abort(404)`, `abort(403)` | error page |

```python
@app.route("/res/<int:rid>")
def res(rid):
    if rid != 1:
        abort(404)
    return "found"

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404      # return the status code too
```

- In a template: `<link rel="stylesheet" href="{{ url_for('static', filename='styles.css') }}">`.
- `url_for` takes the **function (endpoint) name**, not a path. If a route changes, links built with `url_for` update automatically.
- Codes: `404` Not Found, `403` Forbidden, `401` Unauthorized, `400` Bad Request, `405` Method Not Allowed, `500` Internal Server Error.

**PYQ drill**

| | Question | Answer |
| --- | --- | --- |
| **J25 Q7** | `@app.route("/signin/user") def login(): return url_for("login")` and `@app.route("/") def home(): return redirect(url_for("login"))`. What does the browser show for `http://127.0.0.1:5000/`? | **`/signin/user`**: `url_for("login")` is the URL of the *function* `login`, `/signin/user`; `home` redirects there, and `login` returns that text |
| **J25 Q3** | Which function correctly shows the scores for `/score` (`score.html` exists)? A. `return render('score.html', mayur=50, manoj=45)`; B. `return render_template('score.html', mayur=50, manoj=45)`; C. the decorator written **after** the function; D. `return 'score.html', mayur=50, manoj=45` | **B** (A: there is no function `render`; C: the decorator must be **above** `def`; D: not valid Python) |
| **M26 Q6** | `home.html`: `{% if user == "admin" %}<p>Welcome Admin</p>{% else %}<p>Welcome User</p>{% endif %}`; the route does `render_template("home.html", user="admin iitm")` | **Welcome User** |

<details>
<summary>More detail and traps</summary>

- `return redirect(...)`: forgetting `return` does nothing. `abort(404)` raises immediately.
- A custom error handler must return the status code, otherwise the page is sent with status 200.
- `url_for` works inside a request (or `with app.test_request_context():`); `with app.app_context():` alone is not enough.
- `abort(407)` raises `LookupError` (no exception class); return `('text', 407)` instead.
- `render_template_string(text, ...)` renders a template from a string; never pass user-written text as the template.

</details>

**Full notes:** [4-5 More Flask features](../week4/4-5-more-flask-features.md) ([`url_for`](../week4/4-5-more-flask-features.md#url-building-with-url_for), [redirect](../week4/4-5-more-flask-features.md#redirecting-requests), [errors and `abort`](../week4/4-5-more-flask-features.md#error-generation-handling-and-custom-error-pages)), [4-4 Flask templating](../week4/4-4-flask-templating.md) ([rendering](../week4/4-4-flask-templating.md#rendering-templates), [static files](../week4/4-4-flask-templating.md#static-file-serving), [template strings](../week4/4-4-flask-templating.md#flask-template-strings)).

---

## 14. Overview of MVC

⏱ **3 min.** No PYQ in these four papers. *Say:*

| | Question it answers | Does | Must **not** |
| --- | --- | --- | --- |
| **Model** | *What does the app know?* | stores the data and its rules (constraints, relationships), queries and updates, talks to databases | know how data is displayed |
| **View** | *How does it look?* | presents the data it is given (HTML, templates, forms) | control the flow |
| **Controller** | *What happens on a user action?* | handles input, validates, asks the Model to update, **chooses the View** | normally talk to the database directly |

**Flow:** user acts on the **Controller** → Controller updates the **Model** → Controller selects a **View** → the View renders → the user sees the result.

**In Flask:** SQLAlchemy models = **Model**, Jinja2 templates = **View**, route functions = **Controller**.

| Which layer? | |
| --- | --- |
| "price must be at least 0" | Model |
| the HTML table of students | View |
| the function that reads `request.form` and calls `render_template` | Controller |
| "which dashboard to show after login" | Controller |

<details>
<summary>Storage choices (same page)</summary>

**Spreadsheets** are fine for small data but cross-referencing gets hard; an **RDBMS** gives joins and enforced relationships (foreign keys); **NoSQL** stores flexible documents, with relationships handled in application code.

</details>

**Full notes:** [4-1 MVC and data storage](../week4/4-1-database-layer-MODEL.md) ([Model](../week4/4-1-database-layer-MODEL.md#model), [View](../week4/4-1-database-layer-MODEL.md#view), [Controller](../week4/4-1-database-layer-MODEL.md#controller)).

---

## Rapid-fire checklist

- [ ] RTT = 2 × one-way; requests/s = 1 / RTT; bandwidth = requests/s × size × **8**; **Gbps = 1000 Mbps**
- [ ] TCP reliable, ordered, handshake; UDP fast, no guarantee; ports 0-65,535; IPv4 32 bits, IPv6 128 bits
- [ ] Remainders bottom → top; group bits **from the right** (3 octal, 4 hex); $n$ bits = $2^n$ values
- [ ] `img`, `link`, `br` are void; `th` vs `td`; `colspan` / `rowspan`; `dd` is indented
- [ ] Specificity per counter: `!important` > inline > ID > class > element; equal → later wins
- [ ] Visible width (`content-box`) = width + padding + border (margin excluded); `inline` ignores width/height; flex items shrink
- [ ] Jinja2: `{{ }}`, `{% %}`; `length` (not `len`); `sort`, `sort(reverse=True)`, `reject("even")`; missing variable prints nothing
- [ ] `Template`: `$name`; `substitute` → `KeyError`, `safe_substitute` keeps `$name`; **one pass only**; the two syntaxes ignore each other
- [ ] `sys.argv[0]` = script, all strings, `sys.argv[1:]` = the arguments
- [ ] Flask: path parameter in the route (404 if the type does not fit), query in `request.args` (strings!), form in `request.form`, `methods=[...]` (not `method`), fixed routes beat `<variable>` routes
- [ ] `url_for('function_name')`, `redirect` → 302, `abort(404)`, `render_template('file.html', var=...)`
- [ ] MVC: Model = data and rules, View = presentation, Controller = flow and input
