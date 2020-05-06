# Imports from Jinja2
from jinja2 import Environment, FileSystemLoader

alertmanager_file = '/Users/varun.tomar/Documents/personal_github/mauto/develop/config1.yaml'
template_dir = '/Users/varun.tomar/Documents/personal_github/mauto/develop/jinja_templates/templates'
template_name = 'route'

env = Environment(loader=FileSystemLoader(template_dir))
template = env.get_template(template_name)

template_rendered = (template.render(name='prj_name'))


def test():
  alert_receiver = []
  with open(alertmanager_file, "r") as asmr:
    for line in asmr.readlines():
      if "ALERT_ROUTES ABOVE" in line:
        alert_receiver += '''
  - receiver: 'aws-testrepo-service-team'
    match:
      service: {{ name }}-blackbox\n''' .format(template_rendered)
      alert_receiver += line

  print("alert_receiver:\n", ''.join(alert_receiver))
  # with open(alertmanager_file + "-updated.yaml", "a") as asmw:
  #   asmw.writelines(alert_receiver)


test()
