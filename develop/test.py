# Imports from Jinja2
from jinja2 import Environment, FileSystemLoader
alert_receiver = []
alertmanager_file = '/Users/varun.tomar/Documents/personal_github/mauto/develop/config.yaml'
# with open(alertmanager_file + "-updated.yaml", "r") as asmr:
#   for line in asmr.readlines():
#     print("alert_receiver: ", alert_receiver)
#     if "ALERT_RECEIVERS ABOVE" in line:
#       alert_receiver += """{0}-team\n""".format('demo')
#       alert_receiver += line
#
# with open(alertmanager_file + "-updated.yaml", "w") as asmw:
#   asmw.writelines(alert_receiver)


env = Environment(loader=FileSystemLoader('/Users/varun.tomar/Documents/personal_github/mauto/develop/jinja_templates/templates'))
template = env.get_template('notification')


with open(alertmanager_file + "-updated.yaml", "r") as asmr:
  for line in asmr.readlines():
    if "ALERT_RECEIVERS ABOVE" in line:
      alert_receiver += (template.render(name='prj_name'))
      alert_receiver += line
print (alert_receiver)
with open(alertmanager_file + "-updated.yaml", "a") as asmw:
  asmw.writelines(alert_receiver)
