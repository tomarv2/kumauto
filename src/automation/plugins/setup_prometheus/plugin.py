import logging
import os
from automation.parse_inputs import ParseInputs
from .setup import build_prometheus, update_prometheus
from automation.base.base_function import *
from automation.validation import *

from .config import (
    CONFIG_YAML_FILE,
    REQUIREMENTS_YAML_FILE,
    USER_INPUT_ENV
)

logger = logging.getLogger(__name__)


def pm_config():
    if validate_yaml(REQUIREMENTS_YAML_FILE) and validate_yaml(CONFIG_YAML_FILE):
        user_input_env_lower = USER_INPUT_ENV.lower()
        logger.debug("Checking the format of yaml file")
        parser = ParseInputs()
        logger.debug('config file: {}' .format(CONFIG_YAML_FILE))
        parser.parse_user_config_yaml(REQUIREMENTS_YAML_FILE, CONFIG_YAML_FILE, user_input_env_lower)
        os.environ["TEST_PROMETHEUS"] = "1"
        build_prometheus(CONFIG_YAML_FILE,
                         user_input_env_lower,
                         parser.monitoring_config_file_path,
                         parser.monitoring_rules_dir,
                         parser.monitoring_static_file_dir,
                         parser.project_name,
                         parser.targets_to_monitor,
                         parser.monitoring_rules_sample_file,
                         parser.monitoring_static_file_sample_file,
                         parser.modules,
                         parser.project_name_without_env)

        print('-' * 75)
        if os.environ["TEST_PROMETHEUS"] == "1":
            logger.debug("TESTING PROMETHEUS")
            if validate_prometheus_config(parser.monitoring_config_file_path) and \
                    validate_prometheus_rules(parser.monitoring_rules_dir) and \
                    validate_prometheus_static_files(parser.monitoring_static_file_dir):
                os.environ["TEST_PROMETHEUS"] = "0"
            else:
                os.environ["TEST_PROMETHEUS"] = "1"
                logger.debug("PROMETHEUS validation didn't pass...")

        if os.environ["TEST_PROMETHEUS"] == "0":
            logger.debug("updating prometheus")
            update_prometheus(user_input_env_lower,
                              parser.project_name,
                              parser.monitoring_config_file_path,
                              parser.monitoring_rules_dir,
                              parser.monitoring_static_file_dir)

        # -------------------------------------------------------------------------
        #
        # Cleanup temporary files
        #
        # -------------------------------------------------------------------------
        cleanup(parser.monitoring_rules_dir,
                parser.monitoring_static_file_dir,
                parser.monitoring_config_file_path,
                parser.alertmanager_config_file_path)