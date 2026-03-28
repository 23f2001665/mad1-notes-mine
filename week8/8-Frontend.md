

- **Server-Side Rendering (SSR)** – HTML is generated on the server (e.g., using Jinja2 in Flask), and sent as a complete page to the browser.
- **Client-Side Rendering (CSR)** – A basic HTML shell is loaded first, and content is populated later using JavaScript and data (typically JSON) fetched from APIs.

- User-facing: GUI, browser, custom embedded interface
- Browser vs native, Device/OS specific controls

[list2node]

- HTML: what to show
- CSS: how to show
- Javascript: dynamic interaction UX
	-  interact with HTML elements `buttons, links, forms`
	- ✅ `JS` used independently to create more complex forms
	- `V8` JS engine (Chromium)
	- ❌ Machine-endpoints `APIs` Embedded devices (small web client ❌ own network protocol → server→ local temperature sensor `HTTP ❌ JS`)
	- **Transpilation**= translation py to JS + compilation


#### client-side scripting

| PROs | CONs |
| ---- | ---- |
| 1. ✅ combine well with `static` pages<br>2. ✅ less load on server but still dynamic | 1.❌ more resources on `client CPU/GPU`, security: data leakage <br2.  `JS` can client-side requests: user login, ℹ️info, datetime reuse-complex interactions server-side `NodeJS`

Machine client HTTP end-points: access APIs, post sensor ℹ️info to data collection sites (monitoring, time series analysis) 

#### Static pages
→ All/most pages can compiled ahead of time 

| PROs                                                                                                      | CONs                                               |
| --------------------------------------------------------------------------------------------------------- | -------------------------------------------------- |
| ↑ performance: server just picks up file & delivers<br>✅ cache-friendly & fast 10,000/s vs dynamic 100/s | ❌ interactions, small changes require `recompile` |

#### Run-time HTML generation server-side
- Traditional CGI/Web-Services Gateway Interface `WSGI` based apps
	- `Python (Flask, django), Ruby, PHP` 
	- CMS: Wordpress, Joomla, Drupal

| PROs | CONs |
| ---- | ---- |
| - ✅flexible<br>- ✅less security client issues on **client**<br>- ✅ easier to develop: common layouts, themes, user-login, datetime easy | Server load<br>- every page has to be generated dynamically<br>- More security issues on server<br>- DB hits ↑ cost💰↑ speed

::: details ⚙️ WSGI Components
| Component            | Description                                                     | Example                           |
| -------------------- | --------------------------------------------------------------- | --------------------------------- |
| **Web Server**       | Receives requests from users and sends them to the app          | Apache, Nginx, Gunicorn           |
| **WSGI Application** | The Python code that processes the request and sends a response | Flask/Django app                  |
| **Middleware**       | Optional layer between server and app that adds extra features  | Authentication, compression, etc. |
1. Web server sends the request to the WSGI app.
2. The app receives:
   * `environ` → info about the request (URL, method, etc.)
   * `start_response` → function to start sending a response
3. The app processes the request and sends back data to the server.
4. The server sends it to the browser.

| Benefit                     | Description                                      |
| --------------------------- | ------------------------------------------------ |
| **Framework Compatibility** | Works with Django, Flask, Pyramid, etc.          |
| **Flexibility**             | Middleware can add login systems, sessions, etc. |
| **Scalability**             | Can handle many users at once efficiently        |


### Example WSGI Code

```python
def simple_app(environ, start_response):
    status = '200 OK'
    headers = [('Content-Type', 'text/plain')]
    start_response(status, headers)
    return [b"Hello, WSGI World!"]
```


### Common WSGI Servers

| WSGI Server  | Description                     |
| ------------ | ------------------------------- |
| **Gunicorn** | Fast, used in production        |
| **uWSGI**    | Feature-rich, very configurable |
| **mod_wsgi** | Used with Apache web server     |
:::

---

::: warning 💻 Frontend: Synchronous vs Asynchronous Updates

| Feature         | **Synchronous**               | **Asynchronous**                      |
| --------------- | ----------------------------- | ------------------------------------- |
| **Execution**   | One task at a time (blocking) | Multiple tasks at once (non-blocking) |
| **UI Freezes?** | Yes, while waiting            | No, stays responsive                  |
| **Analogy**     | Waiting in line for food      | Order food and wait for buzzer        |
| **Best For**    | Small, quick operations       | API calls, background updates         |
:::

### 🍽️ Easy Real-Life Example

| Situation        | Explanation                                              |                                      |
| ---------------- | -------------------------------------------------------- | ------------------------------------ |
| **Synchronous**  | You order food and wait at the counter till it's ready.  | The page "freezes" until data loads. |
| **Asynchronous** | You order, sit down, and get a buzzer when food’s ready. | Page stays responsive while waiting. |

