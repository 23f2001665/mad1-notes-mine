# Client-Side Validation

**Validation** means checking that the data a user submits is acceptable (an email looks like an email, a phone number has 10 digits, an age is in range) *before* it is used. It can happen in two places:

| | Client-side (in the browser) | Server-side |
| - | ---------------------------- | ----------- |
| Purpose | **Convenience**: tell the user immediately, avoid a useless round trip | **Security and correctness**: the last line of defence |
| Can the user bypass it? | **Yes**, trivially | No |
| Required? | Optional (nice to have) | **Always** |

> [!IMPORTANT]
> Client-side validation improves the user experience. It is **never** a security measure. The server must repeat every check.

## Why the server must validate again

The server cannot know where a request came from. The browser, `curl`, a script and an attacker's tool all send the same HTTP. Four ways the client-side checks disappear:

1. **Not using the form at all**: `curl` posts straight to the URL.
2. **Editing the page in DevTools**: delete `required`, change `type="email"` to `type="text"`.
3. **Setting values from a script**: some checks are skipped for values set by code (see below).
4. **Old or unusual clients**: anything that does not implement the checks.

All of this was reproduced against a Flask route that trusted the form. Its page contained `required` and `pattern="[0-9]{10}"`, but

```bash
curl -X POST -d 'email=not-an-email&phone=abc' http://localhost:5000/signup
```

was accepted, and the server stored exactly `email = "not-an-email"`, `phone = "abc"`. In a browser, removing `required` and changing the field type in DevTools made an empty / garbage value report `valid: true`; and a script that set a 50-character value into a field with `maxlength="8"` was not stopped (`maxlength` limits *typing*, not values assigned by code).

HTTP is also **stateless**: the server remembers nothing about the earlier steps (whether the user saw the form, or passed its checks), so each request must be checked on its own, with nothing assumed.

A server-side check for the same form:

```python
import re
from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route("/signup", methods=["POST"])
def signup():
    email = request.form.get("email", "").strip()
    phone = request.form.get("phone", "")
    errors = {}
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        errors["email"] = "enter a valid email"
    if not re.fullmatch(r"[0-9]{10}", phone):
        errors["phone"] = "phone must be exactly 10 digits"
    if errors:
        return jsonify(errors=errors), 400          # 400 Bad Request
    return jsonify(ok=True), 200
```

The `curl` request above now gets status `400` with both messages, and a valid email with a 10-digit phone gets `200`. Server-side validation also checks what HTML cannot: *is this email already registered?*, *is the date range sensible?*, and it **sanitises** values before they reach a database or a template (see [SQL injection](../week7/7-web-security.md)).

## HTML5 validation (no JavaScript needed)

Add attributes to the form controls and the browser checks them when the user presses *submit*. If anything is invalid it **blocks the submit** and shows a message next to the first bad field.

```html
<form id="f" method="post" action="/signup">
  <input id="mail"  type="email"  name="email" required>
  <input id="user"  name="user"   minlength="5" maxlength="8" required>
  <input id="phone" name="phone"  pattern="[0-9]{10}" title="10 digits">
  <input id="age"   type="number" name="age" min="18" max="60">
  <input id="date"  type="date"   name="date" min="2026-01-01" max="2026-12-31">
  <input id="site"  type="url"    name="site">
  <button>Send</button>
</form>
```

| Attribute | Meaning |
| --------- | ------- |
| `required` | The field must not be empty |
| `minlength`, `maxlength` | Minimum / maximum number of characters |
| `min`, `max` | Smallest / largest number or date |
| `step` | Allowed increments for numbers (default 1) |
| `type` | Expected format: `email`, `url`, `number`, `date`, … |
| `pattern` | A regular expression the **whole** value must match |

Behaviour that was checked in a browser, including the traps:

| Input | Result |
| ----- | ------ |
| empty `required` field | `valueMissing` |
| `type="email"`, value `not-an-email` | `typeMismatch` |
| `type="email"`, value **`a@b`** | **valid**: the browser's email rule is loose (no dot needed). Do not treat it as proof of a real address |
| `pattern="[0-9]{10}"`, value `abc` | `patternMismatch` |
| same pattern, value `12345678901` (11 digits) | `patternMismatch`: the pattern must match the **entire** value, as if it were wrapped in `^...$` |
| same pattern, **empty** (not `required`) | valid: an empty optional field is not checked, add `required` too |
| `minlength="5"`, user types `abcd` | `tooShort` |
| `minlength="5"`, value `abc` set **by a script** | **valid**: `minlength` (and `maxlength`) are only enforced for text *typed by the user* |
| `maxlength="8"`, user types 10 characters | only 8 are accepted |
| `type="number" min="18"`, value 10 | `rangeUnderflow` |
| `max="60"`, value 99 | `rangeOverflow` |
| number `25.5` with the default `step` of 1 | `stepMismatch` |
| `type="date"` before `min` | `rangeUnderflow` |
| `type="url"`, value `example.com` | `typeMismatch` (a scheme such as `https://` is required) |

