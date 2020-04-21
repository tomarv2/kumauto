import shutil
from shutil import copyfile
import os
import yaml

import sys
sys.path.append("..")


from core.logging_function import logger
from core.base_function import *
from .git_push_elastalert import update_github_elastalert


current_list_of_projects = []
current_values_in_elastalert_rules = []

config_yaml = '/automation/config.yaml'  


# ----------------------------------------------
#
# BUILD THE FILES OF ELASTALERT
#
# ----------------------------------------------
def build_elastalert(user_input_env, project_name, elastalert_rules_dir, namespace, ea_query, elastalert_sample_file,
                     elasticsearch_hostname, email_to, pagerduty_service_key_id, pagerduty_client_name):
    logger.info("=" * 75)
    logger.info('elastalert: updating config for: %s', project_name)
    try:
        logger.debug("-" * 75)
        logger.debug("elastalert: rules_dir: %s", elastalert_rules_dir)
        logger.debug("elastalert: sample_file: %s", elastalert_sample_file)
        logger.debug("elastalert: project_name: %s", project_name)
        logger.debug("elastalert: get_index_name: %s", get_index_name(project_name, namespace))
        logger.debug("elastalert: ea_query: %s", convert_list_to_ea_query(ea_query))
        logger.debug("elastalert: alert type: %s", get_alert_type(user_input_env))
        logger.debug("elastalert: email_to list: %s", convert_list_to_str(email_to))
        logger.debug("elastalert: pagerduty_service_key_id: %s", pagerduty_service_key_id)
        logger.debug("elastalert: pagerduty_client_name: %s", pagerduty_client_name)
        logger.debug("elastalert: application_type: %s", get_application_type(project_name))
        logger.debug("-" * 75)
        elastalert_rules_setup(elastalert_rules_dir, elastalert_sample_file, project_name,
                            get_index_name(project_name, namespace), convert_list_to_ea_query(ea_query),
                            get_alert_type(user_input_env), convert_list_to_str(email_to),
                            pagerduty_service_key_id, pagerduty_client_name,
                            user_input_env, get_application_type(project_name), elasticsearch_hostname )
    except BaseException:
        logger.error("elastalert: unable to setup config...")


# --------------------------------------------------------
#
# ADD THE NEW ELASTALERT RULES
#
# --------------------------------------------------------
def elastalert_rules_setup(elastalert_rules_dir, sample_file, project_name, index, ea_query, alert_type, email_to,
                     pagerduty_service_key_id, pagerduty_client_name, env, application, elasticsearch_hostname):
    logger.info("=" * 75)
    logger.info("In elastalert_rules function...")
    logger.debug("elastalert: rules_dir: %s", elastalert_rules_dir)
    logger.debug("elastalert: sample_file: %s", sample_file)
    logger.debug("elastalert: project_name: %s", project_name)
    logger.debug("elastalert: index: %s", index)
    logger.debug("elastalert: ea_query: %s", ea_query)
    logger.debug("elastalert: pagerduty service key: %s", pagerduty_service_key_id)
    logger.debug("elastalert: pagerduty client name: %s", pagerduty_client_name)
    logger.debug("elastalert: alert_type: %s", alert_type)
    logger.debug("elastalert: email_to: %s", email_to)
    logger.debug("elastalert: env: %s", env)
    logger.debug("elastalert: application: %s", application)
    logger.debug("elastalert: taking backup of file...")
    with open(config_yaml, 'r') as stream_config:
        out_config = yaml.load(stream_config)
        temporary_ea_rules = out_config['elastalert']['temporary_ea_rules'][0]
    ea_rules_file = os.path.join(temporary_ea_rules, env, project_name + '.yaml')
    logger.debug("elastalert: ea rules file location: %s", ea_rules_file)
    try:
        ensure_dir_exists(os.path.join(temporary_ea_rules, env))
        ensure_dir_exists(os.path.join(elastalert_rules_dir, env))
        logger.info("elastalert: copying sample file...")
        copyfile(sample_file, ea_rules_file)
    except BaseException:
        logger.warning("elastalert: file already exists (deleting and copying sample file)...")
        shutil.rmtree(ea_rules_file)
        copyfile(sample_file, ea_rules_file)
    logger.info("elastalert: updating elastalert rules section...")
    elastalert_rules = []
    if env in ['aws-qa', 'aws-stg']:
        with open(sample_file, "r") as asmr:
            for line in asmr.readlines():
                if "ELASTALERT RULES GO ABOVE" in line:
                    # we have a match,we want something but we before that...
                    elastalert_rules += '''es_host: {0}
es_port: 9200
name: {1}
type: any
index: {2}
num_events: 1
filter:
- query:
    query_string:
      query: {3}
alert:
- "{4}"
email:
 - "{5}"
alert_subject:  "{6} Project: {8} Type:Application({7})"\n'''. format(elasticsearch_hostname, env + '-' + project_name, index, ea_query,
                                                                            alert_type, email_to, env.upper(),
                                                                            application, project_name)
                elastalert_rules += line
        with open(ea_rules_file, "w") as asmw:
            asmw.writelines(elastalert_rules)

    else:
        with open(sample_file, "r") as asmr:
            for line in asmr.readlines():
                if "ELASTALERT RULES GO ABOVE" in line:
                    # we have a match,we want something but we before that...
                    elastalert_rules += '''es_host: {0}
es_port: 9200
name: {1}
type: any
index: {2}
num_events: 1
filter:
- query:
    query_string:
      query: {3}
alert:
- "{4}"
alert_subject:  "{7} - Pipeline: {9} - Type: Application({8})"
pagerduty_service_key: {5}
pagerduty_client_name: {6}\n'''. format(elasticsearch_hostname, env + '-' + project_name, index, ea_query,
                                        alert_type, pagerduty_service_key_id, pagerduty_client_name, env.upper(),
                                        application, project_name)
                elastalert_rules += line
        with open(ea_rules_file, "w") as asmw:
            asmw.writelines(elastalert_rules)
    logger.info('-' * 75)


