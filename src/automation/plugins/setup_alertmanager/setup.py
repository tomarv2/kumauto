from shutil import copyfile
import logging
import sys
import fileinput
import re
import ruamel.yaml as yaml
from automation.base.base_function import *
from .git_push import update_github_alertmanager
from jinja2 import Environment, FileSystemLoader
from .config import (
    TEMPLATES_DIRECTORY,
    RECIEVER_NOTIFICATION,
    ROUTE_NOTIFICATION
)

logger = logging.getLogger(__name__)
current_values_in_alertmanager = []


# -------------------------------------------------------------
#
# BUILD THE FILES FOR ALERTMANAGER
#
# -------------------------------------------------------------
def build_alertmanager(user_input_env,
                       project_name,
                       alertmanager_config_file_path,
                       modules,
                       tools,
                       email_to,
                       slack_channel,
                       pagerduty_service_key_id):
    logger.debug("inside build_alertmanager function")
    alertmanager_fileloc = alertmanager_config_file_path
    try:
        logger.info('[alertmanager] configuring monitoring: {}'.format(project_name))
        if alertmanager_validate_current_setup(alertmanager_fileloc, project_name, user_input_env) == 0:
            logger.info('[alertmanager] configuring monitoring for: {}' .format(project_name))
            alertmanager_create_new_entry(alertmanager_fileloc,
                                          project_name,
                                          convert_list_to_str(modules),
                                          user_input_env,
                                          convert_list_to_str(tools),
                                          convert_list_to_str(email_to),
                                          convert_list_to_slack_channel(slack_channel),
                                          pagerduty_service_key_id)
        else:
            logger.info("[alertmanager] config already exists, updating contact information: {}" .format(user_input_env))
            alertmanager_replace_existing_entry(alertmanager_fileloc,
                                                project_name,
                                                convert_list_to_str(tools),
                                                convert_list_to_str(email_to),
                                                user_input_env,
                                                slack_channel,
                                                pagerduty_service_key_id)
    except:
        logger.error("[alertmanager] unable to update/create config")


# -------------------------------------------------------------
#
# CHECK WHETHER THE PROJECT ALREADY EXIST IN ALERTMANAGER CONFIG FILE
#
# -------------------------------------------------------------
def alertmanager_validate_current_setup(basefile_list, project_name, env):
    logger.debug("[alertmanager] validating if alert already exists for [{}] in config [{}]" .format(project_name, basefile_list))
    try:
        with open(basefile_list, 'r') as stream:
            logger.debug("loading the yaml")
            out = yaml.load(stream, Loader=yaml.Loader)
            print(out['route'])
            try:
                logger.debug("[alertmanager] getting list of currently monitored projects")
                current_values_in_alertmanager.append(out['route']['routes'])
            except BaseException:
                logger.error("[alertmanager] unable to get list of currently monitored projects, exiting")
                raise SystemExit
    except:
        logger.error("[alertmanager] file does not exist or unable to parse: {}" .format(basefile_list))
    values = []
    try:
        for i in [x for x in current_values_in_alertmanager]:
            for j in i:
                values.append(j)
    except:
        logger.debug("[alertmanager] no project config exists")
        pass
    try:
        logger.info("[alertmanager] verifying if project already exists")
        if project_name in (str(values)):
            logger.info("[alertmanager] monitoring already exists for: {}" .format(project_name))
            return 1
        else:
            logger.info("[alertmanager] monitoring does not exist for: {}" .format(project_name))
            return 0
    except:
        logger.debug("[alertmanager] no matching project found")
        pass


# -------------------------------------------------------------
#
# ADD THE NEW PROJECT IN ALERTMANAGER CONFIG FILE
#
# -------------------------------------------------------------
def alertmanager_create_new_entry(alertmanager_file,
                                  prj_name,
                                  modules,
                                  env,
                                  tools,
                                  to_email_list,
                                  slack_channel,
                                  pagerduty_service_key_id):
    logger.debug("inside [alertmanager_create_new_entry function]")
    if 'alertmanager' in tools:
        logger.debug("[alertmanager] to_email_list: {}" .format(to_email_list))
        logger.debug("[alertmanager] taking backup of file")
        logger.debug("[alertmanager] file name: [{}]" .format(alertmanager_file))
        copyfile(alertmanager_file, alertmanager_file + '.bak')
        logger.debug("[alertmanager] updating alert rules section")
        # if 'aws' in env:
        setup_new_alertmanager(alertmanager_file,
                          prj_name,
                          modules,
                          env,
                          to_email_list,
                          slack_channel,
                          pagerduty_service_key_id)


