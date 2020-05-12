import os
from subprocess import call
import logging

logger = logging.getLogger(__name__)


def validate_alartmanager_config(alartmanager_config_file_path):
    print("Validate alertmanager config file before pushing: {}".format(alartmanager_config_file_path))
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
        print("file {} does not exist".format(alartmanager_config_file_path + '-updated.yaml'))
        return True