Other facts:

* If the form is invalid, clicking submit **fires no `submit` event**; the browser stops first. In a test, clicking a normal button on an invalid form did not run the `submit` handler at all.
* To skip validation on purpose (for example a "Save draft" button): `<button formnovalidate>` or `<form novalidate>`. Both made the submit go through in the test.
* CSS can style fields by state: `input:invalid { border: 2px solid red; }` and `input:valid { ... }` (red and green borders were computed in the test).
* These features work in all modern browsers. The *messages* and the exact look differ between browsers, and a user can always switch them off, which is another reason the server must check again.

## JavaScript: the Constraint Validation API

Every form control has a **`validity`** object with one boolean per rule, plus functions to customise the message.

| `input.validity.…` | `true` when |
| ------------------ | ----------- |
| `valueMissing` | `required` but empty |
| `typeMismatch` | does not match `type` (email, url) |
| `patternMismatch` | does not match `pattern` |
| `tooShort` / `tooLong` | shorter than `minlength` / longer than `maxlength` |
| `rangeUnderflow` / `rangeOverflow` | below `min` / above `max` |
| `stepMismatch` | not a multiple of `step` |
| `badInput` | the browser cannot convert what was typed (e.g. letters in a number field) |
| `customError` | you called `setCustomValidity()` with a non-empty message |
| `valid` | **none** of the above |

| Member | Purpose |
| ------ | ------- |
| `input.checkValidity()` | Returns `true`/`false` and fires an `invalid` event on each invalid control; shows nothing |
| `input.reportValidity()` | Same, but also **shows** the browser's message |
| `input.validationMessage` | The message the browser would show |
| `input.setCustomValidity(msg)` | Marks the field invalid with your own message; **`""` marks it valid again** |
| `form.checkValidity()` | Checks every control of the form |

### Custom message example

```javascript
const email = document.getElementById("mail");

email.addEventListener("input", () => {
  if (email.validity.typeMismatch) {
    email.setCustomValidity("Please enter a valid email address");
  } else {
    email.setCustomValidity("");      // IMPORTANT: clear the old message
  }
});
```

In a browser test, typing `oops` made `validity.valid` false, `customError` true and `validationMessage` equal to the custom text. Typing a good address reset both. If the code never clears the message, the field stays invalid **even when the value is fine**; in a test, a leftover `setCustomValidity("stuck")` kept `valid` false for `ok@x.com` until `setCustomValidity("")` was called. Always clear it.

### A rule HTML cannot express: "passwords must match"

```javascript
const pw = document.getElementById("pw");
const pw2 = document.getElementById("pw2");

function checkMatch() {
  pw2.setCustomValidity(pw.value === pw2.value ? "" : "Passwords do not match");
}
pw.addEventListener("input", checkMatch);
pw2.addEventListener("input", checkMatch);
```

The browser still blocks the submit and shows "Passwords do not match" next to `pw2`, using the same mechanism as the built-in rules. As always, the server compares the two values again.

## Summary

* **Client-side**: HTML5 attributes first, then the Constraint Validation API for custom rules. Improves usability and saves requests.
* **Server-side**: mandatory. Check types, ranges, formats and business rules, and sanitise the values; reply with `400` and a clear message.
* Never trust anything that came from the client, including hidden fields, cookies and headers.

## Practice questions

<details>
<summary>1. A form has <code>required</code> and <code>pattern="[0-9]{10}"</code>. Can the server skip validation? Why?</summary>

No. A request can be sent without the form (`curl`, a script), or the attributes can be removed in DevTools. Client-side validation is for convenience only.
</details>

<details>
<summary>2. <code>pattern="[0-9]{10}"</code> and the value <code>12345678901</code>: valid or not?</summary>

Not valid: the whole value must match the pattern, and it has 11 digits.
</details>

<details>
<summary>3. <code>input.value = "abc"</code> is executed by a script on a field with <code>minlength="5"</code>. Is the field invalid?</summary>

No. `minlength` and `maxlength` are checked only when the user edits the field.
</details>

<details>
<summary>4. After <code>setCustomValidity("Bad")</code> the user fixes the input but the form still refuses to submit. Why?</summary>

The custom message was never cleared. Call `setCustomValidity("")` when the value becomes acceptable.
</details>

<details>
<summary>5. What is the difference between <code>checkValidity()</code> and <code>reportValidity()</code>?</summary>

Both return whether the control is valid. `reportValidity()` also displays the validation message to the user; `checkValidity()` is silent.
</details>

## References

* [MDN: Client-side form validation](https://developer.mozilla.org/en-US/docs/Learn_web_development/Extensions/Forms/Form_validation)
* [MDN: Constraint validation](https://developer.mozilla.org/en-US/docs/Web/API/Constraint_validation)
