# Imports from Jinja2
from jinja2 import Environment, FileSystemLoader

# # Load Jinja2 template
# env = Environment(loader=FileSystemLoader('/Users/varun.tomar/Documents/personal_github/mauto/develop/jinja_templates/templates'))
#
# template = env.get_template('test')
#
# # Render template using data and print the output
# print(template.render(name="Frank", email_to='test'))

with open(alertmanager_file + "-updated.yaml", "r") as asmr:
  for line in asmr.readlines():
    if "ALERT_RECEIVERS ABOVE" in line:
      # Render template using data and print the output
      alert_receiver += (
        template.render(name=prj_name, env=env, email_to=to_email_list, smarthost_details='smtp.gmail.com:587',
                        slack_channel=slack_channel,
                        slack_api_url='https://hooks.slack.com/services/T12345/T12345/T12345',
                        pagerduty_service_key=pagerduty_service_key_id)).format(prj_name, env, to_email_list,
                                                                                slack_channel, pagerduty_service_key_id)
      alert_receiver += line
# write the file with the new content
with open(alertmanager_file + "-updated.yaml", "w") as asmw:
  asmw.writelines(alert_receiver)