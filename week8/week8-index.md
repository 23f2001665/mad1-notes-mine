# Week 8

This week moves from the server to the **browser**. Until now the server produced every page. Now you will see how much work the browser itself does: it runs **JavaScript**, rebuilds the page through the **DOM**, talks to the server **asynchronously**, validates forms, and even runs compiled code (**WebAssembly**), all inside a **sandbox** that has to keep a malicious page from harming you.

By the end of this week, you should be able to:

* explain what **HTML, CSS and JavaScript** each do, and compare **static pages, server-side rendering (SSR) and client-side rendering (CSR)**
* describe the **original synchronous web model** and the techniques that reduce its cost (**caching, CDN, minification, lazy loading**)
* explain what **WSGI** is and how a Flask app is called by a web server
* read and write **basic JavaScript** (variables, functions, objects, loops, template literals) and avoid its classic traps (`==`, `var`, `this`)
* **select, change, create and remove DOM elements**, handle events, and choose between `innerHTML` and `textContent`
* explain **asynchronous updates** (`fetch`, `async/await`, AJAX, WebSockets) and why a blocked main thread freezes the page
* use **HTML5 validation** and the **Constraint Validation API**, and explain why the **server must validate again**
* explain **WebAssembly**, the browser **sandbox**, same-origin policy/CORS, permissions, **Subresource Integrity**, **crypto-mining**, **DoS**, **CAPTCHA** and **rate limiting**

### Topics Covered

* **[Frontend Fundamentals](8-frontend.md)**<br>
  Roles of HTML, CSS and JavaScript, JavaScript engines, static vs SSR vs CSR, the original web model, browser computation and optimisation (caching, CDN, minification, lazy loading)

* **[WSGI: How a Web Server Talks to Flask](8-wsgi.md)**<br>
  The WSGI contract (`environ`, `start_response`), middleware, and why we use Gunicorn/Apache rather than Flask's development server in production

* **[JavaScript Basics](8-javascript-basics.md)**<br>
  Types, `==` vs `===`, `var`/`let`/`const`, functions and arrow functions, objects and `this`, loops, template literals, `prompt`/`alert`, and how to include a script

* **[DOM Manipulation](8-basic-dom-manipulation.md)**<br>
  The DOM tree, selecting elements, changing content/attributes/styles, adding and removing elements, events, `document.write`, and debugging with `console` and `debugger`

* **[Asynchronous Updates](8-async-dom.md)**<br>
  Blocking vs non-blocking code, `fetch` with `async/await`, AJAX, WebSockets, other browser capabilities (canvas, storage, drag and drop) and accessibility

* **[Client-Side Validation](8-client-validation.md)**<br>
  HTML5 validation attributes, the Constraint Validation API (`validity`, `setCustomValidity`), and why client-side checks are only a convenience

* **[WebAssembly and Browser Security](8-wasm-and-browser-security.md)**<br>
  WebAssembly and its stack machine, the sandbox, same-origin policy and CORS, permissions, Subresource Integrity, crypto-mining, DoS, CAPTCHA and rate limiting

### Suggested order

`Frontend → WSGI → JavaScript → DOM → Async → Validation → WASM and security`

Each page ends with short practice questions. `verify_week8_claims.py` in this folder runs the claims of these notes (JavaScript in a real browser, Flask/WSGI/Gunicorn servers, WebAssembly, validation) and reports whether each one holds.

### Key terms

| Term | One-line meaning |
| ---- | ---------------- |
| **DOM** | The browser's in-memory tree of the page that JavaScript can read and change |
| **SSR / CSR** | HTML is assembled on the server / in the browser |
| **AJAX / `fetch`** | Request data in the background and update part of the page |
| **WSGI** | Python standard for how a web server calls a web application |
| **WebAssembly** | Compact binary format that runs in the browser at near-native speed |
| **Sandbox** | Restricted environment: a page cannot read your files or run OS commands |
| **SRI** | `integrity="sha384-…"` makes the browser refuse a script that was changed |
| **CORS** | Server's opt-in that lets another origin read its responses |
