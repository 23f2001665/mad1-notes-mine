
## Cascading Style Sheets

> [!WARNING]
> **⚠️ This section is reference-heavy.** Focus primarily on selectors, specificity, and commonly used pseudo-classes for exams.
> a short CSS Video tutorial!! https://youtu.be/l1mER1bV0N0?si=JzvInFpRWEqTltJ1

- CSS describes how HTML elements are to be displayed on screen. It saves a lot of work because a single CSS file can control the layout and appearance of multiple web pages at once.


## Type of CSS Selectors (Think of Them as Conditions)
```txt
IF an element matches the selector
AND no higher-priority rule overrides it
THEN apply the styles inside { }
```

### Type selector
selects all HTML elements with that tag name.

```css
/* every <p> element on the page */
p {
  color: darkgreen;
  line-height: 1.5;
}
```
A type selector can be combined with a pseudo-class:
```css
/* anchor tag (+ pseudo class HOVER) on mouse hover will be underline with Inter sans-serif font */
a:hover { 
  text-decoration: underline;
  font-family: Inter, sans-serif;
}
```

### .class selector
selects HTML elements with a specific `class` attribute.
- Use period (.) + class name

```css
/* reusable class="centered" will make the text center aligned */
.centered{
    text-align: center;
    }

.large{
    font-size: 1.25rem;
    }
```

### ID selector
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

### Attribute selector
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
} /* class="en", "en-US", ❌"english" */
```
`[attribute^="value"]`: whose value **starts with** a specific value. (no hyphen rule)

```css
[class^="en"] {
} /* class="en", "en-US", "english" */
```
`[attribute$="value"]`: whose value **ends with** a specific value.
```css
[class$="test"] {
}
```

> [!NOTE]
> `~=`, `*=`, `|=`, `^=` and `$=` compare against the **whole attribute string**, not against each class separately: `[class^="en"]` does not match `class="foo en"` (the string starts with "foo"). To pick one class out of many, use the class selector `.en` or `[class~="en"]`.


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

  <style> /* internal css */
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
- Both have the same selector `p` (same specificity), so the rule that comes **later** wins. The internal `<style>` is defined AFTER the `<link>` of the `external` css, so internal wins🏆 `BLUE`. (If the `<style>` were placed before the `<link>`, the external rule would come last and the paragraph would be red.)

#### 3. Inline CSS `<tag style=";"></tag>`
May be used to apply unique style for a single element
```html
<table>
  <tr>
    <td style="border: 1px solid black;">Statistics for Data Science I</td>
  </tr>
</table>

<p style="color: green;">p tag with inline css</p>
```
- `inline` style overrides `internal & external` stylesheets in the `head` section (unless their rule uses `!important`), so paragraph tag will now be 🏆`GREEN`❌`BLUE`

## CSS specificity

> [!WARNING]
> **From strongest to weakest:** `!important > inline > ID > class / attribute / pseudo-class > element / pseudo-element`
>
> *refers to `(pseudo)` classes & elements as well*
>
> 1. If selectors have the same specificity, the rule defined later takes priority.
> 2. If specificity is different, the more specific selector wins.
> 3. `!important` beats every normal declaration for that property on that element. If two competing declarations are both `!important`, the normal rules (specificity, then order) decide between them.

Specificity is compared as three separate counters, from left to right: **(IDs, classes / attributes / pseudo-classes, elements / pseudo-elements)**. It is not one decimal number: a single `#id` beats any number of classes, and a single class beats any number of element names. Pseudo-classes (e.g. `:hover`) count at the same level as classes. The universal selector `*` and the combinators (space, `>`, `+`, `~`) add nothing.

#### Case 1: both selectors are classes (same specificity)

👉 The rule written **later in the CSS** wins.

```css
.a { color: red; }
.b { color: blue; }
```

```html
<p class="a b">Blue text</p>
```

#### Case 2: ID selectors have higher specificity than class selectors

👉 ID rule overrides class rule (even though the class rule comes later).

