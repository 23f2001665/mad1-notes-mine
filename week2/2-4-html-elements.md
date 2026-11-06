# More HTML Elements

In the previous section, we introduced some basic HTML elements such as headings and paragraphs. In this section, we will explore more common HTML elements that are frequently used in web development.

## Text Formatting Elements

HTML provides several elements for formatting text. Here are some of the most commonly used text formatting elements:

- `<b>`: Bold text
- `<i>`: Italic text
- `<u>`: Text with a non-textual annotation (often rendered as underlined)
- `<strong>`: Important text (usually rendered as bold)
- `<em>`: Emphasized text (usually rendered as italic)
- `<mark>`: Highlighted text
- `<small>`: Smaller text
- `<del>`: Deleted text (usually rendered with a strikethrough)
- `<ins>`: Inserted text (usually rendered with an underline)
- `<sub>`: Subscript text
- `<sup>`: Superscript text
- `<code>`: Inline code snippet
- `<pre>`: Preformatted text (preserves whitespace and line breaks)
- **`<br>`**: Line break (void element, no closing tag)

## Example

``` html[example 1]
<p>This is <b>bold</b> text.</p>
<p>This is <i>italic</i> text.</p>
<p>This is <u>underlined</u> text.</p>
<p>This is <strong>important</strong> text.</p>
<p>This is <em>emphasized</em> text.</p>
<p>This is <mark>highlighted</mark> text.</p>
<p>This is <small>smaller</small> text.</p>
<p>This is <del>deleted</del> text.</p>
<p>This is <ins>inserted</ins> text.</p>
```

Output:

This is <b>bold</b> text.<br>
This is <i>italic</i> text.<br>
This is <u>underlined</u> text.<br>
This is <strong>important</strong> text.<br>
This is <em>emphasized</em> text.<br>
This is <mark>highlighted</mark> text.<br>
This is <small>smaller</small> text.<br>
This is <del>deleted</del> text.<br>
This is <ins>inserted</ins> text.<br>

:::info INFO

