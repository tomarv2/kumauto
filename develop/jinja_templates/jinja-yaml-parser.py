# Imports from Jinja2
from jinja2 import Environment, FileSystemLoader

# Import YAML from PyYAML
import ruamel.yaml as yaml

# Load data from YAML file into Python dictionary
config = yaml.load(open('/Users/varun.tomar/Documents/personal_github/mauto/develop/jinja_templates/data.yaml'))

# Load Jinja2 template
env = Environment(loader=FileSystemLoader('/Users/varun.tomar/Documents/personal_github/mauto/src/automation/templates'), trim_blocks=True, lstrip_blocks=True)

template = env.get_template('am_reciever_notifcation')

# Render template using data and print the output
print(template.render(config))

