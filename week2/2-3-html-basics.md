# HTML Introduction

HTML (HyperText Markup Language) is the standard markup language used to create web pages. It provides the structure and content of a webpage, allowing browsers to display text, images, links, and other multimedia elements. HTML5 is the current standard of HTML, introducing features and improvements for modern web development. In this section, we will cover the basics of HTML5, including its syntax and how to create a simple webpage.

## Basic Structure of an HTML Document

An HTML document consists of several key elements that define its structure. Here is a basic template for an HTML5 document:

Example of a Simple HTML Document:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>My First HTML Page</title>
</head>
<body>
  <h1>Welcome to My Webpage</h1>
  <p>This is a simple HTML document.</p>
</body>
</html>
```

Output:

![html-example](../static/html.png)

### Explanation of the Code

In the example above, we have the following key components:

- `<!DOCTYPE html>`: Declares the document type and version of HTML.
- `<html>`: The root element that contains all other HTML elements.
- `<head>`: Contains meta-information about the document, such as the title and links to stylesheets.
- `<meta charset="UTF-8">`: Specifies the character encoding for the document.
- `<title>`: Sets the title of the webpage, which appears in the browser tab.
- `<body>`: The body of the document is enclosed within the `<body>` tags. This is where the content that will be displayed on the webpage is placed.

  - Inside the `<body>`, we have a heading (`<h1>`) and a paragraph (`<p>`).
  - The `<h1>` tag defines a top-level heading. These headings range from `<h1>` to `<h6>`, with `<h1>` being the most important and `<h6>` is the least important.
  - The `<p>` tag defines a paragraph of text. It can be used to display a block of normal text.
  - We will explore more HTML elements in the next section.

:::details **Try it yourself**

You can create your own HTML document by copying the example above into a text editor and saving it with a `.html` extension. Open the file in a web browser to see how it looks!

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>My First HTML Page</title>
</head>
<body>
  <h1>Welcome to My Webpage</h1>
  <p>This is my first HTML document.</p>
</body>
</html>
```

:::

## Common HTML Elements

HTML provides a variety of elements to structure and format content. Here are some commonly used HTML elements:

- `<a>`: Defines a hyperlink.
- `<img>`: Embeds an image.
- `<ul>`: Creates an unordered list.
- `<ol>`: Creates an ordered list.
- `<li>`: Defines a list item.
- `<div>`: A container element used to group other elements.
- `<span>`: An inline container used to style a part of the text.
- `<table>`: Creates a table to display data.
- `<form>`: Defines a form for user input.

In the next section, we will explore these elements in more detail and see how they can be used to create more complex webpages.

## Attributes

Attributes provide additional information about HTML elements. They are included within the opening tag of an element and consist of a name and a value. Here are some common attributes:

- `id`: A unique identifier for an element.
- `class`: A class name that can be used to group elements for styling.
- `href`: Specifies the URL of a link (used with `<a>` tags).
- `src`: Specifies the source of an image (used with `<img>` tags).
- `alt`: Provides alternative text for an image (used with `<img>` tags).
- `style`: Allows inline CSS styling for an element.
- `title`: Provides additional information about an element, often displayed as a tooltip.

Example of an HTML element with attributes:

```html
<a href="https://www.example.com" id="exampleLink" title="Visit Example.com">Visit Example.com</a>
```

This creates a hyperlink that points to "https://www.example.com", has an `id` of "exampleLink", and displays a tooltip "Visit Example.com" when hovered over.

### Global Attributes

Some attributes are specific to certain elements (like href for links or src for images), while others are global and can be used on almost any element. Common global attributes include:

- `id`: A unique identifier for the element.
- `class`: A space-separated list of classes for the element.
- `style`: Inline CSS styles for the element.
- `title`: Additional information about the element, often displayed as a tooltip.
- `lang`: Specifies the language of the element's content.

Example of using global attributes:

```html
<div id="mainContent" class="container" style="background-color: lightblue;" title="Main Content Area">
  <h2 lang="en">Hello World</h2>
  <p>This is a sample paragraph.</p>
</div>
```

## HTML Comments

HTML comments are used to add notes or explanations within the HTML code that are not displayed in the browser. Comments can be helpful for documenting the code or temporarily disabling parts of the code during development.

Example of an HTML comment:

```html
<!-- This is a comment in HTML -->
<p>This paragraph will be displayed in the browser.</p>
<!-- <p>This paragraph is commented out and will not be displayed.</p> -->
```

This will be rendered as:

```txt
This paragraph will be displayed in the browser.
```

## Classifications of HTML Elements

Classifications of HTML elements help in understanding their behavior and purpose. Here are some common classifications:

### Container vs void Elements

HTML elements can be classified into container elements and void(empty) elements based on whether they can contain other elements or not.

- **Container Elements**: These elements can contain other HTML elements or text. They have both opening and closing tags. Examples include `<div>`, `<p>`, `<h1>` to `<h6>`, `<ul>`, `<ol>`, and `<li>`.
  
