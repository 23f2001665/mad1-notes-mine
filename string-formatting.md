# String Formatting in Python

In python course, we have been introduced to various ways of string formatting like `f-strings`, `.format` method and `%` operator. Now we will shortly revist these concepts before moving to a few more advanced string templating tools like `string.Template` and `jinja2.Template`.

---

## % Operator (C-lang printf style)<a name="percent-operator"></a>

The `%` operator is an older method of string formatting in Python, similar to the `printf` style in C. It uses format specifiers to indicate where and how to format the values with strict type checking.

- `%s` - String (or any object with a string representation, like numbers)
- `%d` - Integers
- `%f` - Floating point numbers

``` python
name = "John"
age = 25
greeting = "Hello, my name is %s and I am %d years old." % (name, age)
print(greeting)
```

Output:

```txt
Hello, my name is John and I am 25 years old.
```

### pros:

- Safest among all the formatting methods, does not allow any code execution or object discovery.
- Supported in all Python versions.
- Simple and straightforward for basic formatting needs.

### cons:

- Less readable and more error-prone for complex formatting.
- Limited functionality compared to f-strings and `str.format()`.
- Mostly considered outdated and not recommended for new code.

---

## str.format() method (Python 2.7+) <a name="str-format-method"></a>

The `str.format()` method allows you to format strings by placing placeholders in the string and then calling the `format()` method with the values to replace those placeholders. `str.format()` replaces placeholders with values and allows **accessing object attributes** and **items**, but **<span style="color:yellow;">does not evaluate Python expressions.</span>**

``` python
name1 = "Bob"
age1 = 25

name2 = "Charlie"
age2 = 28

greeting = "Hello, my name is {name} and I am {age} years old."
greeting1 = greeting.format(name=name1, age=age1)
greeting2 = greeting.format(name=name2, age=age2)

print(greeting1)
print(greeting2)
```

Output:

```txt
Hello, my name is Bob and I am 25 years old.
Hello, my name is Charlie and I am 28 years old.
```

### pros

- More flexible than both printf-style formatting and f-strings.
- Allows accessing object attributes and items.
- Supports advanced formatting options.
- Safer than f-strings as it does not evaluate arbitrary expressions.
- Can be reused with different data.
- Available in all Python versions from 2.7 and 3.x.

### cons

- Slightly less readable than f-strings.
- More verbose syntax.
- Only allows basic substitutions.
- Not suitable for complex templating needs.
- Supports attributes and items, but not full expressions, which is safer than f-strings but still can be dangerous in certain contexts.
- **<span style="color:red;">Security risk if user input is involved in template itself.</span>**

---

## f-strings (Python 3.6+)  <a name="f-strings"></a>

f-strings or formatted string literals are a way to embed expressions inside string literals, using curly braces `{}`. They are prefixed with the letter `f` or `F`. f-strings allow for **<span style="color:red;">full expression evaluation</span>** inside the curly braces.

``` python
name = "Alice"
age = 30
greeting = f"Hello, my name is {name} and I am {age} years old."
print(greeting)
```

Output:

```txt
Hello, my name is Alice and I am 30 years old.
```

### pros

- More readable and concise.
- Supports advanced formatting options.
- Faster than both `%` operator and `str.format()` method.
- Allows embedding of **<span style="color:red;">any valid Python expression</span>** inside the curly braces.

### cons

- Only available in Python 3.6 and later.
- Not suitable for complex templating needs.
- Template and data live together
- Evaluated immediately
- Not reusable as a template
- **<span style="color:red;">Security risk if user input is directly embedded.</span>**

---

## Summary<a name="summary"></a>

| Feature                     | % Operator          | str.format()        | f-strings           |
|-----------------------------|---------------------|---------------------|---------------------|
| Python Version              | All versions        | 2.7+ and 3.x        | 3.6+                |
| Syntax                      | `%s`, `%d`, etc.    | `{}` placeholders   | `f"{}"` literals |
| Readability                 | Low                 | Moderate            | High                |
| Performance                 | Slowest             | Moderate            | Fastest             |
| Expression Evaluation       | No                  | Limited             | Yes(complete access)                 |
| Accessing Attributes/Items  | No                  | Yes                 | Yes                 |   
| Reusability                 | Yes                 | Yes                 | No                  |
| Security Risk with User Input| Negligible                 | Medium              | Very High                |
| Use case suitability        | legacy code     | Moderate formatting | Simple formatting |

---

::: tip

- **see comparision of string formatting methods in python** [here](https://realpython.com/python-string-formatting/#choosing-the-right-string-formatting-method)

- **see comparsion with templating tools** [here](./jinja2_cheatsheet.md#comparion)
:::

---

::: danger
**Security Warning:** Avoid using f-strings or `str.format()` with untrusted user input. Both `fstring` and `string.format` allows **dynamic expression evaluation** which can be exploited. Always sanitize and validate any user-provided data before embedding it in strings or simply use safer templating engines like [**string.Template**](./string-templating.md#stringtemplate) or [**jinja2.Template**](./jinja2_cheatsheet.md#jinja2-guide).<br>
:::

::: tip
for more information on security risks related to string formatting, refer to this article: [Python String Formatting Security Risks](https://www.geeksforgeeks.org/python/vulnerability-in-str-format-in-python/)

though there are more ways of string formatting in python like '%' operator, and more techniques related to `str.format()` method, we will not be covering them here. But you can refer to the official documentation for more details: [python official documentation](https://docs.python.org/3/library/string.html#formatstrings)
:::

---

