# JavaScript Basics

In this section, we will cover the basics of JavaScript, a popular programming language used for web development. JavaScript allows you to create dynamic and interactive web pages by manipulating the Document Object Model (DOM) and handling events.

- `console.log()` is used to print output in the browser console for debugging.
```js
function add(a, b) {
    return a + b; //  gives back value
}

function logSum(a, b) {
    console.log(a + b); // just prints
}
```

## Variables and Data Types


```js
let name = "Alice";     // String
let age = 25;           // Number
let isStudent = true;   // Boolean
let x = null;           // Null
let y;                  // Undefined

// Arrays: Ordered lists of values
let fruits = ["apple", "banana", "cherry"];
console.log(fruits[0]); // apple
```
Arithmetic operations:
```js
let a = 10;
let b = 5;

console.log(a + b); // Addition
console.log(a > b); // Comparison
console.log(a === b); 
console.log(5 == '5');  // true (type coercion)
console.log(5 === '5'); // false (strict equality of same data type)

- `===` is preferred because it avoids automatic type conversion.

```

In JavaScript, variables are declared using `var`, `let`, or `const`. `var` is function-scoped and allows re-declaration (which can lead to bugs), while `let` and `const` are block-scoped (modern standard). Use `const` by default for variables that won't change.
```js
if (true) {
    var x = 10;
}
console.log(x); // Works (function-scoped)

vs

if (true) {
    let y = 20;
}
console.log(y); // Error (block-scoped)
```


## Functions

Functions in JavaScript are reusable blocks of code that perform a specific task. You can define a function using the `function` keyword or using arrow function syntax (ES6).

### Function declaration:

```javascript
function greet(name) {
    return "Hello, " + name + "!";
}
console.log(greet("Alice")); // Output: Hello, Alice!
```

### Arrow function:

```javascript
const greet = (name) => {
    return "Hello, " + name + "!";
};
console.log(greet("Bob")); // Output: Hello, Bob!
```
- Arrow functions do not have their own `this` binding; they inherit it from the surrounding context (lexical `this`).
Arrow functions can also be written in a more concise form when they have a single expression:

```javascript
const greet = name => "Hello, " + name + "!";
console.log(greet("Charlie")); // Output: Hello, Charlie!
```

## Objects

Objects in JavaScript are collections of key-value pairs. They can be created using object literals or the `new Object()` syntax.

### Object literal:

```javascript
let person = {
    name: "Alice",
    age: 30,
    city: "New York"
};
console.log(person.name); // Output: Alice
```

## Attributes and Methods

Attributes are properties of an object, while methods are functions that belong to an object. You can access attributes and methods using dot notation.

```javascript
let person = {
    name: "Alice",
    age: 30,
    city: "New York",
    greet: function() {
        return "Hello, my name is " + this.name + ".";
    }
};
console.log(person.name); // Output: Alice (attribute)
console.log(person.greet()); // Output: Hello, my name is Alice. (method)
```

## Control Structures
## If-else
```js
let number = 10;

if (number > 0) {
    console.log("Positive");
} else if (number < 0) {
    console.log("Negative");
} else {
    console.log("Zero");
}
```
## Loops
```js
// For loop
for (let i = 0; i < 3; i++) {
    console.log(i);
}

// For...of (arrays)
let fruits = ["apple", "banana"];
for (let fruit of fruits) {
    console.log(fruit);
}
```
- Avoid using `for...in` with arrays.

```js
const PI = 3.14;
// PI = 3.141; Error

let count = 1;
count = 2; // ✅ allowed
```

## Template Literals
```js
let name = "Alice";
console.log(`Hello ${name}`);
```

:::tip String Concatenation vs. Template Literals
Before ES6, we used `+` to join strings. Template literals (like `f-strings` in python) are much cleaner for multi-line strings or embedding variables.
```js
let item = "Laptop";
let price = 50000;

// Old way
console.log("The " + item + " costs Rs. " + price);

// Better way
console.log(`The ${item} costs Rs. ${price}`);
```
:::
```

### Type checking
```js
console.log(typeof "hello"); // string
console.log(typeof 10);      // number
```

### Basic input

```js
let name = prompt("Enter your name");
alert("Hello " + name);
```
```js
let userName = prompt("Enter your name:");
if (userName) {
    alert(`Hello ${userName}!`);
}
```
- undefined → variable declared but not assigned
- null → intentional empty value

## Including JavaScript in HTML

You can include JavaScript in your HTML file using the `<script>` tag. You can either write your JavaScript code directly within the `<script>` tag or link to an external JavaScript file.

### Inline JavaScript:

```html
<!DOCTYPE html>
<html>
<head>
    <title>JavaScript Basics</title>
</head>
<body>
    <h1>Hello, World!</h1>
    <script>
        console.log("This is an inline JavaScript code.");
    </script>
</body>
</html>
```

### External JavaScript:

```html
<!DOCTYPE html>
<html>
<head>
    <title>JavaScript Basics</title>
</head>
<body>
    <h1>Hello, World!</h1>
    <script src="script.js"></script>
</body>
</html>
```

In the above example, the JavaScript code is placed in an external file named `script.js`. You can write your JavaScript code in that file, and it will be executed when the HTML page is loaded.

## Conclusion

This is just a short introduction to JavaScript basics. There is much more to learn about JavaScript, including advanced topics like asynchronous programming, closures, and prototypes. More about the language you will learn in Modern Application Development II course.

### References

- [MDN Web Docs - JavaScript](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
- [JavaScript.info - The Modern JavaScript Tutorial](https://javascript.info/)
