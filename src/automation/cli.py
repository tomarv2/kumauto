import sys
import os
import yaml
import sys
sys.path.append("..")

#sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from yaml.scanner import ScannerError
from .parse_inputs import ParseInputs
from .setup_prometheus import build_prometheus, update_prometheus
from .setup_alertmanager import build_alertmanager, update_alertmanager
from .setup_elastalert import build_elastalert, update_elastalert

from core.base_function import *
from .validation import *
from core.logging_function import logger

config_yaml = '/Users/varun.tomar/Documents/personal_github/automation/src/config.yaml'  # todo: better arrangement here
requirements_yaml = '/Users/varun.tomar/Documents/personal_github/automation/src/user_input.yaml'
#logger.configure(requirements_yaml)


user_input_env = 'aws'


def entrypoint():
    user_input_env_lower = user_input_env.lower()
    logger.info("Checking the format of yaml file")
    parser = ParseInputs()
    parser.parse_user_config_yaml(requirements_yaml, config_yaml, user_input_env_lower)
    os.environ["TEST_ALERTMANAGER"] = "1"
    os.environ["TEST_PROMETHEUS"] = "1"
    os.environ["TEST_ELASTALERT"] = "1"
    # ----------------------------------------------------
    #
    # Build files entered by user:
    # 1. user_input.yaml
    # 2. config.yaml
    #
    # ----------------------------------------------------
    if validate_yaml(requirements_yaml) and validate_yaml(config_yaml):
        # ----------------------------------------------------
        #
        # Build the new files
        #
        # ----------------------------------------------------
        build_alertmanager(user_input_env_lower, parser.project_name, parser.alertmanager_config_file_path,
                           parser.modules, parser.tools, parser.email_to, parser.slack_channel, parser.pagerduty_service_key_id)
        os.environ["TEST_ALERTMANAGER"] = "0"
        build_prometheus(config_yaml, user_input_env_lower, parser.monitoring_config_file_path,
                         parser.monitoring_rules_dir, parser.monitoring_static_file_dir, parser.project_name,
                         parser.targets_to_monitor, parser.monitoring_rules_sample_file,
                         parser.monitoring_static_file_sample_file, parser.modules, parser.project_name_without_env)
        os.environ["TEST_PROMETHEUS"] = "0"
        build_elastalert(user_input_env_lower, parser.project_name, parser.elastalert_rules_dir,
                         parser.namespace, parser.ea_query, parser.elastalert_sample_file, parser.elasticsearch_hostname,
                         parser.email_to, parser.pagerduty_service_key_id, parser.pagerduty_client_name)
        os.environ["TEST_ELASTALERT"] = "0"
    else:
        logger.debug("yaml files validation didn't pass...")
        os.environ["TEST_ALERTMANAGER"] = "1"
        os.environ["TEST_PROMETHEUS"] = "1"
        os.environ["TEST_ELASTALERT"] = "1"
    ######################################################
    # Test the new files
    ######################################################
    if os.environ["TEST_ALERTMANAGER"] == "0":
        logger.debug("TESTING ALERTMANAGER...")
        if validate_alartmanager_config(parser.alertmanager_config_file_path):
            os.environ["TEST_ALERTMANAGER"] = "0"
        else:
            os.environ["TEST_ALERTMANAGER"] = "1"
            logger.debug("ALERTMANAGER validation didn't pass...")

    if os.environ["TEST_PROMETHEUS"] == "0":
        logger.debug("TESTING PROMETHEUS...")
        if validate_prometheus_config(parser.monitoring_config_file_path) and validate_prometheus_rules\
             (parser.monitoring_rules_dir) and validate_prometheus_static_files(parser.monitoring_static_file_dir):
            os.environ["TEST_PROMETHEUS"] = "0"
        else:
            os.environ["TEST_PROMETHEUS"] = "1"
            logger.debug("PROMETHEUS validation didn't pass...")

    if os.environ["TEST_ELASTALERT"] == "0":
        logger.debug("TESTING ELASTALERT...")
        if validate_elastalert_rules(parser.temporary_ea_rules, user_input_env_lower):
            os.environ["TEST_ELASTALERT"] = "0"
        else:
            os.environ["TEST_ELASTALERT"] = "1"
            logger.debug("ELASTALERT validation didn't pass...")


    ######################################################
    # Push the new files
    ######################################################  
    if os.environ["TEST_ALERTMANAGER"] == "0":
        update_alertmanager(user_input_env_lower, parser.project_name, parser.alertmanager_config_file_path)
    if os.environ["TEST_PROMETHEUS"] == "0": 
        update_prometheus(user_input_env_lower, parser.project_name, parser.monitoring_config_file_path,
                          parser.monitoring_rules_dir, parser.monitoring_static_file_dir)
    if os.environ["TEST_ELASTALERT"] == "0":
        update_elastalert(user_input_env_lower, parser.project_name, parser.elastalert_rules_dir)

    ######################################################
    # Cleanup temporary files
    ######################################################  
    cleanup(parser.monitoring_rules_dir, parser.monitoring_static_file_dir, parser.monitoring_config_file_path, parser.alertmanager_config_file_path)


if __name__ == "__main__":
    entrypoint()