# -------------------------------------------------------
#
# APPLY CHANGES TO NFS/EFS AND GITHUB FOR  ELASTALERT
#
# -------------------------------------------------------
def update_elastalert(env, project_name, elastalert_rules_dir):
    logger.info("=" * 75)
    try:
        update_elastalert_rules_dir(elastalert_rules_dir, env)
        logger.info("entering update git repo function...")
        update_github_elastalert(os.path.join(elastalert_rules_dir, env), project_name, env)
    except BaseException:
        logger.error("promethues: failed to update elastalert files...")


def update_elastalert_rules_dir(elastalert_rules_dir, env):
    with open(config_yaml, 'r') as stream_config:
        out_config = yaml.load(stream_config)
        temporary_ea_rules = out_config['elastalert']['temporary_ea_rules'][0]
    files = os.listdir(os.path.join(temporary_ea_rules, env))
    try:
        ensure_dir_exists(os.path.join(elastalert_rules_dir, env))
        logger.info("elastalert: copying sample file...")
        for ea_rule_file in files:
            if os.path.exists(os.path.join(elastalert_rules_dir, env, ea_rule_file)):
                os.remove(os.path.join(elastalert_rules_dir, env, ea_rule_file))
            copyfile(os.path.join(temporary_ea_rules, env, ea_rule_file), os.path.join(elastalert_rules_dir, env, ea_rule_file))
            logger.debug("copying %s to %s", os.path.join(temporary_ea_rules, env, ea_rule_file), os.path.join(elastalert_rules_dir, env, ea_rule_file))
    except BaseException:
        logger.warning("copying elastalert rules failed...")


# current values in elastalert
# def elastalert_validate_current_setup(elastalert_rulesdir, project, module):
#     logger.info('-' * 75)
#     logger.info("elastalert: validating if alert is prexisting...")
#     logger.info("reading file: %s", elastalert_rulesdir)
#     logger.info("elastalert: currently configured projects: %s", project)
#     with open(elastalert_rulesdir, 'r') as stream:
#         out = yaml.load(stream)
#         try:
#             current_values_in_elastalert_rules.append(out['scrape_configs'])
#         except:
#             logger.info("elastalert: unable to get list of currently monitored projects, exiting...")
#             raise SystemExit
#     values = []
#     for i in [x for x in current_values_in_elastalert_rules]:
#         for j in i:
#             values.append(j)
#     if project + '-' + module in (str(values)):
#         logger.info("elastalert: config entry already exists for: %s", project)
#     else:
#         logger.info("elastalert: config entry does not exist for: %s", project)
#         return 0
#     logger.info('-' * 75)

