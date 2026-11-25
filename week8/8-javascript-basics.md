# JavaScript Basics

JavaScript is the programming language of the browser. It lets a page react to the user, change itself and talk to servers. This page covers the language itself; the next pages use it to change the page ([DOM](8-basic-dom-manipulation.md)) and to fetch data ([Async](8-async-dom.md)).

## Where can I run JavaScript?

| Where | How |
| ----- | --- |
| **Browser console** | Press `F12` (or `Ctrl+Shift+I`), open the *Console* tab, type code |
| **Inside a web page** | `<script>` tag ([see below](#including-javascript-in-html)) |
| **Outside a browser** | Install Node.js and run `node file.js`, or just `node` for an interactive prompt |

> [!NOTE]
> Everything on this page that prints with `console.log` gives the same result in the browser console and in Node.js, except `prompt` and `alert`, which exist only in a browser (in Node, `typeof prompt` is `"undefined"`). The `// comment` after a `console.log(...)` line shows what it prints.

## `console.log` vs `return`

`console.log` **prints** a value for you to read. `return` **gives a value back** to the code that called the function. They are not the same thing:

```js
function add(a, b) {
    return a + b;               // hands the value back to the caller
}

function logSum(a, b) {
    // only prints; the function returns nothing
    console.log(a + b);
}

let r1 = add(2, 3);
let r2 = logSum(2, 3);          // prints 5
console.log(r1);                // 5
console.log(r2);                // undefined
```

A function with no `return` gives back `undefined`.

## Variables and data types

```js
let name = "Alice";       // String
let age = 25;             // Number
let isStudent = true;     // Boolean
let x = null;             // Null: "intentionally empty"
let y;                    // Undefined: declared but never given a value

console.log(typeof name);  // string
console.log(typeof age);   // number
console.log(y);            // undefined
console.log(x);            // null
```

| Value | `typeof` gives |
| ----- | -------------- |
| `"hello"` | `"string"` |
| `10` and `3.5` | `"number"` (JavaScript has **one** number type for integers and decimals) |
| `true` | `"boolean"` |
| `undefined` | `"undefined"` |
| `null` | **`"object"`** (a famous historical bug, kept for compatibility) |
| `[1, 2]` | **`"object"`**: use `Array.isArray(value)` to detect an array |
| `{}` | `"object"` |
| a function | `"function"` |
| `10n` (BigInt) | `"bigint"` |

* `undefined` means "no value was ever assigned". `null` means "the programmer deliberately says: nothing here".
* Numbers are 64-bit floating point, exactly like Python's `float`: `0.1 + 0.2` is `0.30000000000000004` and `0.1 + 0.2 === 0.3` is `false`. Compare decimals with a tolerance.

```js
console.log(0.1 + 0.2);         // 0.30000000000000004
console.log(0.1 + 0.2 === 0.3); // false
```

### Arrays

An array is an ordered list. Indexes start at 0, and reading past the end gives `undefined` (not an error, unlike Python's `IndexError`).

```js
let fruits = ["apple", "banana", "cherry"];
console.log(fruits[0]);        // apple
console.log(fruits.length);    // 3
console.log(fruits[5]);        // undefined
fruits.push("date");           // add to the end
console.log(fruits.at(-1));    // date
```

Useful array methods take a function and return a new array (or value):

```js
console.log([1, 2, 3].map(n => n * 2).join());              // 2,4,6
console.log([1, 2, 3, 4].filter(n => n % 2 === 0).join());  // 2,4
console.log([1, 2, 3].reduce((sum, n) => sum + n, 0));      // 6
```

## Comparing values: `==` vs `===`

`==` **converts the types first** and then compares; `===` compares **without converting** (the values must have the same type *and* value).

```js
console.log(5 == "5");    // true   (the string is converted to a number)
console.log(5 === "5");   // false  (number vs string)
console.log(0 == false);  // true
console.log(0 === false); // false
console.log(null == undefined);   // true
console.log(null === undefined);  // false
```

Some results of `==` are surprising: `"" == false` and `[] == false` are both `true`, `null == 0` is `false`, and `NaN == NaN` is `false` (use `Number.isNaN(x)`). **Use `===` and `!==` by default** so that no hidden conversion happens.

The same conversions apply to operators. `+` joins as soon as one side is a string, but `-` and `*` always do arithmetic:

```js
console.log("5" + 3);     // 53
console.log(5 + 3);       // 8
console.log("5" - 3);     // 2
console.log("3" * "4");   // 12
console.log("a" + null);  // anull
```

### Truthy and falsy

In an `if` condition, every value is treated as true or false. **Falsy** values are exactly these eight: `false`, `0`, `-0`, `0n`, `""`, `null`, `undefined`, `NaN`. Everything else is **truthy**, including some that look empty:

```js
console.log(Boolean("0"));      // true
console.log(Boolean("false"));  // true
console.log(Boolean([]));       // true
console.log(Boolean({}));       // true
console.log(Boolean(""));       // false
```

(An empty array or object is truthy, unlike in Python. Test `arr.length === 0` instead.)

## Declaring variables: `var`, `let`, `const`

| Keyword | Scope | Re-declare in the same scope? | Re-assign? |
| ------- | ----- | ----------------------------- | ---------- |
| `var` | **function** | yes (silently) | yes |
| `let` | **block** (`{ ... }`) | no, `SyntaxError` | yes |
| `const` | **block** | no | **no** |

Use **`const` by default**, `let` when the value must change, and avoid `var`.

```js
if (true) {
    var a = 10;
    let b = 20;
}
console.log(a);                           // 10 (var leaks out of the block)
try { console.log(b); } catch (e) { console.log(e.name); }   // ReferenceError
```

More differences that explain *why* `var` is avoided:

```js
// 1. var is hoisted: the name exists (as undefined) before the line that assigns it
console.log(typeof h);   // undefined
var h = 1;

// 2. let/const cannot be used before their declaration (the "temporal dead zone")
try { console.log(z); let z = 1; } catch (e) { console.log(e.name); }   // ReferenceError

// 3. const stops re-assignment, not changes inside the value
const PI = 3.14;
try { PI = 3.141; } catch (e) { console.log(e.name); }      // TypeError
const list = [1];
list.push(2);
console.log(list.length);   // 2   (the array itself changed; the variable still points at it)
```

A classic trap is a loop that creates functions. A `var` loop variable is *one* variable shared by all the functions, while `let` creates a new variable for every iteration:

```js
const withVar = [], withLet = [];
for (var i = 0; i < 3; i++) withVar.push(() => i);
for (let j = 0; j < 3; j++) withLet.push(() => j);
console.log(withVar.map(f => f()).join());   // 3,3,3
console.log(withLet.map(f => f()).join());   // 0,1,2
```

## Functions

A function is a reusable block of code. Two common ways to write one:

```js
// Function declaration
function greet(name) {
    return "Hello, " + name + "!";
}
console.log(greet("Alice"));    // Hello, Alice!

// Arrow function (ES6)
const greetArrow = (name) => {
    return "Hello, " + name + "!";
};
console.log(greetArrow("Bob")); // Hello, Bob!

// Arrow function, concise form: one expression, the value is returned automatically
const greetShort = name => "Hello, " + name + "!";
console.log(greetShort("Charlie"));   // Hello, Charlie!
```

Things to know about functions:

* **Declarations are hoisted**, so you can call them above their definition. A `const f = () => ...` is not usable before the line that defines it (it fails with `ReferenceError`).
* Arguments are loose: missing ones become `undefined` and extra ones are ignored. Give a default value with `=`:

```js
function hi(name = "guest") {
    return `hi ${name}`;
}
console.log(hi());            // hi guest
console.log(hi("Asha"));      // hi Asha
console.log(hi(undefined));   // hi guest
console.log(hi(null));        // hi null
```

* A concise arrow that returns an **object** needs parentheses, otherwise the braces are read as a function body:

```js
const bad = () => { a: 1 };      // braces = body, "a:" is a label: returns undefined
const good = () => ({ a: 1 });   // returns the object
console.log(bad());              // undefined
console.log(good().a);           // 1
```

* A `return` followed by a **line break** returns `undefined`, because JavaScript inserts a semicolon after `return`. Start the value on the same line as `return`.

## Objects

An object is a collection of **key: value** pairs (like a Python `dict`, but keys are accessed with a dot too).

```js
let person = {
    name: "Alice",
    age: 30,
    city: "New York",
    greet: function () {
        return "Hello, my name is " + this.name + ".";
    }
};
console.log(person.name);        // Alice          (attribute, dot notation)
console.log(person["age"]);      // 30             (bracket notation: also works with any string)
console.log(person.country);     // undefined      (missing key: no error)
console.log("city" in person);   // true
console.log(person.greet());     // Hello, my name is Alice.   (method)

person.country = "USA";          // add a property
delete person.age;              // remove a property
console.log(Object.keys(person).join());   // name,city,greet,country
```

An **attribute** (property) holds data; a **method** is a property whose value is a function. `{}` is the usual way to create an object; `new Object()` produces an empty object too but is rarely used.

### What is `this`?

Inside a method, `this` refers to the object **the method was called on**. It is decided by *how* the function is called, not where it was written:

```js
const p = {
    name: "Alice",
    greet() { return "Hi " + this.name; }
};
console.log(p.greet());      // Hi Alice   (called as p.greet(): this is p)

const lost = p.greet;        // copy the function out of the object
// lost() would now run with this = the global object (or undefined in strict mode),
// so this.name is NOT "Alice".  In Node it gives "Hi undefined".
```

**Arrow functions do not have their own `this`**; they use the `this` of the code around them (lexical `this`). That makes them ideal *inside* a method (for example in a callback) and a poor choice *as* the method itself:

```js
const counter = {
    n: 1,
    doubleAll(list) {
        return list.map(x => x * this.n);   // arrow: this is still counter
    }
};
console.log(counter.doubleAll([1, 2]).join());   // 1,2
```

## Control flow

```js
for (const number of [10, -3, 0]) {
    if (number > 0) {
        console.log("Positive");
    } else if (number < 0) {
        console.log("Negative");
    } else {
        console.log("Zero");
    }
}
// prints Positive, Negative, Zero
```

### Loops

```js
for (let i = 0; i < 3; i++) {
    console.log(i);
}
// prints 0, 1, 2

for (const fruit of ["apple", "banana"]) {   // for...of: the VALUES
    console.log(fruit);
}
// prints apple, banana

for (const key in ["apple", "banana"]) {     // for...in: the KEYS (as strings)
    console.log(key + " is a " + typeof key);
}
// prints "0 is a string", then "1 is a string"
```

| Loop | Gives you | Use for |
| ---- | --------- | ------- |
| `for...of` | each **value** of an iterable (array, string, ...) | arrays |
| `for...in` | each **key** (property name, always a string), including inherited enumerable ones | objects only |

`for...in` over an array returns `"0"`, `"1"`, … and would also list any property added to `Array.prototype`. **Do not use `for...in` with arrays.** Using `for...of` on a plain object fails (`TypeError: ... is not iterable`); loop over `Object.keys(obj)` instead.

## Template literals

Backtick strings can contain `${expression}` and can span several lines. They are JavaScript's equivalent of Python **f-strings**.

```js
let item = "Laptop";
let price = 50000;

// Old way
console.log("The " + item + " costs Rs. " + price);   // The Laptop costs Rs. 50000

// Template literal
console.log(`The ${item} costs Rs. ${price}`);        // The Laptop costs Rs. 50000
console.log(`2 + 3 = ${2 + 3}`);                      // 2 + 3 = 5
```

## Input and output in the browser

```js
let userName = prompt("Enter your name:");   // shows a box; returns the text typed
if (userName) {                               // null (Cancel) and "" (empty) are both falsy
    alert(`Hello ${userName}!`);              // shows a message box
}
```

* `prompt` returns a **string** (the text typed) or **`null`** if the user presses *Cancel*. That is why the `if (userName)` check matters.
* `prompt` and `alert` **pause the whole page** until the user answers, and they exist only in browsers. Real applications use forms and DOM updates instead, and `console.log` for debugging.

## Including JavaScript in HTML

**Inline**: write the code inside a `<script>` tag.

```html
<!DOCTYPE html>
<html>
<head>
    <title>JavaScript Basics</title>
</head>
<body>
    <h1>Hello, World!</h1>
    <script>
        console.log("This is inline JavaScript.");
    </script>
</body>
</html>
```

**External**: keep the code in a separate file and link it with `src`.

```html
<script src="script.js"></script>
```

External files can be cached by the browser and shared between pages, so they are preferred for anything larger than a few lines.

### Where the `<script>` goes matters

The browser reads HTML top to bottom and **runs a script as soon as it reaches it**. A script in `<head>` therefore runs before the `<body>` elements exist:

```html
<head>
    <script>document.getElementById("h").textContent = "changed";</script>
</head>
<body>
    <h1 id="h">Hello</h1>
</body>
```

This fails with `Cannot set properties of null (setting 'textContent')`, because `getElementById("h")` returned `null` (the `<h1>` has not been parsed yet). Three fixes, all checked in a browser:

| Fix | Example |
| --- | ------- |
| Put the script at the **end of `<body>`** | `<script>...</script>` after the elements |
| Add **`defer`** to an external script: it is downloaded in parallel and runs after the page is parsed | `<script src="script.js" defer></script>` |
| Wait for the **`DOMContentLoaded`** event | `document.addEventListener("DOMContentLoaded", () => { ... })` |

## Practice questions

<details>
<summary>1. What do these print? <code>typeof null</code>, <code>typeof []</code>, <code>"5" + 3</code>, <code>"5" - 3</code>, <code>5 == "5"</code>, <code>5 === "5"</code></summary>

`"object"`, `"object"`, `"53"`, `2`, `true`, `false`.
</details>

<details>
<summary>2. Why does a <code>var</code> loop that stores <code>() =&gt; i</code> in an array make every function return the same value?</summary>

`var i` is a single function-scoped variable shared by every closure. When they run after the loop, it holds its final value (3). With `let i` each iteration has its own copy, so the functions return 0, 1, 2.
</details>

<details>
<summary>3. Is <code>const items = []; items.push(1);</code> allowed?</summary>

Yes. `const` forbids re-assigning the variable (`items = []` would fail) but does not make the array immutable.
</details>

<details>
<summary>4. When do you pick <code>for...of</code> and when <code>for...in</code>?</summary>

`for...of` to get the **values** of an array (or string); `for...in` to get the **keys** of an object. Never `for...in` on an array: it yields string indexes and can include inherited properties.
</details>

<details>
<summary>5. A script in <code>&lt;head&gt;</code> calls <code>document.getElementById("x").textContent = "hi"</code> and fails. Why, and how can it be fixed?</summary>

The script runs before the element is created, so `getElementById` returns `null`. Move the script to the end of `<body>`, add `defer`, or run the code in a `DOMContentLoaded` handler.
</details>

## References

* [MDN Web Docs: JavaScript](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
* [JavaScript.info: The Modern JavaScript Tutorial](https://javascript.info/)
