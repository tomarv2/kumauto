from shutil import copyfile
import os
import sys
import fileinput
import re
import ruamel.yaml as yaml
import logging

import sys
sys.path.append("..")


logger = logging.getLogger(__name__)
from automation.core.base_function import *
from .git_push_prometheus import update_github_alertmanager


current_values_in_alertmanager = []


# -------------------------------------------------------------
#
# BUILD THE FILES OF ALERTMANAGER
#
# -------------------------------------------------------------
def build_alertmanager(user_input_env, project_name, alertmanager_config_file_path, modules, tools, email_to, slack_channel, pagerduty_service_key_id):
    alertmanager_fileloc = alertmanager_config_file_path
    try:
        if alertmanager_validate_current_setup(alertmanager_fileloc, project_name, user_input_env) == 0:
            logger.error('[alertmanager] configuring monitoring for: {}' .format(project_name))
            alertmanager_create_new_entry(alertmanager_fileloc, project_name, convert_list_to_str(modules), user_input_env,
                            convert_list_to_str(tools), convert_list_to_str(email_to), convert_list_to_slack_channel(slack_channel), pagerduty_service_key_id)
        else:
            logger.error("[alertmanager] config already exists. Updating contact information: %s", user_input_env)
            alertmanager_replace_existing_entry(alertmanager_fileloc, project_name, convert_list_to_str(tools),
                                                convert_list_to_str(email_to), user_input_env, slack_channel, pagerduty_service_key_id)
    except:
        logger.error("[alertmanager] unable to update/create config...")


# -------------------------------------------------------------
#
# CHECK WHETHER THE PROJECT ALREADY EXIST IN ALERTMANAGER CONFIG FILE
#
# -------------------------------------------------------------
def alertmanager_validate_current_setup(basefile_list, project_name, env):
    logger.debug("[alertmanager] validating if alert already exists for {} in config: {}" .format(project_name, basefile_list))
    try:
        with open(basefile_list, 'r') as stream:
            out = yaml.load(stream, Loader=yaml.Loader)
            print(out['route'])
            try:
                logger.error("[alertmanager] getting list of currently monitored projects...")
                current_values_in_alertmanager.append(out['route']['routes'])
            except BaseException:
                logger.error("[alertmanager] unable to get list of currently monitored projects, exiting...")
                raise SystemExit
    except:
        logger.error("[alertmanager] unable to parse: %s", basefile_list)
    values = []
    try:
        for i in [x for x in current_values_in_alertmanager]:
            for j in i:
                values.append(j)
    except:
        logger.error("[alertmanager] no project config exists...")
        pass
    try:
        logger.error("[alertmanager] verifying if project already exists...")
        if project_name in (str(values)):
            logger.error("[alertmanager] monitoring already exists for: %s", project_name)
            return 1
        else:
            logger.error("[alertmanager] monitoring does not exist for: %s", project_name)
            return 0
    except:
        logger.error("[alertmanager] no matching project found...")
        pass


# -------------------------------------------------------------
#
# ADD THE NEW PROJECT IN ALERTMANAGER CONFIG FILE
#
# -------------------------------------------------------------
def alertmanager_create_new_entry(alertmanager_file, prj_name, modules, env, tools, to_email_list, slack_channel, pagerduty_service_key_id):
    print("inside alertmanager_create_new_entry")
    if 'alertmanager' in tools:
        logger.debug("[alertmanager] to_email_list: {}" .format(to_email_list))
        logger.debug("[alertmanager] taking backup of file...")
        logger.debug("[alertmanager] file name: {}" .format(alertmanager_file))
        copyfile(alertmanager_file, alertmanager_file + '.bak')
        logger.debug("[alertmanager] updating alert rules section...")
        if 'qa' in env:
            nonprod_alertmanager(alertmanager_file, prj_name, modules, env, to_email_list, slack_channel)
        else:
            prod_alertmanager(alertmanager_file, prj_name, modules, env, to_email_list, slack_channel, pagerduty_service_key_id)


