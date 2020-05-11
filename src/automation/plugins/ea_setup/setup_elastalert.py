import shutil
from shutil import copyfile
import os
import ruamel.yaml as yaml
import logging
from automation.base.base_function import *
from .git_push_elastalert import update_github_elastalert
from jinja2 import Environment, FileSystemLoader
from automation.config import config

config_yaml = config("CONFIG_YAML_FILE")
templates_directory = config("TEMPLATES_DIRECTORY")
ea_rules = config("EA_RULES")

logger = logging.getLogger(__name__)
current_list_of_projects = []
current_values_in_elastalert_rules = []


# ----------------------------------------------
#
# BUILD THE FILES OF ELASTALERT
#
# ----------------------------------------------
def build_elastalert(user_input_env,
                     project_name,
                     elastalert_rules_dir,
                     namespace,
                     ea_query,
                     elastalert_sample_file,
                     elasticsearch_hostname,
                     email_to,
                     pagerduty_service_key_id,
                     pagerduty_client_name):
    logger.debug("[elastalert] updating config for: [{}]" .format(project_name))
    try:
        elastalert_rules_setup(elastalert_rules_dir,
                               elastalert_sample_file,
                               project_name,
                               get_index_name(project_name, namespace),
                               convert_list_to_ea_query(ea_query),
                               get_alert_type(user_input_env),
                               convert_list_to_str(email_to),
                               pagerduty_service_key_id,
                               pagerduty_client_name,
                               user_input_env,
                               get_application_type(project_name),
                               elasticsearch_hostname
                               )
    except BaseException:
        logger.error("[elastalert] unable to setup config")


# --------------------------------------------------------
#
# ADD THE NEW ELASTALERT RULES
#
# --------------------------------------------------------
def elastalert_rules_setup(elastalert_rules_dir,
                           sample_file,
                           project_name,
                           index,
                           ea_query,
                           alert_type,
                           email_to,
                           pagerduty_service_key_id,
                           pagerduty_client_name,
                           env,
                           application,
                           elasticsearch_hostname
                           ):
    logger.debug("[elastalert] Inside elastalert_rules function")
    logger.debug("[elastalert] Rules directory: {}" .format(elastalert_rules_dir))
    logger.debug("[elastalert] Sample file: {}" .format(sample_file))
    logger.debug("[elastalert] Project Name: {}" .format(project_name))
    logger.debug("[elastalert] Index: {}" .format(index))
    logger.debug("[elastalert] EA query: {}" .format(ea_query))
    logger.debug("[elastalert] Pagerduty service key: {}" .format(pagerduty_service_key_id))
    logger.debug("[elastalert] Pagerduty client name: {}" .format(pagerduty_client_name))
    logger.debug("[elastalert] Alert type: {}" .format(alert_type))
    logger.debug("[elastalert] Email To: {}" .format(email_to))
    logger.debug("[elastalert] Env: {}" .format(env))
    logger.debug("[elastalert] Application: {}" .format(application))
    logger.debug("[elastalert] taking backup of file")
    if os.path.exists(config_yaml):
        logger.debug("[elastalert] config file exists: {}" .format(config_yaml))
    else:
        logger.debug("[elastalert] file does not exist: {}".format(config_yaml))
    with open(config_yaml, 'r') as stream:
        out_config = yaml.load(stream, Loader=yaml.Loader)
        temporary_ea_rules = ''.join(out_config['elastalert']['temporary_ea_rules'])
        logger.debug("[elastalert] temporary EA rules: {}" .format(temporary_ea_rules))

    ea_rules_file = os.path.join(temporary_ea_rules, env, project_name + '.yaml')
    try:
        logger.debug("[elastalert] checking if directory exists")
        ensure_dir_exists(os.path.join(temporary_ea_rules, env))
        ensure_dir_exists(os.path.join(elastalert_rules_dir, env))
        logger.debug("[elastalert] copying sample file")
        logger.debug("[elastalert] sample_file: {}" .format(sample_file))
        logger.debug("[elastalert] EA rules file: {}" .format(ea_rules_file))
        try:
            copyfile(sample_file, ea_rules_file)
        except:
            raise SystemExit
    except BaseException:
        logger.info("[elastalert] file already exists (deleting and copying sample file)")
        shutil.rmtree(ea_rules_file)
        copyfile(sample_file, ea_rules_file)
    logger.debug("[elastalert] updating elastalert rules section")
    elastalert_rules = []
    #
    # Load Jinja2 template
    #
    jinja_env = Environment(loader=FileSystemLoader(templates_directory))
    try:
        template = jinja_env.get_template(ea_rules)
    except:
        logger.error("[elastalert] error parsing jinja template: {}" .format(template))
    try:
        with open(sample_file, "r") as asmr:
            for line in asmr.readlines():
                if "ELASTALERT RULES GO ABOVE" in line:
                    #
                    # render template using data
                    #
                    elastalert_rules += (template.render(host=elasticsearch_hostname,
                                                         env_prj_name=env + '-' + project_name,
                                                         index=index,
                                                         ea_query=ea_query,
                                                         alert_type=alert_type,
                                                         pagerduty_service_key=pagerduty_service_key_id,
                                                         pagerduty_client_name=pagerduty_client_name,
                                                         email_to=email_to,
                                                         env=env.upper(),
                                                         application=application,
                                                         project_name=project_name
                                                         ))
                # elastalert_rules += line
    except:
        logger.debug("[elastalert] unable to open file: {}" .format(sample_file))
    try:
        with open(ea_rules_file, "w") as asmw:
            asmw.writelines(elastalert_rules)
    except:
        logger.debug("[elastalert] unable to write to file: {}" .format(ea_rules_file))


# -------------------------------------------------------
#
# APPLY CHANGES TO EFS AND GITHUB FOR  ELASTALERT
#
# -------------------------------------------------------
def update_elastalert(env, project_name, elastalert_rules_dir):
    try:
        update_elastalert_rules_dir(elastalert_rules_dir, env)
        logger.debug("entering update git repo function")
        update_github_elastalert(os.path.join(elastalert_rules_dir, env), project_name, env)
    except BaseException:
        logger.error("[elastalert] failed to update elastalert files")


def update_elastalert_rules_dir(elastalert_rules_dir, env):
    with open(config_yaml, 'r') as stream_config:
        out_config = yaml.load(stream_config, Loader=yaml.Loader)
        temporary_ea_rules = out_config['elastalert']['temporary_ea_rules'][0]
    files = os.listdir(os.path.join(temporary_ea_rules, env))
    try:
        ensure_dir_exists(os.path.join(elastalert_rules_dir, env))
        logger.debug("[elastalert] copying sample file")
        for ea_rule_file in files:
            if os.path.exists(os.path.join(elastalert_rules_dir, env, ea_rule_file)):
                os.remove(os.path.join(elastalert_rules_dir, env, ea_rule_file))
            copyfile(os.path.join(temporary_ea_rules, env, ea_rule_file), os.path.join(elastalert_rules_dir, env, ea_rule_file))
            logger.debug("copying {} to {}" .format(os.path.join(temporary_ea_rules, env, ea_rule_file),
                                                    os.path.join(elastalert_rules_dir, env, ea_rule_file)))
    except BaseException:
        logger.error("copying elastalert rules failed")

