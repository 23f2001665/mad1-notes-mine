# HTML Forms

HTML forms are used to collect user input and send it to the server for processing. A basic HTML form consists of various `input` , `select`, and `textarea`. The form also contains the `submit` button through `input` or `button` tag.

Here is an example of a simple HTML form:

```html
 <form action="/submit" method="post">

     <input type="text" id="name1" name="name" required>
     <input type="email" id="email1" name="email" required>
     
     <button type="submit">Submit</button>
 </form>
 ```

In this example, the form has two input fields for the user's name and email address, and a submit button. The `action` attribute specifies the URL where the form data will be sent, and the `method` attribute indicates that the form will use the POST method to send data.

Any data sent through an HTML form should have `name` and `value` attributes for every data field. The `name` attribute represent the **key** and `value` attribute represent the **value** in the form data.

After submission, the browser encodes the form data as key–value pairs (derived from name and user-entered values) and sends it to the server using the specified encoding method. For example, if a user enters "John Doe" as the name and enters `john.doe@example.com` as the email, the form data will be sent to the server somewhat similar to the following format:

```text

name=John+Doe&email=john.doe%40example.com

```

Now we will explore each of the components of an HTML form in detail.

## Form Tag

The `form` tag is used to create an HTML form. It contains various input elements, such as text fields, checkboxes, radio buttons, and submit buttons. The `form` tag has several important attributes:

- `action`: Specifies the URL where the form data will be sent when the form is submitted. This can be a relative or absolute URL.
- `method`: Specifies the HTTP method to be used when submitting the form. The most common methods are `GET` to send data as URL parameters and `POST` to send data in the request body.
- `enctype`: Specifies the encoding type for the form data when it is submitted. The default value is `application/x-www-form-urlencoded`. For file uploads, it should be set to `multipart/form-data`.
- `name`: Assigns a name to the form, which can be used to reference the form in JavaScript.
- `target`: Specifies where to display the response after submitting the form. Common values include `_self` (default, same window), `_blank` (new window/tab), `_parent`, and `_top`.

## Input Tag

The `input` tag is used to create various types of input fields in an HTML form. The `type` attribute of the `input` tag determines the type of input field. Some common types of input fields include:

- `text`: A single-line text input field.
- `email`: An input field for email addresses that validates the input format.
- `password`: An input field that masks the entered text for password input.
- `checkbox`: A checkbox input that allows users to select one or more options.
- `radio`: A radio button input that allows users to select one option from a group.
- `submit`: A button that submits the form data to the server.
- `file`: An input field that allows users to upload files.

### text Input

```html
<input type="text" name="username" id="username_id">
```

This creates a single-line text input field for the username. The `value` attribute will be taken from the user input. Here the `id` can be used to identify the input element with the HTML page and `name` and `value` will be sent over the network. We can add additional attributes to enhance the input field. Some of the commonly used attributes are:

- `placeholder`: Provides a hint to the user about what to enter in the input field.
- `size`: Specifies the width of the input field in characters.
- `maxlength`: Specifies the maximum number of characters allowed in the input field.
- `minlength`: Specifies the minimum number of characters required in the input field.
- `value`: Sets a default value for the input field.
- `pattern`: Specifies a regular expression that the input value must match for validation.

These attributes can be used be all `<input>` tags:
- `required`: Indicates that the input field must be filled out before submitting the form.
- `disabled`: Disables the input field, preventing user interaction, submission and transmission over the network.
- `title`: Provides additional information about the input field, usually displayed as a tooltip.
- `readonly`: Makes the input field read-only, preventing user modification.

### email Input

```html
<input type="email" name="user_email" id="user_email_id" required>
```

This creates an input field for email addresses. The browser will validate the input to ensure it is in a valid email format. The `required` attribute indicates that this field must be filled out before submitting the form.

### password Input

```html
<input type="password" name="user_password" id="user_password_id" required>
```

This creates a password input field where the entered text is masked for security.=

### radio Input

```html
Gender:
<input type="radio" name="gender" id="male_id" value="Male"> Male
<input type="radio" name="gender" id="female_id" value="Female"> Female
<input type="radio" name="gender" id="other_id" value="Other"> Other
```

The `radio` input type allows users to select one option from a group of related options. Each radio button has the same `name` attribute but different `value` attributes. When the form is submitted, only the selected radio button's value will be included in the form data.

We can also add some additional attributes to the radio input type:
- `checked`: Specifies that the radio button should be pre-selected when the page loads.

### checkbox Input

```html
Favourite Fruit:
<input type="checkbox" name="fruit" id="mango_id" value="Mango"> Mango
<input type="checkbox" name="fruit" id="apple_id" value="Apple"> Apple
<input type="checkbox" name="fruit" id="banana_id" value="Banana"> Banana
```

