# string.Template <a name="stringtemplate"></a>

The `string.Template` class is part of Python's standard library `string` provides a way to create simple string templates with placeholders that can be replaced with actual values. It uses `$` or `${}` to denote placeholders. It is designed for simpler use cases and is **safer for user input** as it does not allow arbitrary code execution or object discovery.

We have to use the `Template` class from the `string` module to create a template object. We can then use the `substitute()` or `safe_substitute()` methods to replace the placeholders with actual values.

## Example

``` python
from string import Template
template = Template("Hello, my name is $name and I am ${my_age} years old.")

greeting1 = template.substitute(name="David", my_age=35)
greeting2 = template.substitute(name="Eva", my_age=29)

print(greeting1)
print(greeting2)
```

Output:

```txt
Hello, my name is David and I am 35 years old.
Hello, my name is Eva and I am 29 years old.
```

:::tip

## Try it yourself

copy the following code and paste it into a python file, then run it to see the output

``` python
from string import Template
template = Template("Welcome, $user! Your score is $score.")
result = template.substitute(user="Player1", score=1500)
print(result)
```

:::

## pros

- Simple and easy to use for basic templating needs.
- Template and data are separated.
- Available in all Python versions from 2.4 and 3.x.
- Safe for user input as it does not allow arbitrary code execution.

## cons

- Less flexible than f-strings and `str.format()`.
- Does not support complex expressions or formatting.
- Limited functionality compared to more advanced templating engines.
- Only supports basic placeholder substitution.
- Not suitable for complex templating needs.

## Placeholder Syntax

::: info

- `$identifier`: Simple placeholder.
- `${complex_identifier}`: Placeholder with braces for clarity or complex names(with underscores).
- `$$`: Literal dollar sign.

:::

### Example

``` python
from string import Template
template1 = Template("Total cost is $amount.")
template2 = Template("Your balance is ${my_balance} USD.")
template3 = Template("This costs $$5.")
result1 = template1.substitute(amount=100)
result2 = template2.substitute(my_balance=250)
result3 = template3.substitute()
print(result1)
print(result2)
print(result3)

```

Output:

```txt
Total cost is 100.
Your balance is 250 USD.
This costs $5.
```

---

## substitute() vs safe_substitute()

- `substitute()`: Raises a `KeyError` if any placeholders are missing in the provided data.
- `safe_substitute()`: Leaves placeholders unchanged if they are missing, avoiding exceptions.

### Example

``` python
from string import Template
template = Template("Hello, $name! Welcome to $place.")
result1 = template.safe_substitute(name="Alice")
result2 = template.substitute(name="Alice")
print(result1)
print(result2)
```

Output:

```txt
Hello, Alice! Welcome to $place.
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
KeyError: 'place'
```

KeyError is raised in the second case because `place` is not provided but safe_substitute handles it gracefully returning the placeholder as is.

:::tip

### Try it yourself

copy the following code and paste it into a python file, then run it to see the output

``` python
from string import Template
template = Template("Dear $customer, your order #$order_id is confirmed.")
result1 = template.safe_substitute(customer="John", order_id=12345)
result2 = template.substitute(customer="John")
print(result1)
print(result2)
```

:::

---

## When to Use string.Template

- When you need a simple and safe templating solution without complex formatting.
- When working with user-generated templates where security is a concern.
- When you want to separate template logic from data without advanced features.
- When compatibility with older Python versions (2.4 and above) is required.
- When you want to avoid the complexity of `f-strings` or `str.format()` for basic use cases.

---

:::tip

For more complex templating needs, consider using advanced templating engines like Jinja2 which provide more features and flexibility.

For extra details, refer to the [official documentation](https://docs.python.org/3/library/string.html#template-strings-strings)

You can also check out the t-string introduced in python 3.14 for enhanced string templating capabilities [t-strings](https://realpython.com/python-t-strings/).
:::
