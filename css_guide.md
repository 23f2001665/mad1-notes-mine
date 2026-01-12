Got it ✅
Here’s a **complete Markdown file** with everything we discussed in this chat — from **nth-child, pseudo selectors, CSS hierarchy, Bootstrap basics** — all structured cleanly so you can keep it as a reference.

---

# 📘 CSS & Bootstrap Reference Notes

---

## 🔹 CSS `:nth-child` Pseudo-Selector

* **Definition**: Selects elements based on their order (1-based index) within their parent.
* **Formula**: `:nth-child(an + b)`

  * `n` → counts up from `0` (`0, 1, 2, 3...`)
  * `a` → cycle size (step)
  * `b` → offset (start point)

### Examples:

```css
li:nth-child(2) { color: red; }        /* 2nd child */
li:nth-child(2n) { color: blue; }      /* every 2nd child (even) */
li:nth-child(2n+1) { color: green; }   /* every odd child */
```

---

## 🔹 CSS Pseudo-Selectors

### 🟦 Pseudo-Classes (`:something`)

Apply styles based on **state/position**.

| Selector               | Meaning                       | Example                                         |
| ---------------------- | ----------------------------- | ----------------------------------------------- |
| `:first-child`         | First child of parent         | `p:first-child { color:red; }`                  |
| `:last-child`          | Last child of parent          | `li:last-child { font-weight:bold; }`           |
| `:only-child`          | Only child of parent          | `div:only-child { border:1px solid; }`          |
| `:nth-child(n)`        | nth child (1-based)           | `li:nth-child(3) { color:blue; }`               |
| `:nth-last-child(n)`   | nth child from end            | `li:nth-last-child(1) { color:green; }`         |
| `:first-of-type`       | First element of that type    | `p:first-of-type { color:purple; }`             |
| `:last-of-type`        | Last element of that type     | `p:last-of-type { color:orange; }`              |
| `:only-of-type`        | Only element of that type     | `h1:only-of-type { color:teal; }`               |
| `:nth-of-type(n)`      | nth of that type              | `tr:nth-of-type(2) { background:#eee; }`        |
| `:nth-last-of-type(n)` | nth of type from end          | `td:nth-last-of-type(1) { font-style:italic; }` |
| `:hover`               | Mouse over                    | `button:hover { background:blue; }`             |
| `:active`              | While clicking                | `a:active { color:red; }`                       |
| `:focus`               | Has keyboard focus            | `input:focus { border:2px solid blue; }`        |
| `:focus-visible`       | Focus shown only when needed  | `button:focus-visible { outline:2px solid; }`   |
| `:focus-within`        | Parent of focused element     | `form:focus-within { background:#fafafa; }`     |
| `:checked`             | Checked checkbox/radio        | `input:checked { accent-color:red; }`           |
| `:disabled`            | Disabled input                | `button:disabled { opacity:0.5; }`              |
| `:enabled`             | Enabled input                 | `input:enabled { border:1px solid; }`           |
| `:read-only`           | Read-only input               | `input:read-only { background:#eee; }`          |
| `:read-write`          | Editable input                | `input:read-write { background:#fff; }`         |
| `:valid`               | Input passes validation       | `input:valid { border:2px solid green; }`       |
| `:invalid`             | Input fails validation        | `input:invalid { border:2px solid red; }`       |
| `:required`            | Input with `required`         | `input:required { background:#fee; }`           |
| `:optional`            | Input without `required`      | `input:optional { background:#efe; }`           |
| `:empty`               | No children                   | `div:empty { display:none; }`                   |
| `:not(sel)`            | Everything except             | `p:not(.highlight) { color:gray; }`             |
| `:is(sel)`             | Simplifies multiple           | `:is(h1,h2,h3) { color:blue; }`                 |
| `:where(sel)`          | Like `:is` but no specificity | `:where(nav a) { color:inherit; }`              |
| `:has(sel)`            | (New!) parent selector        | `div:has(img) { border:2px solid; }`            |
| `:lang(xx)`            | Language-specific             | `p:lang(en) { font-style:italic; }`             |
| `:target`              | Element matched by URL `#id`  | `#section:target { background:yellow; }`        |

---

### 🟪 Pseudo-Elements (`::something`)

Style **parts of an element’s content**.