The `checkbox` input type allows users to select one or more options from a list. Each checkbox has a `name` attribute **(which should be the same for related checkboxes)** and a `value` attribute that represents the value sent to the server if the checkbox is checked. When the form is submitted, only the checked checkboxes will be included in the form data.

We can also add some additional attributes to the checkbox input type but they are similar to the radio input type.

:::info

If we want to select multiple values for the same field, we have to use `request.form.getlist('field_name')` in Flask to retrieve all selected values as a list. For example, if multiple checkboxes with the name `fruit` are checked, we can get all selected fruits using:

```python
selected_fruits = request.form.getlist('fruit')
```

:::

### submit Input

```html
<input type="submit" value="Submit Form">
```

This creates a submit button that, when clicked, will submit the form data to the server. The `value` attribute specifies the text displayed on the button.
The `submit` input type does not support additional attributes like other input types, but we can use the `form` attribute to associate the button with a specific form if needed.

## Button Tag

The `button` tag can also be used to create a submit button in an HTML form. It provides more flexibility in terms of content and styling compared to the `input` tag.

```html
<button type="submit">Submit Form</button>
```

This creates a submit button with the text "Submit Form". The `type` attribute specifies that this button is a submit button. The `button` tag can contain HTML content, such as images or other elements, making it more versatile than the `input` tag for buttons and recommended for use in modern web development.

## Select Tag

The `select` tag is used to create a drop-down list in an HTML form. It contains multiple `option` tags, each representing a choice in the drop-down list.

```html

<label for="cars">Choose a car:</label>
<select name="cars" id="cars_id">
  <option value="volvo">Volvo</option>
  <option value="saab">Saab</option>
  <option value="fiat">Fiat</option>
  <option value="audi">Audi</option>
</select>
```

This creates a drop-down list with four car options. The `name` attribute specifies the name of the select field, and each `option` tag has a `value` attribute that represents the value sent to the server when that option is selected.

We can also add some additional attributes to the select tag:

- `multiple`: Allows users to select multiple options from the drop-down list.
- `size`: Specifies the number of visible options in the drop-down list.

### Option Tag

The `option` tag is used within the `select` tag to define individual options in a drop-down list.

```html
<option value="volvo">Volvo</option>
```

This creates an option in the drop-down list with the display text "Volvo" and a value of "volvo". When the user selects this option, the value "volvo" will be sent to the server as part of the form data.
We can also add some additional attributes to the option tag:

- `selected`: Specifies that this option should be pre-selected when the page loads.
- `hidden`: Hides the option from the dropdown list while keeping it in the DOM.
- `label`: Provides a shorter label for the option, which can be used for accessibility purposes.

:::info Providing a default blank option
To provide a default blank option in a select dropdown, we can add an option tag with an empty value at the beginning of the select element. This allows users to see a blank option when they first interact with the dropdown.

```html
<select name="cars" id="cars_id">
  <option value="" disabled selected>Select a car</option>
  <option value="volvo">Volvo</option>
  <option value="saab">Saab</option>
  <option value="fiat">Fiat</option>
  <option value="audi">Audi</option>
</select>
```

In this example, the first option has an empty value and is disabled and selected by default. This prompts users to select a car from the dropdown.

:::

:::info Multiple Selection

Same as `checkbox` input type, if we want to select multiple values from the `select` dropdown, we have to add the `multiple` attribute to the `select` tag and use `request.form.getlist('field_name')` in Flask to retrieve all selected values as a list. For example:

```html
<select name="cars" id="cars_id" multiple>
  <option value="volvo">Volvo</option>
  <option value="saab">Saab</option>
  <option value="fiat">Fiat</option>
  <option value="audi">Audi</option>
</select>
```

And in Flask, we can get all selected cars using:

```python
selected_cars = request.form.getlist('cars')
```

:::

## `file` input

We can also use the `input` tag to create a file upload field in an HTML form. The `type` attribute should be set to `file` to create a file input field. But to successfully upload a file, the form's `enctype` attribute must be set to `multipart/form-data`.

```html
<form action="/upload" method="post" enctype="multipart/form-data">
  <input type="file" name="file_upload" id="file_upload_id" required>
  <button type="submit">Upload File</button>
</form>
```

This creates a file input field that allows users to select a file from their device for upload. The `required` attribute indicates that a file must be selected before submitting the form.

Common attributes for the file input type include:

- `accept`: Specifies the types of files that the server accepts (e.g., `image/*`, `.pdf`).
- `multiple`: Allows users to select multiple files for upload.

## textarea Tag

The `textarea` tag is used to create a multi-line text input field in an HTML form.

```html
<textarea name="message" id="message_id" rows="4" cols="50" placeholder="Enter your message here..." required></textarea>
``` 

