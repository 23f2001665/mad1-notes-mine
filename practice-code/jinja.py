# from jinja2 import Template

# gm_sentence = Template("""Good Morning {{ name }}.
# Hope you day goes well.""")

# output = gm_sentence.render(name="Himanshu")
# print(type(output), repr(output), output, sep='\n\n')


# l = ['apple', 'mango', 'guava']

# fruit_list_tmp = Template("""
# Here is a list of my favourite fruits:
# {% for item in fruit_list -%}
# {% if item[0] == 'a' %} {{item}} {% endif -%}
# {%- endfor %}
# """)

# print(fruit_list_tmp.render(fruit_list = l))

import sys

print(sys.argv)