def nonprod_alertmanager(alertmanager_file, prj_name, modules, env, to_email_list, slack_channel):
    alert_route = []
    alert_receiver = []
    with open(alertmanager_file, "r") as asmr:
        for line in asmr.readlines():
            if "ALERT_ROUTES ABOVE" in line:
                # we have a match,we want something but we before that...
                alert_route += '''
  - receiver: '{0}-team'
    match:
      service: {0}-{1}\n'''.format(prj_name, modules)
            alert_route += line
    with open(alertmanager_file + "-updated.yaml", "w") as asmw:
        asmw.writelines(alert_route)
    # os.rename(alertmanager_file + "-updated.yaml", alertmanager_file)
    logger.error("[alertmanager] updating alert receivers section...")
    with open(alertmanager_file + "-updated.yaml", "r") as asmr:
        for line in asmr.readlines():
            if "ALERT_RECEIVERS ABOVE" in line:
                # we have a match,we want something but we before that...
                alert_receiver += """
################# START JOB #########################
- name: '{0}-team'
  email_configs:
  - send_resolved: true
    to: '{2}' # DO NOT REMOVE TAG: {0}-team
    from: {1}-prometheus@demo.com
    smarthost: outmail.demo.com:25
    headers:
      From: {1}-prometheus@demo.com
      Subject: '{{{3} template "email.default.subject" . {4}}}'
      To: '{2}' # DO NOT REMOVE TAG: {0}-team
    html: '{{{3} template "email.default.html" . {4}}}'
    require_tls: false
  slack_configs:
  - send_resolved: true
    api_url: https://hooks.slack.com/services/T12345/B12345
    channel: {5} # DO NOT REMOVE TAG: {0}-team
################### END JOB #########################\n""".format(prj_name, env, to_email_list, '{', '}', slack_channel)
            alert_receiver += line
    # write the file with the new content
    with open(alertmanager_file + "-updated.yaml", "w") as asmw:
        asmw.writelines(alert_receiver)


def prod_alertmanager(alertmanager_file, prj_name, modules, env, to_email_list, slack_channel, pagerduty_service_key_id):
    alert_route = []
    alert_receiver = []
    with open(alertmanager_file, "r") as asmr:
        for line in asmr.readlines():
            if "ALERT_ROUTES ABOVE" in line:
                # we have a match,we want something but we before that...
                alert_route += '''
  - receiver: '{0}-team'
    match:
      service: {0}-{1}\n'''.format(prj_name, modules)
            alert_route += line
    with open(alertmanager_file + "-updated.yaml", "w") as asmw:
        asmw.writelines(alert_route)
    # os.rename(alertmanager_file + "-updated.yaml", alertmanager_file)
    logger.error("[alertmanager] updating alert receivers section...")
    with open(alertmanager_file + "-updated.yaml", "r") as asmr:
        for line in asmr.readlines():
            if "ALERT_RECEIVERS ABOVE" in line:
                # we have a match,we want something but we before that...
                alert_receiver += """
################# START JOB #########################
- name: '{0}-team'
  email_configs:
  - send_resolved: true
    to: '{2}' # DO NOT REMOVE TAG: {0}-team
    from: {1}-prometheus@demo.com
    smarthost: outmail.demo.com:25
    headers:
      From: {1}-prometheus@demo.com
      Subject: '{{{3} template "email.default.subject" . {4}}}'
      To: '{2}' # DO NOT REMOVE TAG: {0}-team
    html: '{{{3} template "email.default.html" . {4}}}'
    require_tls: false
  pagerduty_configs:
  - send_resolved: true
    service_key: {6} # DO NOT REMOVE TAG: {0}-team
    url: https://events.pagerduty.com/v2/enqueue
    client: '{{{3} template "pagerduty.default.client" . {4}}}'
    client_url: '{{{3} template "pagerduty.default.clientURL" . {4}}}'
    description: '{{{3}template "pagerduty.default.description" .{4}}}'
  slack_configs:
  - send_resolved: true
    api_url: https://hooks.slack.com/services/T2BT338U9/B12345
    channel: {5} # DO NOT REMOVE TAG: {0}-team
################### END JOB #########################\n""".format(prj_name, env, to_email_list, '{', '}', slack_channel, pagerduty_service_key_id)
            alert_receiver += line
    # write the file with the new content
    with open(alertmanager_file + "-updated.yaml", "w") as asmw:
        asmw.writelines(alert_receiver)


