# Imports from Jinja2
from jinja2 import Environment, FileSystemLoader

alertmanager_file = '/Users/varun.tomar/Documents/personal_github/mauto/develop/config1.yaml'
template_dir = '/Users/varun.tomar/Documents/personal_github/mauto/develop/jinja_templates/templates'
template_name = 'route'


def setup_new_alertmanager(alertmanager_file,
                           prj_name,
                           modules):
  alert_route = []
  with open(alertmanager_file, "r") as asmr:
    for line in asmr.readlines():
      if "ALERT_ROUTES ABOVE" in line:
        # we have a match,we want something but we before that...
        alert_route += '''
  - receiver: '{0}-team'
    match:
      service: {0}-{1}\n'''.format('prj_name', 'modules')
      alert_route += line
  print("alert_route:\n", ''.join(alert_route))
  # with open(alertmanager_file + "-updated.yaml", "w") as asmw:
  #   asmw.writelines(alert_route)


setup_new_alertmanager(alertmanager_file, 'test', 'dev')
