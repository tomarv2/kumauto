import os
import ruamel.yaml as yaml
from subprocess import call
import logging
from .config import (
    CONFIG_YAML_FILE
)

logger = logging.getLogger(__name__)


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
        print("file {} does not exist".format(prometheus_config_file_path + '-updated.yaml'))
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
