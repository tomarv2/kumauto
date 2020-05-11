import logging

from automation.parse_inputs import ParseInputs
from .setup_elastalert import build_elastalert, update_elastalert
from automation.base.base_function import *
from automation.validation import *
from automation.config import config

config_yaml = config("CONFIG_YAML_FILE")
requirements_yaml = config("REQUIREMENTS_YAML_FILE")
user_input_env = config("USER_INPUT_ENV")
logger = logging.getLogger(__name__)


def ea_config():
    if validate_yaml(requirements_yaml) and validate_yaml(config_yaml):
        user_input_env_lower = user_input_env.lower()
        logger.debug("Checking the format of yaml file")
        parser = ParseInputs()
        logger.debug('config file: {}' .format(config_yaml))
        parser.parse_user_config_yaml(requirements_yaml, config_yaml, user_input_env_lower)
        os.environ["TEST_ELASTALERT"] = "1"
        build_elastalert(user_input_env_lower,
                         parser.project_name,
                         parser.elastalert_rules_dir,
                         parser.namespace,
                         parser.ea_query,
                         parser.elastalert_sample_file,
                         parser.elasticsearch_hostname,
                         parser.email_to,
                         parser.pagerduty_service_key_id,
                         parser.pagerduty_client_name)
        if os.environ["TEST_ELASTALERT"] == "0":
            logger.debug("TESTING ELASTALERT")
            if validate_elastalert_rules(parser.temporary_ea_rules, user_input_env_lower):
                os.environ["TEST_ELASTALERT"] = "0"
            else:
                os.environ["TEST_ELASTALERT"] = "1"
                logger.debug("ELASTALERT validation didn't pass...")
        if os.environ["TEST_ELASTALERT"] == "0":
            update_elastalert(user_input_env_lower, parser.project_name, parser.elastalert_rules_dir)
        # -------------------------------------------------------------------------
        #
        # Cleanup temporary files
        #
        # -------------------------------------------------------------------------
        cleanup(parser.monitoring_rules_dir,
                parser.monitoring_static_file_dir,
                parser.monitoring_config_file_path,
                parser.alertmanager_config_file_path)