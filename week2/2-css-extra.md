::: danger Out of syllabus
These topics are only for learning purposes if someone is really interested in styling. Can be skipped if you lack time.
:::
| Purpose     | Common Properties                  | Example |
|------------|------------------------------------|---------|
| Text       | `color`, `text-align`, `transform` | `color: #ff6347; text-align: center; text-transform: uppercase;` |
| Border     | `border`, `border-radius`          | `border: 2px dotted darkgray; border-radius: 6px;` |
| Background | `background-color`, `background-image` | `background-color: rgb(51, 52, 81);` |

- `justify`: Stretches the lines so that each line has equal width
- `vertical-align` sets the vertical alignment of an element: `baseline, length/%, sub, super, top, middle, bottom, text-top/bottom`

## Fonts
- The CSS [`font-family` property](https://www.w3schools.com/css/css_font_fallbacks.asp) specifies the font for an element.
```css
.p1 {
    font-family: "Times New Roman", Times, serif;
    font-style: italic;
   /* normal/oblique (leaning like italic) */
    font-weight: bolder;
   /* normal (400), bold (700), lighter, 100-900 thickness ranges */
   font-size: 18px;

/* shorthand version */
  font: italic bolder 18px Times, serif;

}
/* arial, georgia, courier new */
```
- `font-size`: `small, medium, large`
    - `em`: This uni`t is relative to the font size of the parent element.
    - `rem`: This unit is relative to the font size of the root HTML element.
    - `%:` This unit is relative to the font size of the parent element
    - `smaller` and `larger`: These units adjust the font size relative to th`e parent element.
👉 Always provide **fallback** fonts so the browser can choose if the first one is not found or installed properly.

## Lists
```css
ul.a {list-style-type: circle;}
ul.b {list-style-type: disc;}
ul.c {list-style-type: square;}

ol.d {list-style-type: upper-roman;}
ol.e {list-style-type: lower-roman;}
ol.f {list-style-type: lower-alpha;}
ol.g {list-style-type: decimal;}
```

## Tables
- **Borders**: `border-width`, `border-style`, `border-color`
- **Layout**: `width`, `height`, `padding`, `vertical-align`
- **Effects**: `tr:hover`, `tr:nth-child(even)`

```css
div.tablecontainer {
  overflow-x: auto;
}
```
- Table will display a horizontal scrollbar if the screen is too small to display the full content.


::: warning `<table>, <th>, and <td>` elements have separate borders.
:::


#### Center Align Block Elements
To horizontally center a block-level element, we use: 
1. `margin: auto;`
2. specify a `width` so that it does not stretch out to the edges of its container.
```css
.center {
  margin: auto;
  width: 50%; /* required */
}
<div class="center"></div>
```
<!-- 
<div class="card">
  <h2>CSS <code>position</code> Property</h2>
  <ul>
    <li><strong>static</strong> – default positioning</li>
    <li><strong>relative</strong> – positioned relative to itself</li>
    <li><strong>absolute</strong> – positioned relative to nearest positioned parent</li>
    <li><strong>fixed</strong> – fixed to viewport</li>
    <li><strong>sticky</strong> – switches between relative & fixed</li>
  </ul>
</div>
 -->

### Buttons

- `background-color` – sets the background color of the button
- `color` – controls the color of the button text
- `border` – defines the outline or boundary of the button
- `padding` – adds space between the text and the button’s border
- `border-radius` – rounds the corners of the button
- `box-shadow` – creates depth by adding a shadow effect
- `text-align` – aligns the text inside the button (usually centered)
- `font-size` – adjusts the size of the button text
- `text-decoration` – removes default styling (like underline) when links are used as buttons
- `cursor` – changes the mouse pointer (e.g., to a hand) when hovering over the button

## CSS Pseudo-Elements

A CSS pseudo-element is a special keyword that is added to a selector to style a **specific part of an element**, instead of styling the entire element.


#### Syntax
using double colons (::) followed by the pseudo-element name.
```css
selector::pseudo-element {
  CSS properties;
}
```

::: tabs
==::first-line
styles only the first visible line of text inside. 
⚠️**ONLY FOR block-level** elements & text-related properties are allowed
(color, font, background, spacing, etc.)

use: Highlight the opening line of an article or blog post.

```css
.article::first-line {
  color: #2c3e50;
  font-weight: bold;
  letter-spacing: 0.5px;
}
```

== ::first-letter
styles only the first letter of text inside.
⚠️**ONLY FOR block-level** elements & text-related properties are allowed


```css
.story::first-letter {
  font-size: 3rem;
  color: #c0392b;
  float: left;
  margin-right: 6px;
}
```
Creates magazine-style opening paragraphs.


== ::before
inserts content before the actual content of an element.

⚠️Requires the `content :` property

Use: Automatically add labels or icons:
```css
.note::before {
  content: "Note: ";
  font-weight: bold;
  color: #d35400;
}
```
Now, every `.note` element automatically starts with “Note:”.

== ::after
inserts content after the element’s content.
⚠️Requires the `content :` property

Use: Add status symbols, task lists or validation feedback.

```css
.task.completed::after {
  content: " ✓";
  color: green;
  font-weight: bold;
}
```

== ::marker
styles the bullet or number of list items.

Use: Highlight important list points. (not list text just markers)

```css
.highlights li::marker {
  color: #8e44ad;
  font-size: 1.2em;
}
```

== ::selection
styles text selected by the user (mouse drag or keyboard selection).

⚠️Only limited properties(color, background)

Use: Match text selection with theme color

```css
::selection {
  background-color: #ffeaa7;
  color: #2d3436;
}
```

== ::backdrop
styles the overlay behind dialogs or modals when they are active.
Use: Dim background to focus user attention.
```css
dialog::backdrop {
  background-color: rgba(0, 0, 0, 0.6);
}
```
:::

| Selector                 | Meaning                        |
| ------------------------ | ------------------------------ |
| `::before`               | Insert content before          |
| `::after`                | Insert content after           |
| `::first-letter`         | First letter of text           |
| `::first-line`           | First line of text             |
| `::selection`            | Text selection highlight       |
| `::marker`               | List bullet/number             |
| `::placeholder`          | Input placeholder              |
| `::backdrop`             | Background of fullscreen modal |

## CSS Pseudo-classes
A **CSS pseudo-class** is a keyword added to a selector that styles an element **based on its state, position, or condition**. Like element has effect of:

* User hovers or clicks
* Input gets focus
* Element is first/last child
* Form input is valid/invalid


#### Syntax
written using a **single colon (`:`)**.

```css
selector:pseudo-class {
  CSS properties;
}
```

#### Position-Based

These pseudo-classes depend on an element’s **position inside its parent**.

::: tabs
== :first-child
Styles an element **only if it is the first child** of its parent.

```css
.menu li:first-child {
  font-weight: bold;
}
```
Use: Highlight the first menu item.

== :last-child
Styles an element **only if it is the last child**.
Use: Style the last item differently (e.g., “Logout”).

```css
.list li:last-child {
  color: red;
}
```
== :only-child

Matches an element **only if it is the single child** of its parent.
Use: Center text when only one paragraph exists.

```css
.card p:only-child {
  text-align: center;
}
```
== :nth-child(n)

Selects elements based on **order (1-based index)**.

```css
table tr:nth-child(odd) {
  background-color: grey;
}
```
Use: Zebra-striped tables. (alternate rows with grey color background)

`:nth-last-child(n)`

Counts children **from the end**.
Use: Highlight the most recent notification.

```css
.notifications li:nth-last-child(1) {
  font-weight: bold;
}
```
:::


#### Type-Based Pseudo-Classes

##### `:first-of-type`

Selects the first occurrence of a specific element type.
Use: Emphasize opening paragraph of an article.
```css
article p:first-of-type {
  font-size: 1.1rem;
}
```
Similarily:
1. `:last-of-type` selects the last element of that type.
2. `:only-of-type`: Matches an element that is the **only one of its type**.
3.`:nth-of-type(n)`: selects the nth element of a given type.

```css
table tr:nth-of-type(2) {
  background-color: #eaeaea;
}
```


#### 👥User Interaction Pseudo-Classes
:::tabs

== :hover
Applied when the mouse pointer is over an element.

```css
.button:hover {
  background-color: #3498db;
}
```

==:active

Applied **while an element is being clicked**.

```css
a:active {
  color: red;
}
```

==:focus

Applied when an element receives keyboard focus.

```css
input:focus {
  border: 2px solid blue;
}
```
1. `:focus-visible` Focus styling **only when necessary** (keyboard users).
2. `:focus-within`: Applies to a parent when **any child has focus**.
Use: Highlight active forms.

```css
form:focus-within {
  background-color: #fafafa;
}
```

#### 🔹 Form-State Pseudo-Classes

:::tabs
== :checked
Matches checked checkboxes or radio buttons.

```css
input:checked {
  accent-color: green;
}
```

== :disabled/:enabled

```css
button:disabled {
  opacity: 0.5;
}

input:enabled {
  border-color: green;
}
```

==:read-only/:read-write

```css
input:read-only {
  background-color: #eee;
}

textarea:read-write {
  background-color: white;
}
```
==:valid/:invalid
Use: Real-time form validation feedback.


```css
input:valid {
  border: 2px solid green;
}

input:invalid {
  border: 2px solid red;
}
```

== :required/:optional

```css
input:required {
  background-color: #fff0f0;
}

input:optional {
  background-color: #f0fff0;
}
```
:::

#### Logical & Utility Pseudo-Classes

:::tabs
==:empty

Selects elements with **no children and no text**.

```css
div:empty {
  display: none;
}
```

== :not(selector)

Selects everything **except** what is specified.

```css
p:not(.important) {
  color: gray;
}
```

==:is(selector)

Simplifies multiple selectors.

```css
:is(h1, h2, h3) {
  color: navy;
}
```

== :where(selector)

Same as `:is`, but **adds no specificity**.

```css
:where(nav a) {
  text-decoration: none;
}
```
== :has(selector)
Selects a parent **based on its children**.

```css
.card:has(img) {
  border: 2px solid black;
}
```
== :target
Styles an element referenced by the URL hash.
Use: anchor-based navigation.
```css
#section1:target {
  background-color: yellow;
}
```
:::

| Selector          | Meaning                       |
| ----------------- | ----------------------------- |
| `:first-child`    | First child of parent         |
| `:last-child`     | Last child of parent          |
| `:only-child`     | Only child of parent          |
| `:nth-child(n)`   | nth child (1-based)           |
| `:first-of-type`  | First element of that type    |
| `:last-of-type`   | Last element of that type     |
| `:only-of-type`   | Only element of that type     |
| `:nth-of-type(n)` | nth of that type              |
| `:hover`          | Mouse over                    |
| `:active`         | While clicking                |
| `:focus`          | Has keyboard focus            |
| `:checked`        | Checked checkbox/radio        |
| `:disabled`       | Disabled input                |
| `:enabled`        | Enabled input                 |
| `:read-only`      | Read-only input               |
| `:read-write`     | Editable input                |
| `:valid`          | Input passes validation       |
| `:invalid`        | Input fails validation        |
| `:required`       | Input with `required`         |
| `:optional`       | Input without `required`      |
| `:empty`          | No children                   |
| `:not(sel)`       | Everything except             |
| `:is(sel)`        | Simplifies multiple           |
| `:where(sel)`     | Like `:is` but no specificity |
| `:has(sel)`       | (New!) parent selector        |
| `:target`         | Element matched by URL `#id`  |


::: details Bootstrap
👉 Bootstrap is a CSS framework that provides ready-made styles and layout utilities so we don’t have to write everything from scratch.

- To import bootstrap styles in your html file
```css
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.5/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-SgOJa3DmI69IUzQ2PVdRZhwQ+dy64/BUtbMJw1MZ8t5HZApcHrRKUc4W0kG879m7" crossorigin="anonymous">
```
- for details checkout: [Bootstrap guide MAD1 project]
- Standard styles for buttons, forms, icons
- Uses `label for`	, `aria-describedby`, `aria-labelledby` for screen readers

```html
<div class="mb-3">
  <label for="exampleInputEmail1" class="form-label">Email address</label>
  <input type="email" class="form-control" id="exampleInputEmail1" aria-describedby="emailHelp">
  <div id="emailHelp" class="form-text">
    We'll never share your email with anyone else.
  </div>
</div>

<div class="mb-3">
  <label for="exampleInputPassword1" class="form-label">Password</label>
  <input type="password" class="form-control" id="exampleInputPassword1">
</div>

<div class="mb-3 form-check">
  <input type="checkbox" class="form-check-input" id="exampleCheck1">
  <label class="form-check-label" for="exampleCheck1">Check me out</label>
</div>
```
:::

::: warning other less-used css properties if you are interested to checkout 
1. [text-decoration](https://www.w3schools.com/css/css_text_decoration.asp)
2. [text spacing](https://www.w3schools.com/css/css_text_spacing.asp)
3. [shadow](https://www.w3schools.com/css/css_text_shadow.asp)
4. [Google provides more Fonts](https://developers.google.com/fonts/docs/getting_started)
`<link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Sofia">`
5. [For more icons](https://fontawesome.com/) `<i class="fas fa-cloud"></i>`
6. [styling for HTML forms](https://www.w3schools.com/css/css_form.asp)
7. [gradients](https://www.w3schools.com/css/css3_gradients.asp)
:::
