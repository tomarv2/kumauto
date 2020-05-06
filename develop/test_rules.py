from jinja2 import Environment, FileSystemLoader

rules_receiver = []
alertmanager_file = '/Users/varun.tomar/Documents/personal_github/mauto/develop/config1.yaml'
template_dir = '/Users/varun.tomar/Documents/personal_github/mauto/src/automation/templates'
template_name = 'prometheus_config'


jinja_env = Environment(loader=FileSystemLoader(template_dir))
try:
    template = jinja_env.get_template(template_name)
except:
    print("failed")


with open(alertmanager_file + "-updated.yaml", "r") as asmr:
    for line in asmr.readlines():
        if "PROMETHEUS JOB SECTION ABOVE" in line:
            rules_receiver += (template.render(name='prj_name', env='test'))
            rules_receiver += line

print(''.join(rules_receiver))
# with open(alertmanager_file + "-updated.yaml", "a") as asmw:
#   asmw.writelines(rules_receiver)
