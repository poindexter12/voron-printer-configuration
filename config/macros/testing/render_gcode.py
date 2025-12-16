from jinja2 import Environment

# Klipper uses a custom Jinja2 environment with single braces for expressions
# See: https://www.klipper3d.org/Command_Templates.html
KLIPPER_ENV = Environment('{%', '%}', '{', '}')

# Example macro template using Klipper syntax (can be loaded from a file)
macro = """
{% set temp = params.TEMP|default(215)|int %}
{% set feed = 60 * temp %}
RESPOND PREFIX="DEBUG" MSG="temp={ temp } feed={ feed }"
M104 S{ temp }
G1 X50 Y50 F{ feed }
"""

# Example parameters (can be extended to parse CLI args)
params = {"TEMP": 220}

template = KLIPPER_ENV.from_string(macro)
output = template.render(params=params)
print(output)
