# Tables

HTML tables are used to display data in a structured format using rows and columns. They are created using the following tags:

- `<table>`: Defines the table.
- `<tr>`: Defines a table row.
- `<th>`: Defines a table header cell.
- `<td>`: Defines a table data cell.
- `<thead>`: Groups the header content in a table know as **Table Header Section**.
- `<tbody>`: Groups the body content in a table know as **Table Body Section**.
- `<tfoot>`: Groups the footer content in a table know as **Table Footer Section**.
- `<caption>`: Adds a caption to the table.
- `colspan` and `rowspan` attributes: Used to span cells across multiple columns or rows.

:::warning Deprecated Attribute
**`border` attribute** is deprecated in HTML5, and it is recommended to use CSS for styling tables instead. We can use following CSS properties to add borders to tables:

```css
table, th, td {
    border: 1px solid black;
    border-collapse: collapse; /* Optional: to collapse borders */
}
```

:::

Let's look at each of these components in detail one by one.

## Table tag `<table>`

The `<table>` tag is used to create a table in HTML. Table elements are defined within the opening `<table>` and closing `</table>` tags.Table have rows and columns to organize data.

The `<table>` element itself has very few attributes in modern HTML. Most table layout and spacing is handled using CSS instead of HTML attributes.

**Use CSS for styling tables instead of using deprecated attributes like `bgcolor`, `align`, `frame`, `cellpadding`, `cellspacing` and `background`.**

### Example

```html
<table>
    <!-- Table content goes here -->
</table>
```

:::info Note

- We can customize the table further using CSS for styling.
- We can also give id to the table for further reference in CSS or JavaScript.

:::

## Table Rows `<tr>`

The `<tr>` tag is used to define a row in an HTML table. Each row can contain multiple cells, which are defined using the `<th>` (header cells) or `<td>` (data cells) tags.

### Example

```html
<table>
    <tr>
        <th>Header 1</th>
        <th>Header 2</th>
    </tr>
    <tr>
        <td>Data 1</td>
        <td>Data 2</td>
    </tr>
    <tr>
        <td>Data 3</td>
        <td>Data 4</td>
    </tr>
</table>
```

Here, the first `<tr>` contains header cells (`<th>`), while the subsequent `<tr>` elements contain data cells (`<td>`).

## Table Cells `<th>` and `<td>`

The `<th>` tag is used to define a header cell in an HTML table, while the `<td>` tag is used to define a standard data cell. Header cells are typically displayed in bold and centered by default.

### Example

```html
<table>
    <tr>
        <th>Header 1</th>
        <th>Header 2</th>
    </tr>
    <tr>
        <td>Data 1</td>
        <td>Data 2</td>
    </tr>
</table>
```

In this example, "Header 1" and "Header 2" are header cells, while "Data 1" and "Data 2" are standard data cells.

:::info Attributes of `<th>` and `<td>`

- `colspan`: Specifies the number of columns a cell should span.
- `rowspan`: Specifies the number of rows a cell should span.
- `scope` (for `<th>` only): Specifies whether a header cell is a header for a row, column, or group of rows or columns. Values can be "row", "col", "rowgroup", or "colgroup".

:::

## Table Sections `<thead>`, `<tbody>`, and `<tfoot>`

The `<thead>`, `<tbody>`, and `<tfoot>` tags are used to group different sections of a table for better organization, styling and semantics. Each of these sections may contain multiple rows defined by the `<tr>` tag. These tags help in separating the header, body, and footer of the table giving more structure to the table.

- `<thead>`: Defines the header section of the table, typically containing column headers.
- `<tbody>`: Defines the body section of the table, containing the main data rows.
- `<tfoot>`: Defines the footer section of the table, often used for summary or totals.

### Example

```html
<table>
    <thead>
        <tr>
            <th>Header 1</th>
            <th>Header 2</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Data 1</td>
            <td>Data 2</td>
        </tr>
        <tr>
            <td>Data 3</td>
            <td>Data 4</td>
        </tr>
    </tbody>
    <tfoot>
        <tr>
            <td>Total</td>
            <td>Data 5</td>
        </tr>
    </tfoot>
</table>
```