# -------------------------------------------------------------
#
# UPDATE THE PROJECT INFORMATION IN ALERTMANAGER CONFIG FILE
#
# -------------------------------------------------------------
def alertmanager_replace_existing_entry(alertmanager_file, prj_name, tools, to_email_list, env, slack_channel, pagerduty_service_key_id):
    logger.debug("[alertmanager] file location: %s", alertmanager_file)
    logger.debug("[alertmanager] project name: %s", prj_name)
    logger.debug("[alertmanager] to_email_list: %s", to_email_list)
    logger.debug("[alertmanager] env: %s", env)
    tag = "# DO NOT REMOVE TAG: " + prj_name + '-' + 'team'
    final_to_email_list = to_email_list + ' ' + tag
    logger.debug("[alertmanager] new email_to entries: %s", final_to_email_list)
    try:
        logger.debug("[alertmanager] backing up alertmanager.yaml file: %s", alertmanager_file)
        copyfile(alertmanager_file, alertmanager_file + '.bak')
    except BaseException:
        logger.error("[alertmanager] unable to backup file..")
        pass
    to_email_list_new = "'" + to_email_list + "'"
    logger.debug("tag: %s", tag)
    logger.debug("final_line: %s", final_to_email_list)
    if 'alertmanager' in tools:
        logger.error("[alertmanager] trying to update alertmanager config.yaml file..")
        copyfile(alertmanager_file, alertmanager_file + "-updated.yaml")
        for line in fileinput.input([alertmanager_file + "-updated.yaml"], inplace=True):
            try:
                if line.strip().endswith(tag):
                    if 'service_key' in line:
                        new_service_key = 'service_key: ' + pagerduty_service_key_id + ' ' + tag
                        line = re.sub(r"service_key:\s(.*)", new_service_key, line)
                sys.stdout.write(line)
            except BaseException:
                raise SystemExit
        for line in fileinput.input([alertmanager_file + "-updated.yaml"], inplace=True):
            try:
                if line.strip().endswith(tag):
                    if 'channel' in line:
                        if tag not in line:
                            new_slack_channel = 'channel: ' + slack_channel + ' ' + tag
                            line = re.sub(r"channel:\s(.*)", new_slack_channel, line)
                sys.stdout.write(line)
            except BaseException:
                raise SystemExit
        for line in fileinput.input([alertmanager_file + "-updated.yaml"], inplace=True):
            try:
                if line.strip().endswith(tag):
                    if 'to:' or 'To:' in line:
                        line = re.sub(r'\'.*\'', to_email_list_new, line)
                sys.stdout.write(line)
            except BaseException:
                raise SystemExit


# -------------------------------------------------------------
#
# APPLY CHANGES TO NFS/EFS AND GITHUB FOR ALERTMANAGER
#
# -------------------------------------------------------------
def update_alertmanager(env, project_name, alertmanager_config_file_path):
    try:
        logger.error("[alertmanager] updating repo...")
        update_alertmanager_config(alertmanager_config_file_path)
        update_github_alertmanager(alertmanager_config_file_path, project_name, env)
    except BaseException:
        logger.error("[prometheus] failed to update alertmanager config...")


def update_alertmanager_config(alertmanager_file):
    if os.path.exists(alertmanager_file + "-updated.yaml"):
        try:
            logger.error("renaming  %s to  %s ", alertmanager_file + "-updated.yaml", alertmanager_file)
            os.rename(alertmanager_file + "-updated.yaml", alertmanager_file)
        except BaseException:
            logger.error("[alertmanager] failed to apply change on config.yaml...")