Example of a Container Element:
  
```html
<div>
  <h1>This is a Heading</h1>
  <p>This is a paragraph inside a div.</p>
</div>
```

- **Void Elements**: These elements do not contain any content and do not have a closing tag. They are self-closing. Examples include `<img>`, `<br>`, `<hr>`, and `<input>`.

Example of a Void Element:

```html
<img src="image.jpg" alt="Description of image">
<br>
<hr>
<input type="text" name="username">
```

:::info Note:

- Container elements are used to group and structure content, while void elements are used to insert standalone items like images or line breaks.
- In general we should ensure that container elements have both opening and closing tags, while void elements do not have closing tags.
- Modern HTML5 allows void elements to be written without a trailing slash (e.g., `<img>` instead of `<img />`), but both forms are acceptable.

:::

### Semantic vs Non-Semantic Elements

HTML elements can be classified into semantic and non-semantic elements based on their meaning and purpose.

- **Semantic Elements**: These elements clearly describe their meaning in a human- and machine-readable way. Examples include `<header>`, `<footer>`, `<article>`, `<section>`, `<em>` and `<strong>`. They provide better accessibility and SEO benefits.

- **Non-Semantic Elements**: These elements do not convey any specific meaning about their content. Examples include `<div>`, `<span>`, `<b>` and `<i>`. They are primarily used for styling and layout purposes without providing additional context.

| Semantic Elements | Non-Semantic Elements   |
| ---               | ---                     |
| `<header>`        | `<div id="header">`     |
| `<footer>`        | `<div id="footer">`     |
| `<article>`       | `<div class="article">` |
| `<section>`       | `<div class="section">` |
| `<nav>`           | `<div id="nav">`        |
| `<figure>`        | `<div class="figure">`  |
| `<em>`            | `<i>`                   |
| `<strong>`        | `<b>`                   |

:::info Note:

- While `<i>` and `<b>` are valid HTML elements, they only provide visual or stylistic meaning. `<em>` and `<strong>` convey semantic importance and are preferred when the emphasis or importance of text matters.
- Rule of thumb:
  - If an element describes what the content is, use a semantic element.
  - If it only groups or styles content, use a non-semantic element.

:::

## Block-level vs inline elements

<div class="card">
  <h3>Block-level Elements</h3>
  <p>
    Block-level elements always start on a new line and stretch to fill the
    full width of their container.
  </p>
  <ul>
    <li><code>&lt;div&gt;</code></li>
    <li><code>&lt;h1&gt; to &lt;h6&gt;</code></li>
    <li><code>&lt;p&gt;</code></li>
    <li><code>&lt;form&gt;</code></li>
    <li><code>&lt;section&gt;</code></li>
    <li><code>&lt;ul, ol, li&gt;</code></li>

  </ul>
</div>
<div class="card">
  <h3>Inline Elements</h3>
  <p>
    Inline elements stay within the same line and only take as much space as
    their content needs.
    <strong>width</strong> and <strong>height</strong> do not apply to inline elements.
  </p>
  <ul>
    <li><code>&lt;span&gt;</code></li>
    <li><code>&lt;a&gt;</code></li>
    <li><code>&lt;img&gt;</code></li>
    <li><code>&lt;strong, em&gt;</code></li>

  </ul>
</div>


- Block-level elements are typically used for larger sections of content, while inline elements are used for smaller pieces of content within block-level elements.
- By default, elements have block or inline behavior, which can later be changed using CSS properties like `display: block;` or `display: inline;`

<block-inline-visualizer />

::: details Explanation (Edit the HTML on the left and observe how it appears on the right)<br>1. Why do `SPAN` and `EM` appear on **same line**?<br>2. Why does `PARAGRAPH` move to the **next line**?<br>3.  `SPAN`s, `STRONG`, and `ANCHOR` are inline yet Why they take up **two lines**?<br>4. Why does `DIV` &  final `SPAN` take full line?

1. `<span>`,`<em>`, `<strong>`, `<a>` are **inline** elements so take up required width and try to fit on same line.
2. `<p>` is **block-level** element so starts on a **new line**
3. If multiple inline elements  can't fit within same line then they spill onto next line.
4. `div` is **block-level** element so occupies the **full width** of their container and Force the next element onto a new line (even if that's **inline**)
:::

## Summary

In this chapter, we learned:

- What HTML is and how a basic HTML document is structured
- Common HTML elements and attributes
- The difference between container and void elements
- Semantic vs non-semantic elements
- Block-level vs inline elements

:::tip **Extra Resources:**

- [HTML Basics (W3Schools)](https://www.w3schools.com/html/html_basic.asp)
- [HTML5 Introduction (MDN)](https://developer.mozilla.org/en-US/docs/Web/Guide/HTML/Introduction)
- [Creating a Simple HTML Page (YouTube)](https://youtu.be/PlxWf493en4?t=56) → A video tutorial on creating a simple HTML page.

:::