def setup_new_alertmanager(alertmanager_file,
                      prj_name,
                      modules,
                      env,
                      to_email_list,
                      slack_channel,
                      pagerduty_service_key_id):
    logger.debug("[alertmanager] inside setup_new_alertmanager")
    alert_route = []
    alert_receiver = []
    #
    # Load Jinja2 template
    #
    jinja_env = Environment(loader=FileSystemLoader(TEMPLATES_DIRECTORY))
    logger.debug("[alertmanager] template dir: {}" .format(TEMPLATES_DIRECTORY))
    template = jinja_env.get_template(ROUTE_NOTIFICATION)  # 'am_route_notification')
    try:
        logger.debug("[alertmanager] opening file")
        with open(alertmanager_file, "r") as asmr:
            for line in asmr.readlines():
                if "ALERT_ROUTES ABOVE" in line:
                    try:
                        alert_route += (template.render(name=prj_name, module=modules))
                    except:
                        logger.debug("unable to render")
                alert_route += line
    except:
        logger.error("unable to open file")
    #
    # write the file
    #
    logger.debug("[alertmanager] writing to file {}" .format(alertmanager_file + "-updated.yaml"))
    with open(alertmanager_file + "-updated.yaml", "w") as asmw:
        asmw.writelines(alert_route)
    # os.rename(alertmanager_file + "-updated.yaml", alertmanager_file)
    logger.debug("[alertmanager] updating alert receivers section")
    #
    # Load Jinja2 template
    #
    jinja_env = Environment(loader=FileSystemLoader(TEMPLATES_DIRECTORY))
    reciever_template = jinja_env.get_template(RECIEVER_NOTIFICATION) #'am_reciever_notification')
    try:
        with open(alertmanager_file + "-updated.yaml", "r") as asmr:
            logger.debug("[alertmanager] inside file: {}" .format(alertmanager_file + "-updated.yaml"))
            for line in asmr.readlines():
                if "ALERT_RECEIVERS ABOVE" in line:
                    try:
                        logger.debug("rendering template")
                        #
                        # render template using data
                        #
                        logger.debug("checking output: {}\n{}\n{}\n{}\n{}" .format(prj_name,
                                                    env,
                                                    to_email_list,
                                                    'slack_channel',
                                                    pagerduty_service_key_id))
                        alert_receiver += (reciever_template.render(name=prj_name,
                                                                    env=env,
                                                                    email_to=to_email_list,
                                                                    smarthost_details='smtp.gmail.com:587',
                                                                    slack_channel=slack_channel,
                                                                    slack_api_url='https://hooks.slack.com/services/T12345',
                                                                    pagerduty_service_key=pagerduty_service_key_id
                                                                    ))
                    except:
                        logger.debug("issue rendering template")
                alert_receiver += line
    except:
        logger.error("unable to open file: {}" .format(alertmanager_file + '-updated.yaml'))
    #
    # write the file with the new content
    #
    logger.debug("[alertmanager] printing file {}" .format(''.join(alert_receiver)))
    with open(alertmanager_file + "-updated.yaml", "w") as asmw:
        asmw.writelines(alert_receiver)


# -------------------------------------------------------------
#
# UPDATE THE PROJECT INFORMATION IN ALERTMANAGER CONFIG FILE
#
# -------------------------------------------------------------
def alertmanager_replace_existing_entry(alertmanager_file,
                                        prj_name,
                                        tools,
                                        to_email_list,
                                        env,
                                        slack_channel,
                                        pagerduty_service_key_id):
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
        logger.debug("[alertmanager] trying to update alertmanager config.yaml file")
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
        update_alertmanager_config(alertmanager_config_file_path)
        update_github_alertmanager(alertmanager_config_file_path, project_name, env)
    except BaseException:
        logger.error("[alertmanager] failed to update alertmanager config")


def update_alertmanager_config(alertmanager_file):
    logger.debug("[alertmanager] updating config")
    if os.path.exists(alertmanager_file + "-updated.yaml"):
        try:
            logger.debug("renaming [{}] to [{}]" .format(alertmanager_file + "-updated.yaml", alertmanager_file))
            os.rename(alertmanager_file + "-updated.yaml", alertmanager_file)
        except BaseException:
            logger.error("[alertmanager] failed to apply change on config.yaml")


