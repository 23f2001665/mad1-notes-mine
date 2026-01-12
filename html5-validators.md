# Html5 validators

## input tag validators

| Attribute                      | Applies To                 | Description                  | Example                                                      |
| ------------------------------ | -------------------------- | ---------------------------- | ------------------------------------------------------------ |
| `required`                     | All inputs                 | Field cannot be empty        | `<input type="text" required>`                               |
| `minlength`, `maxlength`       | text, password, email      | Length restriction           | `<input minlength="3" maxlength="15">`                       |
| `pattern`                      | text, password, tel, email | Regex-based format check     | `<input pattern="[A-Za-z]{3,}" title="Only letters, min 3">` |
| `min`, `max`                   | number, date, time         | Numerical/date range         | `<input type="number" min="18" max="99">`                    |
| `step`                         | number, range, date, time  | Increment restriction        | `<input type="number" step="0.5">`                           |
| `type="email"`                 | email                      | Checks valid email syntax    | `<input type="email">`                                       |
| `type="url"`                   | url                        | Checks valid URL syntax      | `<input type="url">`                                         |
| `type="tel"` + `pattern`       | tel                        | Custom phone formats         | `<input type="tel" pattern="[0-9]{10}">`                     |
| `type="number"`                | number                     | Must be numeric (no letters) | `<input type="number">`                                      |
| `type="date"`, `time`, `month` | date/time                  | Native date/time pickers     | `<input type="date" required>`                               |
| `multiple`                     | email, file                | Allows multiple entries      | `<input type="file" multiple>`                               |
| `accept`                       | file                       | MIME or extension filter     | `<input type="file" accept="image/*">`                       |
| `readonly`, `disabled`         | all                        | UI-only control              | `<input readonly value="system-assigned">`                   |


### example

```
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>HTML5 Validation Demo</title>
  <style>
    body {
      font-family: system-ui, sans-serif;
      margin: 2rem;
      background: #f7f7fa;
    }

    form {
      background: white;
      border-radius: 1rem;
      box-shadow: 0 0 10px rgba(0,0,0,0.1);
      padding: 2rem;
      max-width: 450px;
    }

    input, select, button {
      width: 100%;
      padding: 0.5rem;
      margin: 0.5rem 0 1rem 0;
      border: 1px solid #ccc;
      border-radius: 6px;
      font-size: 1rem;
      box-sizing: border-box;
    }

    /* === Pseudo-class validation styles === */
    input:valid {
      border-color: #28a745;
      background-color: #eaffea;
    }

    input:invalid {
      border-color: #dc3545;
      background-color: #ffeaea;
    }

    input:focus:invalid {
      outline: 2px solid #dc3545;
    }

    input:required:invalid {
      background-image: linear-gradient(to right, #ffeaea, white);
    }

    /* Optional visual feedback */
    input:required:valid {
      background-image: linear-gradient(to right, #eaffea, white);
    }

    button {
      background: #007bff;
      color: white;
      border: none;
      padding: 0.75rem;
      border-radius: 8px;
      cursor: pointer;
    }

    button:hover {
      background: #0056b3;
    }
  </style>
</head>
<body>

  <h2>HTML5 Validation Showcase</h2>

  <form action="/" method="POST">
    <label>Full Name (required, 3–20 chars):
      <input type="text" name="fullname" required minlength="3" maxlength="20" placeholder="Your Name">
    </label>

    <label>Email (HTML5 email validation):
      <input type="email" name="email" required placeholder="e.g. you@example.com">
    </label>

    <label>Password (6+ chars, must contain number):
      <input type="password" name="password"
             required pattern="^(?=.*[0-9]).{6,}$"
             title="At least 6 characters, including a number">
    </label>

    <label>Phone (10 digits only):
      <input type="tel" name="phone" pattern="[0-9]{10}" title="Must be 10 digits">
    </label>

    <label>Age (18–60):
      <input type="number" name="age" min="18" max="60" required>
    </label>

    <label>Website (must start with https://):
      <input type="url" name="website" pattern="https://.*" title="Must begin with https://">
    </label>

    <label>Birthday:
      <input type="date" name="dob" max="2007-12-31" required>
    </label>

    <label>Favorite Color:
      <input type="color" name="color" required>
    </label>

    <label>Profile Picture:
      <input type="file" name="photo" accept="image/*" required>
    </label>

    <label>Resume (PDF only):
      <input type="file" name="resume" accept=".pdf" required>
    </label>

    <label>Experience Level:
      <select name="level" required>
        <option value="">Choose one...</option>
        <option value="junior">Junior</option>
        <option value="mid">Mid-level</option>
        <option value="senior">Senior</option>
      </select>
    </label>

    <label>
      <input type="checkbox" required> I accept the terms and conditions
    </label>

    <button type="submit">Submit</button>
  </form>
</body>
</html>
```

## css psuedo classes for validation effects

| Pseudo-class                 | Description                        | Example Usage                                     |
| ---------------------------- | ---------------------------------- | ------------------------------------------------- |
| `:valid`                     | Input satisfies all constraints    | `input:valid { border-color: green; }`            |
| `:invalid`                   | Input violates any constraint      | `input:invalid { border-color: red; }`            |
| `:required`                  | Field has the `required` attribute | `input:required { background: #fffde7; }`         |
| `:optional`                  | Field does *not* have `required`   | `input:optional { color: gray; }`                 |
| `:in-range`                  | Number/date within `min`/`max`     | `input:in-range { color: green; }`                |
| `:out-of-range`              | Number/date outside allowed range  | `input:out-of-range { color: red; }`              |
| `:read-only` / `:read-write` | Field is locked or editable        | `input:read-only { background: #eee; }`           |
| `:checked`                   | For checkbox/radio selected        | `input:checked { accent-color: #007bff; }`        |
| `:focus:invalid`             | Focused but invalid                | `input:focus:invalid { outline: 2px solid red; }` |
| `:placeholder-shown`         | Input currently shows placeholder  | `input:placeholder-shown { color: gray; }`        |

---
