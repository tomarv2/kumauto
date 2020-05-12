import os
import ruamel.yaml as yaml
import logging
from automation.base.base_function import validate_yaml
from .config import config

logger = logging.getLogger(__name__)
config_yaml = config("CONFIG_YAML_FILE")


def validate_elastalert_rules(temporary_ea_rules, env):
    tmp_elastalert_rules_dir = os.path.join(temporary_ea_rules, env)
    if os.path.exists(tmp_elastalert_rules_dir):
        src_files = os.listdir(tmp_elastalert_rules_dir)
        with open(config_yaml, 'r') as stream_config:
            out_config = yaml.load(stream_config, Loader=yaml.Loader)
            schema_file = out_config['elastalert']['EA_rules_schema'][0]
        for rule_file in src_files:
            print("checking EA rule [{}]" .format(rule_file))
            if not validate_yaml(os.path.join(tmp_elastalert_rules_dir,rule_file)):
                return False
            #
            #
            #TODO: dumping too many logs (redo)
            #
            #
            # c = CoreKwalify(source_file=os.path.join(tmp_elastalert_rules_dir,rule_file), schema_files=[schema_file])
            # try:
            #     c.validate(raise_exception=True)
            # except:
            #     print("Error in file [{}]" .format(rule_file))
            #     return False
    return True

