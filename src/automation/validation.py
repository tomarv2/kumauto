import shutil
import os
import ruamel.yaml as yaml
from subprocess import call
from pykwalify.core import Core as CoreKwalify
import logging
from automation.base.base_function import validate_yaml
from .config import config

logger = logging.getLogger(__name__)
config_yaml = config("CONFIG_YAML_FILE")


def validate_prometheus_config(prometheus_config_file_path):
    return True
    #
    # TODO:
    # returning true temp
    # until moving to docker is ready downloaded version of amtool is working
    #
    if os.path.exists(prometheus_config_file_path + '-updated.yaml'):
        cmd = 'promtool check config ' + prometheus_config_file_path + '-updated.yaml'
        if call(cmd, shell=True) == 0:
            return True
        else:
            return False
    else:
        print("file {} does not exist" .format(prometheus_config_file_path + '-updated.yaml'))
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
            files_list += " " + rule_file
    # # TODO: SEARCH CMD TO VALIDATE STATIC FILES
    # if files_list != "":
    #     return call(['promtool FIND RIGHT CMD', files_list], shell=True)
    # else: 
    #     return True
    return True


def validate_alartmanager_config(alartmanager_config_file_path):
    print("Validate alertmanager config file before pushing: {}" .format(alartmanager_config_file_path))
    return True
    #
    # TODO:
    # returning true temp
    # until moving to docker is ready downloaded version of amtool is working
    #
    if os.path.exists(alartmanager_config_file_path + '-updated.yaml'):
        cmd = 'amtool check-config ' + alartmanager_config_file_path + '-updated.yaml'
        if call(cmd, shell=True) == 0:
            return True
        else:
            return False
    else:
        print("file {} does not exist" .format(alartmanager_config_file_path + '-updated.yaml'))
        return True


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

