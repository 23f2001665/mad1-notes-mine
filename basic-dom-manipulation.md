# 🧩 Basic DOM Manipulation Reference

---

## 1️⃣ Selecting Elements

### 📍 `document.getElementById(id)`

Finds **one element** by its unique `id`.

```html
<h2 id="title">Welcome</h2>

<script>
  const title = document.getElementById("title");
  console.log(title); // <h2 id="title">Welcome</h2>
</script>
```

---

### 📍 `document.getElementsByClassName(class)`

Returns a **live HTMLCollection** (like an array, but updates automatically).

```html
<p class="note">First</p>
<p class="note">Second</p>

<script>
  const notes = document.getElementsByClassName("note");
  console.log(notes[0].textContent); // "First"
</script>
```

---

### 📍 `document.getElementsByTagName(tag)`

Returns all elements with that tag.

```js
const paragraphs = document.getElementsByTagName("p");
console.log(paragraphs.length);
```

---

### 📍 `document.querySelector(selector)`

Finds the **first** element that matches a **CSS selector**.

```html
<p class="desc">Description</p>
<script>
  const desc = document.querySelector(".desc");
</script>
```

---

### 📍 `document.querySelectorAll(selector)`

Finds **all** elements matching a selector — returns a static **NodeList**.

```js
const items = document.querySelectorAll("ul li");
items.forEach(li => console.log(li.textContent));
```

---

## 2️⃣ Changing Content

### 📝 `textContent`

Sets or gets the text (ignores HTML tags).

```js
title.textContent = "Hello, DOM!";
```

### 🧾 `innerHTML`

Sets or gets HTML content (parses tags).

```js
desc.innerHTML = "<b>Bold description</b>";
```

### 🧱 `innerText`

Similar to `textContent`, but respects CSS styles and hidden text.

```js
title.innerText = "Visible text only";
```

---

## 3️⃣ Changing Attributes

### 🧩 `setAttribute(name, value)`

Adds or updates an attribute.

```js
const link = document.querySelector("a");
link.setAttribute("href", "https://developer.mozilla.org");
link.setAttribute("target", "_blank");
```

### 🧾 `getAttribute(name)`

Reads an attribute value.

```js
console.log(link.getAttribute("href"));
```

### ❌ `removeAttribute(name)`

Removes an attribute.

```js
link.removeAttribute("target");
```

### 📷 Shortcut properties for common attributes:

```js
img.src = "photo.jpg";
input.value = "hello";
div.id = "newId";
```

---

## 4️⃣ Event Listeners

Attach logic to user actions like `click`, `input`, `mouseover`, etc.

### 🧠 Syntax:

```js
element.addEventListener(eventType, callbackFunction);
```

### ✅ Example 1 — Click event:

```html
<button id="btn">Click me</button>

<script>
  const btn = document.getElementById("btn");

  btn.addEventListener("click", () => {
    alert("Button clicked!");
  });
</script>
```

---

### ✅ Example 2 — Input event:

```html
<input id="nameBox" placeholder="Type your name">
<p id="output"></p>

<script>
  const box = document.getElementById("nameBox");
  const out = document.getElementById("output");

  box.addEventListener("input", () => {
    out.textContent = `Hello, ${box.value}`;
  });
</script>
```

---

### ✅ Example 3 — Mouse events:

```js
element.addEventListener("mouseenter", () => element.style.background = "lightyellow");
element.addEventListener("mouseleave", () => element.style.background = "");
```

---

### 🧰 Removing an event listener:

```js
function greet() { console.log("Hello!"); }
btn.addEventListener("click", greet);
btn.removeEventListener("click", greet);
```

---

## 🧭 Quick Reference Summary

| Task             | Method                                     |
| ---------------- | ------------------------------------------ |
| Select by ID     | `getElementById("id")`                     |
| Select by Class  | `getElementsByClassName("class")`          |
| Select by Tag    | `getElementsByTagName("tag")`              |
| CSS-style Select | `querySelector(".class")`                  |
| All matches      | `querySelectorAll("selector")`             |
| Change text      | `element.textContent = "..."`              |
| Change HTML      | `element.innerHTML = "..."`                |
| Set attribute    | `element.setAttribute("name","value")`     |
| Get attribute    | `element.getAttribute("name")`             |
| Add listener     | `element.addEventListener("event", fn)`    |
| Remove listener  | `element.removeEventListener("event", fn)` |

---