In this example, the table is divided into three sections: the header (`<thead>`), the body (`<tbody>`), and the footer (`<tfoot>`).

:::info Note

- Using these sectioning tags can improve the accessibility of the table and make it easier to style different parts of the table using CSS.
- They don’t have unique attributes
- But they can still take global attributes (id, class, etc.)
- These tags are optional but recommended for better structure.
- These tags don't have any visual effect on the table by default.
- **Though not commonly used, but `<thead>` can contain multiple `<tr>` elements to create multi-row headers.**

:::

## Complete Example

Here's an example of a simple HTML table with proper semantics using `<thead>`, `<tbody>`, and `<tfoot>`:

```html
<!DOCTYPE html>
<html>
<head>
    <title>HTML Table Example</title>
    <style>
        table, th, td {
            border: 1px solid black;
        }
    </style>
</head>
<body>
    <table>
    <caption>Student Grades</caption>

    <thead>
        <tr>
            <th>Name</th>
            <th>Subject</th>
            <th>Grade</th>
        </tr>
    </thead>

    <tbody>
        <tr>
            <td>Alice</td>
            <td>Math</td>
            <td>A</td>
        </tr>
        <tr>
            <td>Bob</td>
            <td>Science</td>
            <td>B+</td>
        </tr>
        <tr>
            <td>Charlie</td>
            <td>History</td>
            <td>A-</td>
        </tr>
    </tbody>

    <tfoot>
        <tr>
            <td colspan="2">Average Grade</td>
            <td>A-</td>
        </tr>
    </tfoot>

    </table>
</body>
</html>
```

This will render as:

![Table Example](../static/html-tables.png)

In this example:

- The `<table>` tag creates the table.
- The `<caption>` tag adds a title to the table.
- The `<thead>` section contains the header row with `<th>` elements.
- The `<tbody>` section contains the data rows with `<td>` elements.
- The `<tfoot>` section contains the footer row, which can be used for summary information.

:::info Note

- We can customize the appearance of tables further using CSS for styling, such as changing colors, fonts, and spacing.
- It is a good practice to use `<thead>`, `<tbody>`, and `<tfoot>` for better organization and accessibility of tables.
- We should use CSS for styling tables instead of using deprecated attributes like `border`, `bgcolor`, `background`, `align`, `cellpadding`, and `cellspacing`.

:::

:::details **Try it yourself**

You can create your own HTML table by copying the example above into a text editor and saving it with a `.html` extension. Open the file in a web browser to see how it looks!

```html
<!DOCTYPE html>
<html>
<head>
    <title>My HTML Table</title>
    <style>
        table, th, td {
            border: 1px solid black;
        }
    </style>
</head>
<body>
    <table>
    <caption>My Sample Table</caption>

    <thead>
        <tr>
            <th>Column 1</th>
            <th>Column 2</th>
        </tr>
    </thead>

    <tbody>
        <tr>
            <td>Row 1, Cell 1</td>
            <td>Row 1, Cell 2</td>
        </tr>
        <tr>
            <td>Row 2, Cell 1</td>
            <td>Row 2, Cell 2</td>
        </tr>
    </tbody>

    <tfoot>
        <tr>
            <td colspan="2">Footer Information</td>
        </tr>
    </tfoot>

    </table>
</body>
</html>
```

:::

## Summary

In this section, we explored HTML tables, which are used to display data in a structured format using rows and columns. We learned about the various tags used to create tables, including `<table>`, `<tr>`, `<th>`, `<td>`, `<thead>`, `<tbody>`, and `<tfoot>`. We also discussed how to use attributes like `colspan` and `rowspan` to customize the layout of table cells. Additionally, we highlighted the importance of using CSS for styling tables instead of deprecated HTML attributes. Understanding how to create and structure tables is essential for effectively presenting tabular data on web pages.

*We will continue to exploring more HTML elements and their usage in further sections. Specifically, we will look into forms and input elements after flask-basics section.*

:::info Additional Resources:

- [MDN Web Docs - HTML Tables](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/table)
- [W3Schools - HTML Tables](https://www.w3schools.com/html/html_tables.asp)
- [HTML Living Standard - Tables](https://html.spec.whatwg.org/multipage/tables.html)

:::
