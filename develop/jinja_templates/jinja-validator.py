# Imports from Jinja2
from jinja2 import Environment, FileSystemLoader

# Import YAML from PyYAML
import ruamel.yaml as yaml

# Load data from YAML file into Python dictionary
config = yaml.load(open('/Users/varun.tomar/Documents/personal_github/mauto/develop/jinja_templates/data.yaml'))

# Load Jinja2 template
#env = Environment(loader=FileSystemLoader('/Users/varun.tomar/Documents/personal_github/mauto/develop/jinja_templates/templates'), trim_blocks=True, lstrip_blocks=True)

env = Environment(loader=FileSystemLoader('/Users/varun.tomar/Documents/personal_github/mauto/develop/jinja_templates/templates'))

#    jinja2_env = jinja2.Environment(loader=jinja2.FileSystemLoader(tmpl_path))

template = env.get_template('junk')

# Render template using data and print the output
print(template.render(config))

print t.render(username="Frank")
