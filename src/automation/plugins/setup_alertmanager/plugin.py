import logging
import os
from automation.parse_inputs import ParseInputs
from automation.base.base_function import *
from.validation import validate_alartmanager_config
from .setup import build_alertmanager, update_alertmanager
from .config import (
    CONFIG_YAML_FILE,
    REQUIREMENTS_YAML_FILE,
    USER_INPUT_ENV
)

logger = logging.getLogger(__name__)


def am_config():
    if validate_yaml(REQUIREMENTS_YAML_FILE) and validate_yaml(CONFIG_YAML_FILE):
        user_input_env_lower = USER_INPUT_ENV.lower()
        logger.debug("Checking the format of yaml file")
        parser = ParseInputs()
        # ----------------------------------------------------
        #
        # Build the new files
        #
        # ----------------------------------------------------
        logger.debug('config file: {}' .format(CONFIG_YAML_FILE))
        parser.parse_user_config_yaml(REQUIREMENTS_YAML_FILE, CONFIG_YAML_FILE, user_input_env_lower)
        os.environ["TEST_ALERTMANAGER"] = "1"
        build_alertmanager(user_input_env_lower,
                           parser.project_name,
                           parser.alertmanager_config_file_path,
                           parser.modules,
                           parser.tools,
                           parser.email_to,
                           parser.slack_channel,
                           parser.pagerduty_service_key_id)

        os.environ["TEST_ALERTMANAGER"] = "0"
        # -------------------------------------------------------------------------
        #
        # Test the new files
        #
        # -------------------------------------------------------------------------
        if os.environ["TEST_ALERTMANAGER"] == "0":
            logger.debug("TESTING ALERTMANAGER")
            if validate_alartmanager_config(parser.alertmanager_config_file_path):
                os.environ["TEST_ALERTMANAGER"] = "0"
            else:
                os.environ["TEST_ALERTMANAGER"] = "1"
                logger.debug("ALERTMANAGER validation didn't pass")
        # -------------------------------------------------------------------------
        #
        # Push the new files
        #
        # -------------------------------------------------------------------------
        if os.environ["TEST_ALERTMANAGER"] == "0":
            update_alertmanager(user_input_env_lower, parser.project_name, parser.alertmanager_config_file_path)

        # -------------------------------------------------------------------------
        #
        # Cleanup temporary files
        #
        # -------------------------------------------------------------------------
        cleanup(parser.monitoring_rules_dir,
                parser.monitoring_static_file_dir,
                parser.monitoring_config_file_path,
                parser.alertmanager_config_file_path)
