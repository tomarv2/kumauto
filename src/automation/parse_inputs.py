import ruamel.yaml as yaml
import logging
from automation.base.base_function import *

logger = logging.getLogger(__name__)


class ParseInputs:
    def __init__(self):
        self.old_targets = []
        self.new_targets = []
        self.clean_list = []
        self.update_route = []
        self.update_receivers = []
        # parse user_input.yaml
        self.tools = []
        self.email_to = []
        self.ea_query = []
        self.modules = []
        self.targets_to_monitor = []
        self.slack_channel = []

    # -------------------------------------------------------------------------
    #
    # PARSE CONFIG.YAML AND REQUIREMENTS.YAML
    #
    # -------------------------------------------------------------------------
    def parse_user_config_yaml(self, requirements_yaml, config_yaml, user_input_env):
        logger.debug("inside parser input")
        # parse requirements file
        with open(requirements_yaml, 'r') as stream:
            out = yaml.load(stream, Loader=yaml.Loader)
            # project to monitor
            self.project_name = user_input_env + "-" + out['monitoring']['project'][0]
            # project to monitor
            self.project_name_without_env = out['monitoring']['project'][0]
            # tools
            self.tools.append(out['monitoring']['tools'])
            # email notifications
            self.email_to.append(out['monitoring']['notification']['email'])
            # # elastalert query
            self.ea_query.append(out['monitoring']['elastalert']['query'][user_input_env])
            # targets to monitor
            self.targets_to_monitor.append(out['monitoring']['target'][user_input_env])
            # modules
            self.modules.append(out['monitoring']['modules'])
            # pagerduty id
            self.pagerduty_service_key_id = out['monitoring']['notification']['pagerduty']['service_key'][0]
            self.namespace = out['monitoring']['namespace'][0]
            self.slack_channel.append(out['monitoring']['notification']['slack']['channel'])
        # parse config file
        with open(config_yaml, 'r') as stream_config:
            out_config = yaml.load(stream_config, Loader=yaml.Loader)
            self.alertmanager_config_file_path = out_config['prometheus']['alertmanager']['config']['file_path'][0]
            self.alertmanager_config_nfs_path = out_config['prometheus']['alertmanager']['config']['nfs_path'][0]
            self.monitoring_config_file_path = out_config['prometheus']['monitoring']['config']['file_path'][0]
            self.monitoring_rules_dir = out_config['prometheus']['monitoring']['rules']['dir'][0]
            self.monitoring_rules_sample_file = out_config['prometheus']['monitoring']['rules']['sample_file'][0]
            self.monitoring_rules_sample_file_spark = out_config['prometheus']['monitoring']['rules']['sample_file_spark'][0]
            self.monitoring_rules_nfs_path = out_config['prometheus']['monitoring']['rules']['nfs_path'][0]
            self.monitoring_static_file_dir = out_config['prometheus']['monitoring']['static_file']['dir'][0]
            self.monitoring_static_file_sample_file = out_config['prometheus']['monitoring']['static_file']['sample_file'][0]
            self.monitoring_static_file_nfs_path = out_config['prometheus']['monitoring']['static_file']['nfs_path'][0]
            self.pagerduty_client_name = out_config['pagerduty_client_name'][0]
            self.elastalert_rules_dir = out_config['elastalert']['rules']['dir'][0]
            self.elastalert_nfs_path = out_config['elastalert']['rules']['nfs_path'][0]
            self.elastalert_sample_file = out_config['elastalert']['rules']['sample_file'][0]
            self.elastalert_config_file_path = out_config['elastalert']['config']['file_path'][0]
            self.elastalert_nfs_path = out_config['elastalert']['config']['nfs_path'][0]
            self.elasticsearch_hostname = out_config['elasticsearch']['hostname'][user_input_env.lower()]
            self.slack_channel.append(out_config['slack']['channel'])
            self.temporary_ea_rules = out_config['elastalert']['temporary_ea_rules'][0]
