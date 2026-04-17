# JavaScript Basics

In this section, we will cover the basics of JavaScript, a popular programming language used for web development. JavaScript allows you to create dynamic and interactive web pages by manipulating the Document Object Model (DOM) and handling events.

## Variables and Data Types

In JavaScript, you can declare variables using the `var`, `let`, or `const` keywords. The `var` keyword is function-scoped and can be re-declared and updated, while `let` and `const` are block-scoped. The `const` keyword is used for variables that cannot be reassigned.

```javascript
var name = "Alice"; // Using var
let age = 30; // Using let
const PI = 3.14; // Using const
```

A variable defined with `var` can be re-declared and updated:

```javascript
var name = "Bob"; // Re-declaring name
name = "Charlie"; // Updating
console.log(name); // Output: Charlie

var name = "Dave"; // Re-declaring name again
console.log(name); // Output: Dave
```

Variables defined with `let` cannot be re-declared but can be updated:

```javascript
let age = 25; // Declaring age
age = 26; // Updating age
console.log(age); // Output: 26

let age = 27; // Re-declaring age again (this will cause an error)
```

Variables defined with `const` cannot be re-assigned or re-declared in the same scope:

```javascript
const PI = 3.14;
PI = 3.14159; // This will cause an error

const MAX_USERS = 100;
const MAX_USERS = 200; // This will also cause an error
```

## Control Structures

JavaScript provides various control structures for managing the flow of your code, such as `if`, `else`, `for`, and `while` statements.

### If-else statement:

```javascript
let number = 10;
if (number > 0) {
    console.log("The number is positive.");
} else if (number < 0) {
    console.log("The number is negative.");
} else {
    console.log("The number is zero.");
}
```

JavaScript doesn't have an `elif` keyword, but you can achieve the same functionality using `if`, `else if`, and `else`.

### For loop

For loops are used in different ways in JavaScript, let's see them one by one:

#### On a range of numbers (C-like syntax):

```javascript
for (let i = 0; i < 5; i++) {
    console.log(i); // Output: 0, 1, 2, 3, 4
}
```

#### On an array:

```javascript
let fruits = ["apple", "banana", "cherry"];
for (let i = 0; i < fruits.length; i++) {
    console.log(fruits[i]); // Output: apple, banana, cherry
}
```

#### Using for...of loop (ES6):

```javascript
let fruits = ["apple", "banana", "cherry"];
for (let fruit of fruits) {
    console.log(fruit); // Output: apple, banana, cherry
}
```

#### Using for...in loop (for objects):

```javascript
let person = { name: "Alice", age: 30, city: "New York" };
for (let key in person) {
    console.log(key + ": " + person[key]); // Output: name: Alice, age: 30, city: New York
}
``` 

### While loop

```javascript
let count = 0;
while (count < 5) {
    console.log(count); // Output: 0, 1, 2, 3, 4
    count++;
}
```

| For loop type | Syntax | Use case |
| --- | --- | --- |
| C-like for loop | `for (initialization; condition; increment) { ... }` | When you need to iterate a specific number of times or over a range of numbers. |
| For...of loop | `for (variable of iterable) { ... }` | When you want to iterate over the values of an iterable object (like arrays, strings, etc.). |
| For...in loop | `for (variable in object) { ... }` | When you want to iterate over the enumerable properties of an object. (keys)|

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