```css
#t { color: red; }
.c { color: blue; }
```

```html
<p id="t" class="c">Red text</p>
```

#### Case 3: inline styles have higher priority than both ID and class selectors

👉 Inline style wins.

```css
#t { color: red; }
```

```html
<p id="t" style="color: blue;">Blue text</p>
```

#### Case 4: the `!important` declaration overrides inline, ID, and class rules

👉 `!important` wins for that property.

```css
.c { color: blue !important; }
#t { color: red; }
```

```html
<p id="t" class="c" style="color: green;">Blue text</p>
```

#### Case 5: multiple `!important` rules

When both rules use `!important`, normal specificity rules apply.

```css
.c { color: blue !important; }
#t { color: red !important; }
```

```html
<p id="t" class="c">Red text</p>
```

If specificity is equal, the rule written later in the CSS wins.

```css
.a { color: blue !important; }
.b { color: red !important; }
```

```html
<p class="a b">Red text</p>
```


### Margins, height, width, padding
1. **Margin** is the space *outside* the border (between the element and its neighbours)
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
    max-width: 500px;/* EQUIVALENT TO width: min(50%, 500px); */

    margin: 3px;
    padding: 25px 50px 75px 100px;
/* remember the 🚨ORDER is top right bottom left */
    border: 5px solid gray;

  
}
```

<details>
<summary>By default (<code>box-sizing: content-box</code>), height and width do not include padding or borders.</summary>

![padding border margin image](https://cdn.hashnode.com/res/hashnode/image/upload/v1662289464907/UChQ641Mf.png)

```txt
500px (content width) + 150px (left + right padding) + 10px (left + right border) = 660px (total width, when the parent is wide enough that width: 50% is at least 500px; max-width caps the content width at 500px)

100px (content height) + 100px (top + bottom padding) + 10px (top + bottom border) = 210px (total height)
```

</details>

### Some named colors in CSS
Named colors can be used for simplicity, for more precise colors, use `RGB (red-green-blue values), HEX codes or HSL (hue-saturation-lightness values)`

[CSS Color Names Visualizer](https://davidbau.com/colors)



### Links
When a user interacts with a link, it goes through different states.
CSS provides special pseudo-classes to style each state. Order matters:

#### `:link → :visited → :hover → :active`

("**LoVe HAte**": LinK, Visited, Hover, Active.) These pseudo-classes all have the same specificity, so when several of them match at once (e.g. a visited link under the mouse) the rule written **last** wins. If `a:hover` is written before `a:link`, the later `a:link` rule overrides it and the hover effect never appears.

#### :link
a normal, user has never clicked before link. DEFAULT STATE
👉 Use: Show users that the link is new / unexplored

```css
a:link {
  color: blue;
}
```

#### :visited
a link the user has visited
Use: Help users recognize pages they’ve already opened (for privacy, browsers only allow colour-related properties here)
```css
a:visited {
  color: purple;
}
```
#### :hover
a link when the user's mouse pointer is placed over the link.
Use: commonly used for interaction feedback. Indicate “this is clickable”
```css
a:hover {
  text-decoration: underline;
  color: darkblue;
}
```
#### :active
Applies at the exact moment the link is clicked (mouse down)
Give a **very short** “pressed link” feedback
```css
a:active {
  color: red;
}
```

For more info checkout: [User-interaction pseudo classes](2-7-css-extra.md#user-interaction-pseudo-classes)

### CSS `display` Property

The `display` property controls how an element behaves on the page.

- **inline** : flows inside text
- **block** : takes full width
- **inline-block** : behaves like inline, but allows width, height, padding, and margin like a block
- **flex** : flexible block for rows or columns
- **grid** : 2D grid system

> [!WARNING]
> `display: none;` removes the element from layout entirely. (does not take up any space) `visibility: hidden;` hides the element but keeps its space.

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
selects the `<p>` element that immediately follows a `<div>`, and share the same parent

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
