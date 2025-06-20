# gen.py
try:
    import yaml
    import jinja2
except ImportError as e:
    print("Missing dependency:", e.name)
    print("Install with: pip3 install -r requirements.txt")
    exit(1)

from jinja2 import Environment, FileSystemLoader

# Load data from YAML
with open('stepper_settings.cfg.yaml') as f:
    data = yaml.safe_load(f)

# Set up Jinja2 environment
env = Environment(
    loader=FileSystemLoader('.'),
    trim_blocks=True,
    lstrip_blocks=True
)
template = env.get_template('stepper_settings.cfg.j2')

# Render template with loaded data
rendered = template.render(common=data['common'], axes=data['axes'])

# Write out the generated config
with open('stepper_settings.cfg', 'w') as f:
    f.write(rendered)

print("Generated stepper_settings.cfg")