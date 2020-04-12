import shutil
import os
import yaml
from subprocess import call
from pykwalify.core import Core
from core.logging_function import logger
from core.base_function import validate_yaml

config_yaml = '/automation/config.yaml'


def validate_prometheus_config(prometheus_config_file_path):
    if os.path.exists(prometheus_config_file_path + '-updated.yaml'):
        cmd = 'promtool check config ' + prometheus_config_file_path + '-updated.yaml'
        if call(cmd, shell=True) == 0:
            return True
        else:
            return False
    else:
        logger.debug("file %s does not exist", prometheus_config_file_path + '-updated.yaml')
        return True


def validate_prometheus_rules(prometheus_rules_dir):
    src_files = os.listdir(prometheus_rules_dir)
    files_list = ""
    for rule_file in src_files:
        if "-updated.yaml" in rule_file:
            files_list += " " + rule_file
    
    if files_list != "":
        cmd = 'promtool check rules ' + files_list
        if call(cmd, shell=True) == 0:
            return True
        else:
            return False
    else: 
        return True


def validate_prometheus_static_files(prometheus_static_files_dir):
    src_files = os.listdir(prometheus_static_files_dir)
    files_list = ""
    for rule_file in src_files:
        if "-updated.yaml" in rule_file:
            files_list += " " +  rule_file
    # # TODO: SEARCH CMD TO VALIDATE STATIC FILES
    # if files_list != "":
    #     return call(['promtool FIND RIGHT CMD', files_list], shell=True)
    # else: 
    #     return True
    return True


def validate_alartmanager_config(alartmanager_config_file_path):
    if os.path.exists(alartmanager_config_file_path + '-updated.yaml'):
        cmd = 'amtool check-config ' + alartmanager_config_file_path + '-updated.yaml'
        if call(cmd, shell=True) == 0:
            return True
        else:
            return False
    else:
        logger.debug("file %s does not exist", alartmanager_config_file_path + '-updated.yaml')
        return True


def validate_elastalert_rules(temporary_ea_rules, env):
    tmp_elastalert_rules_dir = os.path.join(temporary_ea_rules, env)
    if os.path.exists(tmp_elastalert_rules_dir):
        src_files = os.listdir(tmp_elastalert_rules_dir)
        with open(config_yaml, 'r') as stream_config:
            out_config = yaml.load(stream_config)
            schema_file = out_config['elastalert']['EA_rules_schema'][0]
        for rule_file in src_files:
            logger.debug("checking EA rule %s ", rule_file)
            if not validate_yaml(os.path.join(tmp_elastalert_rules_dir,rule_file)):
                return False
            c = Core(source_file=os.path.join(tmp_elastalert_rules_dir,rule_file), schema_files=[schema_file])
            try:
                c.validate(raise_exception=True)
            except:
                logger.error("Error in file %s", rule_file)
                return False
    return True

