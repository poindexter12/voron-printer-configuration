from jinja2 import Template

# Example macro template (can be loaded from a file)
macro = """
{% set temp = params.TEMP|default(215)|int %}
{% set feed = 60 * temp %}
RESPOND PREFIX="DEBUG" MSG="temp={{ temp }} feed={{ feed }}"
M104 S{{ temp }}
G1 X50 Y50 F{{ feed }}
"""

# Example parameters (can be extended to parse CLI args)
params = {"TEMP": 220}

template = Template(macro)
output = template.render(params=params)
print(output)