| Selector                 | Meaning                        | Example                                                       |
| ------------------------ | ------------------------------ | ------------------------------------------------------------- |
| `::before`               | Insert content before          | `p::before { content:"→ "; }`                                 |
| `::after`                | Insert content after           | `p::after { content:" ✓"; }`                                  |
| `::first-letter`         | First letter of text           | `p::first-letter { font-size:2em; }`                          |
| `::first-line`           | First line of text             | `p::first-line { font-weight:bold; }`                         |
| `::selection`            | Text selection highlight       | `::selection { background:yellow; }`                          |
| `::marker`               | List bullet/number             | `li::marker { color:red; }`                                   |
| `::placeholder`          | Input placeholder              | `input::placeholder { color:gray; }`                          |
| `::backdrop`             | Background of fullscreen modal | `dialog::backdrop { background:rgba(0,0,0,.5); }`             |
| `::file-selector-button` | Style file input button        | `input[type=file]::file-selector-button { background:blue; }` |

---

## 🔹 CSS Hierarchy & Selector Relationships

### 1. CSS Cascade

When multiple rules apply, CSS decides **which one wins**:

1. **Importance**: `!important` > everything else.
2. **Specificity**: Inline > ID > Class/pseudo-class > Element.
3. **Source order**: Later rules override earlier ones if specificity is equal.

**Specificity scoring shortcut**:

* Inline = 1000
* ID = 100
* Class / attribute / pseudo-class = 10
* Element / pseudo-element = 1

---

### 2. DOM Relationships in Selectors

* **Descendant (`A B`)**: all `B` inside `A` (any depth).
* **Child (`A > B`)**: only direct children.
* **Adjacent Sibling (`A + B`)**: only the very next sibling.
* **General Sibling (`A ~ B`)**: all siblings after `A`.
* **Universal (`*`)**: matches everything.

Example:

```html
<div>
  <h1>Heading</h1>
  <p>First para</p>
  <span>
    <p>Nested para</p>
  </span>
  <p>Second para</p>
</div>
```

* `div p {}` → all `<p>`s (3 total).
* `div > p {}` → only direct children (First + Second para).
* `h1 + p {}` → First para only.
* `h1 ~ p {}` → First + Second para.

---

### 3. Specificity Example

```html
<div id="main" class="box">
  <p>Hello</p>
</div>
```

```css
p { color: blue; }        /* specificity: 0-0-0-1 */
.box p { color: green; }  /* specificity: 0-0-1-1 */
#main p { color: red; }   /* specificity: 0-1-0-1 */
```

➡ Result: `"Hello"` will be **red** (ID rule wins).

---

## 🔹 Bootstrap Basics

### 1. Containers

* `.container`: fixed-width, responsive breakpoints.
* `.container-fluid`: always full-width.
* `.container-{breakpoint}`: fluid until that breakpoint, then fixed.

---

### 2. Grid System

* Based on **12-column flexbox grid**.
* `.row` = horizontal group.
* `.col` = auto-size column.
* `.col-6` = 50% width.
* `.col-md-4` = 33% width on `md+` screens.

Example:

```html
<div class="container">
  <div class="row">
    <div class="col-6">Half</div>
    <div class="col-6">Half</div>
  </div>
</div>
```

---

### 3. Spacing Utilities (`mb-3`, `px-2`, etc.)

Format: `{property}{sides}-{size}`

* Properties: `m` = margin, `p` = padding
* Sides: `t` = top, `b` = bottom, `s` = start, `e` = end, `x` = left+right, `y` = top+bottom, none = all
* Sizes: `0`–`5` and `auto`

Examples:

* `mb-3` → margin-bottom: 1rem
* `px-2` → padding-left/right: 0.5rem
* `m-0` → no margin

---

### 4. Buttons (`.btn`)

* Base class: `.btn`
* Variants: `.btn-primary`, `.btn-secondary`, `.btn-success`, `.btn-danger`, `.btn-warning`, `.btn-info`, `.btn-light`, `.btn-dark`
* Sizes: `.btn-sm`, `.btn-lg`
* Outline: `.btn-outline-primary`

Example:

```html
<button class="btn btn-primary">Click Me</button>
```

---

### 5. Tooltips

* Small popups on hover/focus.
* Require **Bootstrap JS initialization**.

Example:

```html
<button type="button" class="btn btn-secondary" 
        data-bs-toggle="tooltip" 
        data-bs-placement="top" 
        title="Tooltip on top">
  Hover me
</button>
```

JS activation:

```js
var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
tooltipTriggerList.map(function (el) {
  return new bootstrap.Tooltip(el)
})
```

---

✅ This file covers everything from:

* **nth-child**
* **All pseudo selectors (classes + elements)**
* **CSS hierarchy (cascade + specificity + relationships)**
* **Bootstrap basics (containers, grid, spacing, buttons, tooltips)**

---

Do you want me to also include a **ready-to-run Bootstrap HTML demo** (with all these concepts applied) at the end of this markdown file so you can test it instantly in a browser?