**Synchronous (Blocking):**

```javascript
function fetchData() {
  let response = fetch('https://example.com/data'); // blocks
  console.log("Data fetched!");
}

fetchData();
console.log("This message waits until data is fetched!");
```

**Asynchronous (Non-blocking):**

```javascript
async function fetchData() {
  let response = await fetch('https://example.com/data'); // runs in background
  console.log("Data fetched!");
}

fetchData();
console.log("This message appears immediately!");
```



::: info
TYPICALLY: issue requests → wait for response → render HTML → wait for user input
- Page update: new request sent from client, server has to respond complete page & client render again from scratch.
	- holds more redundant resources → harder to scale, ↑ work, slow-updates ❌
	- Dynamic limited by page rendering in PHP
:::

[Apache vs Nginx](https://serverguy.com/apache-vs-nginx/)

| Feature                 | Server-Side Rendering (e.g., Jinja2) | Client-Side Rendering (e.g., JS + JSON)  |
| ----------------------- | ------------------------------------ | ---------------------------------------- |
| First Page Load         | Faster                               | Slower (needs extra round trips)         |
| SEO Friendliness        | High (content is ready in HTML)      | Lower (unless prerendering is used)      |
| Interactivity           | Requires full-page reloads or AJAX   | Dynamic updates without reloading        |
| Server Load             | Higher (renders full pages)          | Lower (renders data only)                |
| Complexity on Client    | Low                                  | High (JavaScript required for rendering) |
| Template Logic Location | Server                               | Client                                   |


### Asynchronous updates
- Update only part of the page: load minimal extra data in *background* after main page has been loaded+rendered
- `AJAX` refresh in background queries to server


### [DOM (Document Object Model)](https://developer.mozilla.org/en-US/docs/Web/API/Document_Object_Model)
- tree structure, `obj-oriented` allows manipulation, paired with `JS` (Py XML)
	- composition, inheritance (parent-child)
	- loops, iterators
	- Flexible programmable but also complex frontend
```js
document.querySelector("input").addEventListener("click", () ={
  // document.getElementsByTagName("h2") returns a NodeList of the <h2>
  // elements in the document, and the first is number 0:
  const header = document.getElementsByTagName("h2").item(0);

  // The firstChild of the header is a Text node:
  header.firstChild.data = "A dynamic document";

  // Now header is "A dynamic document".
  // Access the first paragraph
  const para = document.getElementsByTagName("p").item(0);
  para.firstChild.data = "This is the first paragraph.";

  // Create a new Text node for the second paragraph
  const newText = document.createTextNode("This is the second paragraph.");

  // Create a new Element to be the second paragraph
  const newElement = document.createElement("p");

  // Put the text in the paragraph
  newElement.appendChild(newText);

  // Put the paragraph on the end of the document by appending it to
  // the body (which is the parent of para)
  para.parentNode.appendChild(newElement);
});
```
Render HTML, cookie interaction `sessions`
- `W3C` accessibility guidelines → ❌ rely on colors/font to convey meaning (if run in text-browsers/terminal)
- separate `CSS` styling from HTML gives freedom to browser-user


## WASM (Web Assembly)
- binary hard to learn for human
- stack-based virtual machine
- sandboxed with controlled access to APIs
- Executable Format for Web **High performance** but less used (`Emscripten` compile C → WASM)
- High performance execution: graphics → OpenGL

### Native Mode
- Web + `APIs` works like regular Desktop/Mobile App but security concerns with browser

## Validation
Server-side+ client-side: ❌ guarantee came from actual front-end (`email, date range, sanitization`)
	m- HTTP is stateless so recheck at server ❌ assume client in particular state


- [form](https://developer.mozilla.org/en-US/docs/Learn_web_development/Extensions/Forms/Form_validation) 
	- `required`
	- `minlength, maxlength`
	- `min, max:` for numeric vals
	- `type`
	- `pattern` REGEX match

- `Javascript` validation [documentation](https://developer.mozilla.org/en-US/docs/Web/API/Constraint_validation)
```js
const email = document.getElementById("mail");

email.addEventListener("input", (event) ={
  if (email.validity.typeMismatch) {
    email.setCustomValidity("I am expecting an email address!");
  } else {
    email.setCustomValidity("");
  }
});
```
##### Captcha
- prove you are human → limited number of clicks per unit time → page script will generate token ✅ only then server accepts request <span style="color:rgb(181, 118, 244)"Railway Tatkal, CoWin </span
 
##### Sandboxing
- secure area that `JS` engine has access to ❌ files, network resources, local storage
- popular JS file with bad version which redirects 1000s to same →  `DoS` Denial of Service server
- difficult to navigate/close page (too many resources kill it)
- exploit bugs in browser
- ❌ tilt, camera sensors, local storage via user browser permissions → local native compile ✅ smooth ↓ browser