This creates a multi-line text area for users to enter a message. The `rows` and `cols` attributes specify the visible dimensions of the text area, while the `placeholder` attribute provides a hint to the user about what to enter. The `required` attribute indicates that this field must be filled out before submitting the form.

Common attributes for the textarea tag include:

- `maxlength`: Specifies the maximum number of characters allowed in the text area.
- `minlength`: Specifies the minimum number of characters required in the text area.

## Label Tag

The `label` tag is used to define a label for an input element in an HTML form. It improves accessibility and usability by associating a text description with the corresponding input field.

```html
<label for="username_id">Username:</label>
<input type="text" name="username" id="username_id">
```

Label tags can be associated with input elements in two ways:

1. Using the `for` attribute: The `for` attribute of the `label` tag should match the `id` attribute of the corresponding input element. This creates a link between the label and the input field.
2. Wrapping the input element: The input element can be nested inside the `label` tag.

## Complete Form Example

```html
<!DOCTYPE html>
<html>
<head>
    <title>HTML Form Example</title>
</head>
<body>
    <h1>The Example Form</h1>

<form action="/submit" method="post" enctype="multipart/form-data">
    <div id="user_info_section">
    <label for="username_id">Username:</label>
    <input type="text" name="username" id="username_id" placeholder="Enter your username" required>

    <label for="user_email_id">Email:</label>
    <input type="email" name="user_email" id="user_email_id" placeholder="Enter your email" required>

    <label for="user_password_id">Password:</label>
    <input type="password" name="user_password" id="user_password_id" placeholder="Enter your password" required>
    </div>

    <div id="gender_section">
    <label for="male_id">Male:</label>
    <input type="radio" name="gender" id="male_id" value="Male">
    <label for="female_id">Female:</label>
    <input type="radio" name="gender" id="female_id" value="Female"> Female
    </div>

    <div id="fruit_section">

    <label for="mango_id">Mango:</label>
    <input type="checkbox" name="fruit" id="mango_id" value="Mango">

    <label for="apple_id">Apple:</label>
    <input type="checkbox" name="fruit" id="apple_id" value="Apple"> Apple

    <label for="banana_id">Banana:</label>
    <input type="checkbox" name="fruit" id="banana_id" value="Banana"> Banana
    </div>

    <div id="car_section">
    <label for="cars">Choose a car:</label>
    <select name="cars" id="cars_id">
      <option value="" disabled selected>Select a car</option>
      <option value="volvo">Volvo</option>
      <option value="saab">Saab</option>
      <option value="fiat">Fiat</option>
      <option value="audi">Audi</option>
    </select>
    </div>

    <div id="textarea_section">
    <textarea name="message" id="message_id" rows="4" cols="50" placeholder="Enter your message here..." required></textarea>
    </div>

    <div id="file_upload_section">
    <label for="file_upload_id">Upload a file:</label>
    <input type="file" name="file_upload" id="file_upload_id" required>
    </div>

    <button type="submit">Submit Form</button>
</form>
</html>
```

To run this example, save it as an HTML file in `templates` folder and create a Flask application to handle the form submission. The content of the form can be accessed using the following code in Flask:

```python
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        data_fields = request.form.to_dict(flat=False)  # Get all text-based fields as a dictionary
        files = request.files  # Get uploaded files
        os.makedirs('uploads', exist_ok=True)  # Create uploads directory if it doesn't exist
        
        for file_key in files:
            file = files[file_key]
            file.save(os.path.join('uploads', secure_filename(file.filename)))  # Save uploaded files
        return str(data_fields)  # Return form data as string for demonstration
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
```

The folder structure should look like this:

```text
week4/
│├── app.py
│└── templates/
│    └── index.html
|-uploads/  # This folder will be created automatically by the program to store uploaded files
```

This python code sets up a Flask application that renders the HTML form and handles form submissions. When the form is submitted, it retrieves the form data and saves any uploaded files to an "uploads" directory. More about request object can be found in the next section.

## Summary

In this lesson, we explored HTML forms and their components, including various input types, the select tag, and the textarea tag. We learned how to create different types of input fields, such as text, email, password, radio buttons, checkboxes, and file uploads. We also discussed the attributes that enhance the functionality and usability of these form elements. Understanding HTML forms is essential for collecting user input and interacting with web applications effectively.

In the next lesson, we will learn how to handle form submissions and process the data on the server side using flask request object.

### Additional references

- [MDN Web Docs - HTML forms](https://developer.mozilla.org/en-US/docs/Learn/Forms)
- [MDN Web Docs - Input types](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input)
- [MDN Web Docs - Select element](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/select)
- [MDN Web Docs - Textarea element](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/textarea)
