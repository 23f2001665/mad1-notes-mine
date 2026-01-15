# More on HTML Elements

In the previous section, we introduced some basic HTML elements such as headings and paragraphs. In this section, we will explore more common HTML elements that are frequently used in web development.

## Lists

HTML provides three types of lists: ordered lists, unordered lists, and description lists.

### Ordered Lists

An ordered list is used to create a list of items that have a specific order. It is created using the `<ol>` tag, with each item in the list represented by an `<li>` tag.

```html
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

:::info

- Description lists are particularly useful for glossaries or terms and definitions.
- You can nest lists within other lists for more complex structures.
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
- To open the link in a new tab, you can add the `target="_blank"` attribute to the `<a>` tag.
- You can also use the `title` attribute to provide additional information about the link, which will appear as a tooltip when the user hovers over the link.
- You can create email links using the `mailto:` protocol in the `href` attribute (e.g., `<a href="mailto:someone@example.com">Send Email</a>`).
- You can create telephone links using the `tel:` protocol in the `href` attribute (e.g., `<a href="tel:+1234567890">Call Us</a>`).

:::

## Images

Images are added to a webpage using the `<img>` tag. The `src` attribute specifies the path to the image file, and the `alt` attribute provides alternative text for the image if it cannot be displayed.

```html
<img src="image.jpg" alt="Description of the image" id="sampleImage" height="200" width="300"/>
```

This will display the image located at "image.jpg" with the specified dimensions. If the image cannot be displayed, the text "Description of the image" will be shown instead.

:::info

- The `<img>` tag is a void element and does not have a closing tag.
- Better practice is to use CSS for styling images rather than using the `height` and `width` attributes directly in the HTML.
- Video and audio elements can also be added using the `<video>` and `<audio>` tags, respectively.
- Use the `id` attribute to uniquely identify the image element in the document.

:::

## Summary

In this section, we explored additional HTML elements including lists (ordered, unordered, and description lists), links, and images. These elements are fundamental for structuring content on web pages and enhancing user interaction. Understanding how to use these elements effectively is crucial for web development.

In the next section, we will delve into HTML [tables](html-tables.md), which are essential for collecting user data.