- The `<b>` and `<i>` tags are used for stylistic purposes, while `<strong>` and `<em>` convey semantic meaning.
- Refer back to the section on Semantic HTML for more details on the importance of using semantic elements. [Semantic HTML](2-html-basics.md#semantic-vs-non-semantic-elements)
- Rule of thumb: Use semantic elements for meaning, and CSS for styling.

:::

## Lists

HTML provides three types of lists: ordered lists, unordered lists, and description lists.

### Ordered Lists

An ordered list is used to create a list of items that have a specific order. It is created using the `<ol>` tag, with each item in the list represented by an `<li>` tag.

``` html[example 1]
<ol>
  <li>First item</li>
  <li>Second item</li>
  <li>Third item</li>
</ol>
```

This will render as:

```txt
1. First item
2. Second item
3. Third item
```

### Unordered Lists

An unordered list is used to create a list of items that do not have a specific order. It is created using the `<ul>` tag, with each item in the list represented by an `<li>` tag.

```html
<ul>
  <li>Item one</li>
  <li>Item two</li>
  <li>Item three</li>
</ul>
```

This will render as:

```txt
- Item one
- Item two
- Item three
```

### Description Lists

A description list is used to create a list of terms and their descriptions. It is created using the `<dl>` tag, with each term represented by a `<dt>` tag and each description represented by a `<dd>` tag.

```html
<dl>
  <dt>HTML</dt>
  <dd>HyperText Markup Language</dd>
  <dt>CSS</dt>
  <dd>Cascading Style Sheets</dd>
</dl>
```

This will render as:

```txt
HTML
    HyperText Markup Language
CSS
    Cascading Style Sheets
```

:::details Details

- Description lists are particularly useful for glossaries or terms and definitions.
- We can nest lists within other lists for more complex structures.
- We can give different ordered lists different styles using the `type` attribute (e.g., `type="A"` for uppercase letters, `type="a"` for lowercase letters, `type="I"` for uppercase Roman numerals, and `type="i"` for lowercase Roman numerals).
- We can also change the starting number of an ordered list using the `start` attribute (e.g., `<ol start="5">` will start the list at 5).
- Unordered lists also have different bullet styles using the `type` attribute (e.g., `type="circle"`, `type="square"`).
- **Note:** The `type` attribute for lists is deprecated in HTML5; CSS should be used for styling instead.

:::

## Links

Links are created using the `<a>` (anchor) tag. The `href` attribute specifies the URL of the page the link goes to. The text between the opening and closing `<a>` tags is the clickable part of the link.

```html
<a href="https://www.example.com" id="example">Visit Example.com</a>
```

This will render as:

```txt
Visit Example.com
```

When clicked, it will take the user to "https://www.example.com".

:::info

- use the `id` attribute to uniquely identify the link element in the document.
- use of `name` attribute is deprecated in HTML5, and `id` should be used instead for identifying elements.

:::
  
Linking can be done to various types of resources, including webpages, email addresses, and files. The location of these resources can be external (on a different website) or internal (within the same website). Internal links can also point to specific sections within the same page using the `id` attribute. The internal link would look like this:

```html
<a href="#section1">Go to Section 1</a>
...
<h2 id="section1">Section 1</h2>
```

Here, clicking on "Go to Section 1" will take the user to the section of the page with the `id` of "section1".

:::details

- The href attribute specifies the destination, whereas the id attribute identifies an element in the document.
- The `id` attribute can be used to create a bookmark within the page.
- To open the link in a new tab, we can add the `target="_blank"` attribute to the `<a>` tag.
- We can also use the `title` attribute to provide additional information about the link, which will appear as a tooltip when the user hovers over the link.
- We can create email links using the `mailto:` protocol in the `href` attribute (e.g., `<a href="mailto:someone@example.com">Send Email</a>`).
- We can create telephone links using the `tel:` protocol in the `href` attribute (e.g., `<a href="tel:+1234567890">Call Us</a>`).

:::

## Images

Images are added to a webpage using the `<img>` tag. The `src` attribute specifies the path to the image file, and the `alt` attribute provides alternative text for the image if it cannot be displayed.

```html
<img src="image.jpg" alt="Description of the image" id="sampleImage" height="200" width="300"/>
```

This will display the image located at "image.jpg" with the specified dimensions. If the image cannot be displayed, the text "Description of the image" will be shown instead.

:::info

- The `<img>` tag is a void element and does not have a closing tag.
- **By default, html will search for the image in the same directory. We can also provide a relative or absolute path to the image.**
- Better practice is to use CSS for styling images rather than using the `height` and `width` attributes directly in the HTML.
- Video and audio elements can also be added using the `<video>` and `<audio>` tags, respectively.
- Use the `id` attribute to uniquely identify the image element in the document.

:::

## Complete Example

```html[complete example]
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>HTML Elements Example</title>

    <style>
      /* Styling an element using its id attribute */
      #sampleImage {
        border: 2px solid black;
      }
    </style>
  </head>

  <body>
    <h1>HTML Elements</h1>
    <p>This is an example of various HTML elements.</p>

    <h2>Text Formatting</h2>
    <p>This is <strong>important</strong> and <em>emphasized</em> text.</p>

    <h2>Lists</h2>

    <h3>Ordered List</h3>
    <ol>
      <li>First item</li>
      <li>Second item</li>
      <li>Third item</li>
    </ol>

    <h3>Unordered List</h3>
    <ul>
      <li>Item one</li>
      <li>Item two</li>
      <li>Item three</li>
    </ul>

    <h3>Description List</h3>
    <dl>
      <dt>HTML</dt>
      <dd>HyperText Markup Language</dd>

      <dt>CSS</dt>
      <dd>Cascading Style Sheets</dd>
    </dl>

    <h2>Links</h2>
    <p>
      Visit
      <a
        href="https://www.example.com"
        id="exampleLink"
        title="Visit Example.com"
        target="_blank"
        rel="noopener noreferrer"
      >
        Example.com
      </a>
      for more information.
    </p>

    <h2>Images</h2>
    <img
      src="image.jpg"
      alt="Description of the image"
      id="sampleImage"
      height="200"
      width="300"
    />
  </body>
</html>
```

This will be rendered as:

![Complete Example Output](../static/html-elements.png)

:::info Notes

- `id="sampleImage"` is used to apply CSS (`#sampleImage { ... }`) to the `<img>` element.
- `target="_blank"` opens the link in a new tab; `rel="noopener noreferrer"` is recommended for security.
- `<img>` is a void element (no closing tag).

:::

:::details **Try it Yourself!**

You can copy the following code into an HTML file and open it in your web browser to see how it works. Feel free to modify the content and experiment with different HTML elements!

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>HTML Elements Practice</title>
  </head>
  <body>
    <h1>Practice HTML Elements</h1>
      <h2>Text Formatting</h2>
          <p>Try adding your own text formatting using <strong>strong</strong> and <em>emphasis</em> tags.</p>
      <h2>Lists</h2>
          <h3>Ordered List</h3>
              <ol>
                  <li>Item 1</li>
                  <li>Item 2</li>
                  <li>Item 3</li>
              </ol>
          <h3>Unordered List</h3>
              <ul>
                  <li>Item A</li>
                  <li>Item B</li>
                  <li>Item C</li>
              </ul>
          <h3>Description List</h3>
              <dl>
                  <dt>Term 1</dt>
                  <dd>Description for Term 1</dd>
                  <dt>Term 2</dt>
                  <dd>Description for Term 2</dd>
              </dl>
      <h2>Links</h2>
          <p>Add a link to your favorite website:</p>
          <a href="https://www.yourfavoritewebsite.com" target="_blank">Your Favorite Website</a>
      <h2>Images</h2>
          <p>Insert an image using the <code>&lt;img&gt;</code> tag:</p>
          <img src="your-image.jpg" alt="Your Image Description" width="300" />
  </body>
</html>
```

:::

## Summary

In this section, we explored basic text formatting and additional HTML elements including lists (ordered, unordered, and description lists), links, and images. These elements are fundamental for structuring content on web pages and enhancing user interaction. Understanding how to use these elements effectively is crucial for web development.

In the next section, we will delve into HTML tables, which are used to display tabular data on web pages.
