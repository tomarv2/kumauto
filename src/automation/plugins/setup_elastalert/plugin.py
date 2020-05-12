import logging
import os
from automation.parse_inputs import ParseInputs
from .setup import build_elastalert, update_elastalert
from automation.base.base_function import *
from automation.validation import *
from .config import (
    CONFIG_YAML_FILE,
    REQUIREMENTS_YAML_FILE,
    USER_INPUT_ENV
)

logger = logging.getLogger(__name__)


def ea_config():
    if validate_yaml(REQUIREMENTS_YAML_FILE) and validate_yaml(CONFIG_YAML_FILE):
        user_input_env_lower = USER_INPUT_ENV.lower()
        # ----------------------------------------------------
        #
        # Build the new files
        #
        # ----------------------------------------------------
        logger.debug("Checking the format of yaml file")
        parser = ParseInputs()
        logger.debug('config file: {}' .format(CONFIG_YAML_FILE))
        parser.parse_user_config_yaml(REQUIREMENTS_YAML_FILE, CONFIG_YAML_FILE, user_input_env_lower)
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
        # -------------------------------------------------------------------------
        #
        # Test the new files
        #
        # -------------------------------------------------------------------------
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