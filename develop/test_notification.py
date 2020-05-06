# Imports from Jinja2
from jinja2 import Environment, FileSystemLoader

alert_receiver = []
alertmanager_file = '/Users/varun.tomar/Documents/personal_github/mauto/develop/config1.yaml'
template_dir = '/Users/varun.tomar/Documents/personal_github/mauto/src/automation/templates'
template_name = 'am_reciever_notification'

env = Environment(loader=FileSystemLoader(template_dir))
template = env.get_template(template_name)

with open(alertmanager_file + "-updated.yaml", "r") as asmr:
  for line in asmr.readlines():
    if "ALERT_RECEIVERS ABOVE" in line:
      alert_receiver += (template.render(name='prj_name'))
      alert_receiver += line
    print('not found')

print(alert_receiver)
with open(alertmanager_file + "-updated.yaml", "a") as asmw:
  asmw.writelines(alert_receiver)
