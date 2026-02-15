
## Cascading Style Sheets

::: warning ⚠️ This section is reference-heavy. Focus primarily on selectors, specificity, and commonly used pseudo-classes for exams.
a short CSS Video tutorial!! https://youtu.be/l1mER1bV0N0?si=JzvInFpRWEqTltJ1
:::

- CSS describes how HTML elements are to be displayed on screen. It saves a lot of work because a single CSS file can control the layout and appearance of multiple web pages at once.


## Type of CSS Selectors (Think of Them as Conditions)
```txt
IF an element matches the selector
AND no higher-priority rule overrides it
THEN apply the styles inside { }
```

:::tabs
==type selector
```css
/* anchor tag (+ pseudo class HOVER) on mouse hover will be underline with Inter sans-serif font */
a:hover { 
  text-decoration: underline;
  font-family: Inter, sans-serif;
}
```
==.class selector
selects HTML elements with a specific `class` attribute.
- Use period (.) + class name

```css
/* reusable <class="centered"> will make it centered align on page*/
.centered{
    text-align: center;
    }

.large{
    font-size: 1.25rem;
    }
```
==ID selector
The id of an element is unique within a page, so the id selector is used to select 1 unique HTML element.
- Use hash (#) + id of the element.
```css
#main-header {
    font-size: 2em;
    padding: 30px 20px;
}
/* padding: VERTICAL HORIZONTAL
   30px → top & bottom
   20px → left & right */
```
==attribute selector
select elements with a specific attribute
```css
a[target] {
	color: purple;
	} /*all <a> elements with target attribute will be purple color*/ 
```
`[attribute="value"]`: select elements with a specific attribute with an **exact value**
```css
input[type="button"] {
  width: 100px;
  padding: 6px;
  background-color: lightgreen;
}/*<input> element with EXACTLY type="button"*/
```
`[attribute~="value"]`: select elements with an attribute value **containing a specific word**<br>
matches whole words (space-separated values)
```css
[title~="first"] {
  border: 5px solid yellow;
} /* "first post", "para first" but ❌"first-list", ❌"firstoy" */

```
`[attribute*="value"]`: whose attribute value contains **specific value**<br>matches any substring (partial match allowed)

```css
div[class*="post"] {
	background-color: #9a9797;
	}/* postman Aposts newpost: any class contains "post" substring background becomes grey */
```

`[attribute|="value"]`: exact match or starts with val followed by a hyphen (-).

```css
[class|="en"] {
} /* lang "en", "en-US", ❌"english" */
```
`[attribute^="value"]`: whose value **starts with** a specific value. (no hyphen rule)

```css
[class^="en"] {
} /* lang "en", "en-US", "english" */
```
`[attribute$="value"]`: whose value **ends with** a specific value.
```css
[class$="test"] {
}
```
:::


## Universal selector
The CSS rule will affect every HTML element on the page: 
```css
* {
  text-align: center;
  color: blue;
}
```
better to avoid using them as it affects every element and can make styles harder to manage in large projects.

## Grouping selector
Allows you to apply the same set of CSS rules to multiple HTML elements at once, using commas.

```css
div, span, p {
  text-align: center;
  background-color: black;
}
/* (div) OR (span) OR (p) NOT AND */
```
Apply these styles to all `<div>` elements, all `<span>` elements, and all `<p>` elements.




## How to Add CSS?
#### 1. External CSS `<link rel="stylesheet" href="style.css">`
Usually used for the common theme of your entire website within 1 file!!
- `<link>` element , inside the `<head>` section of HTML page.
```html
<html>
  <head>
    <link rel="stylesheet" href="example.css">
  </head>
<body>
```

#### 2. Internal CSS `<style></style>`
may be used if that HTML page has a unique style, separate or in addition to the external styling.

```html
<head>
  <link rel="stylesheet" href="external-style.css"> <!-- has p { color: red; } -->

  <style> /* inline css */
  p {
    color: blue;
  }

  h1 {
    color: maroon;
    margin-left: 40px;
  }
  </style>  
</head>
```
- Both have same selector `p` but internal style is defined AFTER the link of `external` css, so inline wins🏆 `BLUE`

#### 3. Inline CSS `<tag style=";"></tag>`
May be used to apply unique style for a single element
```html
<td style="border: 1px solid black;">Statistics for Data Science I</td>

<p style="color: green;">p tag with inline css</p>
```
- `inline` style overrides `internal & external` stylesheets in the `head` section, so paragraph tag will now be 🏆`GREEN`❌`BLUE`

## CSS specificity
::: warning From strongest to weakest: `!important > inline > ID > class / attribute > element`
*refers to `(pseudo)` classes & elements as well*

1. If selectors have the same specificity, the rule defined later takes priority.
2. If specificity is different, the more specific selector wins.
3. `!important` has HIGHEST priority; **overrides ALL styling rules** for that specific property on that element!

:::

---

<CSS-specificity />

---

::: details Explanation of Each Case

**Case 1:**  Both selectors are classes (same specificity).<br>
👉 The rule written **later in the CSS** wins.<br>

**Case 2:** ID selectors have higher specificity than class selectors.<br>
👉 ID rule overrides class rule.<br>


**Case 3:** Inline styles have higher priority than both ID and class selectors.<br>
👉 Inline style wins.<br>

**Case 4:** The `!important` declaration overrides inline, ID, and class rules.<br>
👉 `!important` wins for that property.<br>

**Case 5: Multiple `!important` rules**  
When both rules use `!important`, normal specificity rules apply.<br> 
If specificity is equal, the rule written later in the CSS wins.
:::


### Margins, height, width, padding
1. **Margin**
2. Padding is used to generate space around an element's content (inside borders).
3. **height**
4. **width**
5. `max-width` property sets the maximum allowed width of an element. 

- `auto` - the browser calculates
- `length` - specifies in px, pt, cm, etc.
- `%` - specifies in % of the width of the containing element

```css
div {
    height: 100px;
    width: 50%;
    max-width: 500px;/* EQUIVALENT TO width: max(50%, 500px); */

    margin: 3px;
    padding: 25px 50px 75px 100px;
/* remember the 🚨ORDER is top right bottom left */
    border: 5px solid gray;

  
}
```
::: details By default (`box-sizing: content-box`), height and width do not include padding or borders.
![padding border margin image](https://cdn.hashnode.com/res/hashnode/image/upload/v1662289464907/UChQ641Mf.png)
```txt
500px (width of content area) + 150px (left padding + right padding) + 10px (left border + right border) = 500px (as we set max-width else 660 px)

100px (height of content area) + 100px (top padding + bottom padding) + 10px (top border + bottom border) = 210px (total height)
```

### Some named colors in CSS
Named colors can be used for simplicity, for more precise colors, use `RGB (red-green-blue values), HEX codes or HSL (hue-saturation-light values)`

<iframe
  src="https://davidbau.com/colors/"
  title="CSS Color Names Visualizer"
  width="100%"
  height="520"
  style="
    border: 1px solid var(--vp-c-divider);
    border-radius: 12px;
  "
  loading="lazy"
></iframe>

:::



### Links
When a user interacts with a link, it goes through different states.
CSS provides special pseudo-classes to style each state. Order matters:

#### `:link → :visited → :hover → :active`

:::tabs
== :link
a normal, user has never clicked before link. DEFAULT STATE
👉 Use: Show users that the link is new / unexplored

```css
a:link {
  color: blue;
}
```

== :visited
a link the user has visited
Use: Help users recognize pages they’ve already opened
```css
a:visited {
  color: purple;
}
```
== :hover
a link when the user's mouse pointer is placed over the link.
Use: commonly used for interaction feedback. Indicate “this is clickable”
```css
a:hover {
  text-decoration: underline;
  color: darkblue;
}
```
== :active
Applies at the exact moment the link is clicked (mouse down)
Give a **very short** “pressed link” feedback
```css
a:active {
  color: red;
}
```
:::

<pseudo-class />

For more info checkout: [User-interaction pseudo classes](2-css-extra.md#user-interaction-pseudo-classes)

<!-- Display Property -->
<div class="card">
  <h2>CSS <code>display</code> Property</h2>
  <p>
    The <code>display</code> property controls how an element behaves on the page.
  </p>

  <ul>
    <li><strong>inline</strong> : flows inside text</li>
    <li><strong>block</strong> : takes full width</li>
    <li><strong>inline-block</strong> : behaves like inline, but allows width, height, padding, and margin like a block
</li>
    <li><strong>flex</strong> : flexible block for rows or columns</li>
    <li><strong>grid</strong> : 2D grid system</li>
  </ul>
</div>

::: warning `display: none;` removes the element from layout entirely. (does not take up any space)
:::

## CSS Combinators
Combinators define relationships between elements.

1. **Descendant (space)**: selects all nested elements (children, grandchildren, etc.)

2. **Child (`>`)**: selects direct children only
```css
div > p {
  background-color: yellow;
}
```
selects all `<p>` elements that are direct children of `<div>`

3. **Next sibling (+)**: selects the immediate next element (same parents)

```css
div + p {
  background-color: yellow;
}
```
selects the first `<p>` element that immediately follows a `<div>`, and share the same parent

4. **Subsequent sibling (~)**: selects all following siblings
    
```css
div ~ p {
  background-color: yellow;
}
```
selects all `<p>` elements that follow the `<div>` and share the same parent

| Selector | Meaning |
|--------|--------|
| `A, B` | A OR B |
| `A B` | B inside A |
| `A > B` | Direct child |
| `A + B` | Immediate sibling |
| `A ~ B` | All following siblings |
