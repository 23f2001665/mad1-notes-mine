
## WASM (Web Assembly)
- **binary instruction format** is hard to learn for human
- Executes on a stack-based virtual machine
- Runs in a sandboxed with controlled access to APIs
- Executable Format for Web **High performance** but less used 
    - `Emscripten` tool compiles C → WASM
- Enables high-performance execution of `non-JavaScript` code in browser: 
    - **high-performance execution** Ex: graphics & simulations → OpenGL
- **Near-native** performance i.e. Web + `APIs` works like regular Desktop/Mobile App. Like expose device capabilities through APIs:
    - File system access
    - Camera and sensors
    - Payments and system integration
    - Enables <span style="color:rgb(152, 205, 137)">smoother interaction with system resources</span>
    - Require explicit user permissions -> causes security concerns due to browser having access to sensitive resources

⚠️ Adoption is still limited compared to `JavaScript` but growing steadily.

## Server-side validation is essential:
- Server cannot trust that requests come from a valid frontend. Has to check datatypes `email, date range` & sanitization.
- HTTP is stateless, so the server cannot assume prior client state

## Client-side validation:

- Improves user experience by catching errors early
- Reduces unnecessary server requests
- ⚠️Must always be duplicated on the server for security


- [form](https://developer.mozilla.org/en-US/docs/Learn_web_development/Extensions/Forms/Form_validation) 
    - `required`: mandatory field
    - `minlength, maxlength`: text constraints
    - `min, max`: numeric constraints
    - `type`: predefined formats (e.g., email)
    - `pattern`: regex validation

⚠️ Not all browsers fully support these features; server-side validation is still required.

- `Javascript` validation [documentation](https://developer.mozilla.org/en-US/docs/Web/API/Constraint_validation)
```js
const email = document.getElementById("mail");

email.addEventListener("input", (event) => {
  if (email.validity.typeMismatch) {
    email.setCustomValidity("Please enter a valid email address");
  } else {
    email.setCustomValidity("");
  }
});
```

## 1. CAPTCHA
**Problem**: Automated scripts can generate a large number of requests, increasing server load.

**Solution**:
- Verify that the user is human
- A client-side script generates a verification token
- The server rejects requests without a valid token

Used in systems like ticket booking and appointment platforms like <span style="color:rgb(181, 118, 244)">Railway Tatkal, CoWin </span>
 
## 2. Sandboxing
Similar to a virtual machine but at a higher abstraction level.
- secure area that `JS` engine runs in a <span style="color:rgb(240, 96, 118)">restricted execution environment</span>
    - No direct access to no computer local files, OS resources (except HTTP connection)
    - Browser's `local` & `session` storage (with restrictions)
- popular JS file with bad version which redirects 1000s to same →  `DoS` Denial of Service server
- difficult to navigate/close page (too many resources kill it)
- exploit bugs in browser
- No access tilt, camera sensors, local storage via user browser permissions → local native compile so more secure for unstable testing version of app.

## 3. Crypto-mining Risk
- JavaScript can perform arbitrary computations in the browser
- Malicious pages may run hidden scripts (e.g., cryptocurrency mining)
- Results are sent back to the server via asynchronous requests
- Users may be unaware of resource usage

## 4. Overload and Denial of Service (DoS)
overwhelming a system with excessive requests
Client-side attack:
- A script consumes CPU resources
- Browser becomes slow or unresponsive

Server-side attack:
- Malicious script loaded by many users
- Generates large volumes of requests to a target server

This can make services unavailable.
You will learn more about `security` in [Week 9](../week9/9-Security.md)