import shutil, os, sys

import sys
sys.path.append("..")

from automation.core.base_function import *
from automation.core.git_actions import *
import yaml
import logging


config_yaml = '/automation/config.yaml'
logger = logging.getLogger(__name__)

def update_github_prometheus(prometheus_rules_dir, prometheus_static_files_dir, prometheus_config_file, project_name, env):
    # prase config file
    with open(config_yaml, 'r') as stream_config:
            out_config = yaml.load(stream_config)
            ssh_key_path = out_config['ssh_key_path'][0]
            branch = out_config['branch'][0]
            repo_path = out_config['prometheus']['monitoring']['repo']['path'][0]
            repo_url = out_config['prometheus']['monitoring']['repo']['url'][0]

    logger.debug("[prometheus] push to git...")
    logger.debug("[prometheus] ssh_key_path: %s", ssh_key_path)
    git_ssh_cmd = 'ssh -o StrictHostKeyChecking=no -i %s' % ssh_key_path
    prometheus_rules_path = os.path.join(repo_path, 'monitoring', 'rules', env)
    prometheus_static_files_path = os.path.join(repo_path, 'monitoring', 'static_files', env)
    prometheus_config_path = os.path.join(repo_path, 'monitoring','config')

    logger.debug("[prometheus] git_ssh_cmd: %s", git_ssh_cmd)
    logger.debug("[prometheus] repo_path: %s", repo_path)
    logger.debug("[prometheus] repo_url: %s", repo_url)
    logger.debug("[prometheus] monitoring_env_directory: %s", os.path.join(repo_path, 'monitoring'))
    logger.debug("[prometheus] prometheus_static_files_path: %s", prometheus_static_files_path)
    logger.debug("[prometheus] prometheus_config_path: %s", prometheus_config_path)

    try:
        logger.debug("[prometheus] verify if repo exists locally: %s", repo_path)
        if os.path.exists(repo_path):
            shutil.rmtree(repo_path)
        repo_instance = clone_repo(git_ssh_cmd, repo_url, repo_path, branch)
    except BaseException:
        logger.error('[prometheus] unable to clone...')
        raise SystemExit
    logger.debug("[prometheus] checkout branch: %s", branch)
    checkout_branch(git_ssh_cmd, repo_instance, branch)

    # -------------------------------------------------------------------------
    #
    #    Update prometheus rules
    #
    # -------------------------------------------------------------------------
    logger.debug("[prometheus] list dir and copy from: %s to : %s", prometheus_rules_dir, prometheus_rules_path)
    src_files = os.listdir(prometheus_rules_dir)
    for rule_file_name in src_files:
        rule_file_path = os.path.join(os.path.join(prometheus_rules_dir, rule_file_name))
        logger.debug("[prometheus] rules file path: %s", rule_file_path)
        try:
            if os.path.isfile(rule_file_path):
                if not os.path.exists(prometheus_rules_path):
                    try:
                        os.makedirs(prometheus_rules_path)
                    except OSError:
                        logger.debug("directory does not exist...")
                        pass
                try:
                    logger.debug("[prometheus] rules file name: %s", os.path.join(prometheus_rules_path, rule_file_name))
                    logger.debug("[prometheus] copying rule files: %s", rule_file_path)
                    if not os.path.exists(os.path.join(prometheus_rules_path, rule_file_name)):
                        logger.debug("[prometheus] copying rules file...")
                        try:
                            shutil.copy(rule_file_path, os.path.join(prometheus_rules_path, rule_file_name))
                        except:
                            logger.error("[prometheus] unable to copy rules file from: %s to %s ", rule_file_path, os.path.join(prometheus_rules_path, rule_file_name) )
                    else:
                        logger.debug('rule exist, then compare content')
                        if not compare_files(rule_file_path, os.path.join(prometheus_rules_path, rule_file_name)):
                            logger.debug("different content ")
                            os.remove(os.path.join(prometheus_rules_path, rule_file_name))
                            shutil.copy(rule_file_path, os.path.join(prometheus_rules_path, rule_file_name))
                except BaseException:
                    logger.error("[prometheus] rules file copy failed")
        except BaseException:
            logger.error("[prometheus] directory/files already exists: %s", prometheus_rules_path)

    # -------------------------------------------------------------------------
    #
    #    Update prometheus static files
    #
    # -------------------------------------------------------------------------
    logger.debug("[prometheus] list dir and copy from: %s to : %s", prometheus_static_files_dir, prometheus_static_files_path)
    src_files = os.listdir(prometheus_static_files_dir)
    for static_file_name in src_files:
        logger.debug("[prometheus] copying static file: %s", static_file_name)
        static_file_path = os.path.join(
            os.path.join(prometheus_static_files_dir, static_file_name))
        logger.debug("[prometheus] static_file_name: %s", static_file_name)
        try:
            if os.path.isfile(static_file_path):
                if not os.path.exists(prometheus_static_files_path):
                    try:
                        os.makedirs(prometheus_static_files_path)
                    except OSError:
                        logger.error("directory does not exist...")
                        pass
                try:
                    logger.debug("[prometheus] copying static files")
                    if not os.path.exists(os.path.join(prometheus_static_files_path, static_file_name)):
                        shutil.copy(static_file_path, os.path.join(prometheus_static_files_path, static_file_name))
                    else:
                        logger.debug("file exists ")
                        if not compare_files(static_file_path,os.path.join(prometheus_static_files_path, static_file_name)):
                            logger.error("different content ")
                            os.remove(os.path.join(prometheus_static_files_path, static_file_name))
                            shutil.copy(static_file_path, os.path.join(prometheus_static_files_path, static_file_name))
                except BaseException:
                    logger.error("[prometheus] static_file copy failed")
        except BaseException:
            logger.error( "[prometheus] directory/files already exists: %s", prometheus_static_files_path)

    # -------------------------------------------------------------------------
    #
    #    Update prometheus config
    #
    # -------------------------------------------------------------------------
    for target in get_list_env(env):
        prometheus_config_path_env = os.path.join(prometheus_config_path, target)
        logger.debug("[prometheus] copy from: %s to : %s", prometheus_config_file, os.path.join(prometheus_config_path,'config.yaml'))
        try:
            if os.path.isfile(prometheus_config_file):
                if not os.path.exists(prometheus_config_path_env):
                    try:
                        os.makedirs(prometheus_config_path_env)
                    except OSError:
                        logger.debug("directory does not exist...")
                        pass
                try:
                    logger.error("[prometheus] copying prometheus config file")
                    if not os.path.exists(os.path.join(prometheus_config_path_env,'config.yaml')):
                        shutil.copy(
                            prometheus_config_file,
                            os.path.join(
                                prometheus_config_path_env,
                                'config.yaml'))
                    else:
                        logger.error("file exists ")
                        if not compare_files(prometheus_config_file,os.path.join(prometheus_config_path_env,'config.yaml')):
                            logger.error("different content ")
                            os.remove(os.path.join(prometheus_config_path_env,'config.yaml'))
                            shutil.copy(
                                prometheus_config_file,
                                os.path.join(
                                    prometheus_config_path_env,
                                    'config.yaml'))
                except BaseException:
                    logger.error("[prometheus] config.yaml copy failed")
        except BaseException:
            logger.error(
                "[prometheus] directory/files already exists: %s",
                os.path.join(
                    prometheus_config_path_env,
                    'config.yaml'))

    # -------------------------------------------------------------------------
    #
    #    Commit and push all changes
    #
    # -------------------------------------------------------------------------
    logger.error("[prometheus] git commit...")
    commit_changes(git_ssh_cmd,repo_instance,branch,project_name)
    logger.error("[prometheus] git push...")
    push_changes(git_ssh_cmd, repo_instance, branch)


def update_github_alertmanager(alertmanager_config_file, project_name, env):
    logger.debug("[alertmanager] updating repo")
    #
    # parse config file
    #
    with open(config_yaml, 'r') as stream_config:
            out_config = yaml.load(stream_config)
            ssh_key_path = out_config['ssh_key_path'][0]
            branch = out_config['branch'][0]
            repo_path = out_config['prometheus']['monitoring']['repo']['path'][0]
            repo_url = out_config['prometheus']['monitoring']['repo']['url'][0]
    #
    # NOTE: the ssh key should exist in the Dockerfile
    # use environment variables to pass containers
    #
    logger.debug("[prometheus] push to git...")
    logger.debug("[prometheus] ssh_key_path: %s", ssh_key_path)
    git_ssh_cmd = 'ssh -o StrictHostKeyChecking=no -i %s' % ssh_key_path
    alertmanager_config_path = os.path.join(repo_path, 'alertmanager', 'config')

    logger.debug("[prometheus] git_ssh_cmd: %s", git_ssh_cmd)
    logger.debug("[prometheus] repo_path: %s", repo_path)
    logger.debug("[prometheus] repo_url: %s", repo_url)
    logger.debug("[prometheus] alrtmanager_env_directory: %s", os.path.join(repo_path, 'alertmanager'))
    logger.debug("[prometheus] alertmanager_config_path: %s", alertmanager_config_path)

    try:
        logger.debug("[prometheus] verify if repo exists locally: %s", repo_path)
        if os.path.exists(repo_path):
            shutil.rmtree(repo_path)
        repo_instance = clone_repo(git_ssh_cmd, repo_url, repo_path, branch)
    except BaseException:
        logger.error('[prometheus] unable to clone...')
        raise SystemExit
    logger.debug("[prometheus] checkout branch: %s", branch)
    checkout_branch(git_ssh_cmd, repo_instance, branch)

    # -------------------------------------------------------------------------
    #
    #    Update alertmanager config
    #
    # -------------------------------------------------------------------------
    for target in get_list_env(env):
        alertmanager_config_path_env = os.path.join(alertmanager_config_path, target)
        logger.debug("[prometheus] copy from: {} to : {}" .format(
            alertmanager_config_file, os.path.join(alertmanager_config_path_env, 'config.yaml')))
        try:
            if os.path.isfile(alertmanager_config_file):
                if not os.path.exists(alertmanager_config_path_env):
                    try:
                        os.makedirs(alertmanager_config_path_env)
                    except OSError:
                        logger.error("directory does not exist...")
                        pass
                ##
                try:
                    logger.debug("[prometheus] copying alertmanager config file")
                    if not os.path.exists(os.path.join(alertmanager_config_path_env,'config.yaml')):
                        shutil.copy(alertmanager_config_file, os.path.join( alertmanager_config_path_env, 'config.yaml'))
                    else:
                        logger.error("file exists ")
                        if not compare_files(alertmanager_config_file, os.path.join(alertmanager_config_path_env,'config.yaml')):
                            logger.error("different content ")
                            os.remove(os.path.join(alertmanager_config_path_env, 'config.yaml'))
                            shutil.copy(alertmanager_config_file, os.path.join(alertmanager_config_path_env, 'config.yaml'))
                except BaseException:
                    logger.error("[prometheus] alertmanager config.yaml copy failed")
        except BaseException:
            logger.error(
                "[prometheus] directory/files already exists: %s",
                os.path.join(alertmanager_config_path_env, 'config.yaml'))

    # -------------------------------------------------------------------------
    #
    #    Commit and push all changes
    #
    # -------------------------------------------------------------------------
    logger.debug("[prometheus] git commit...")
    commit_changes(git_ssh_cmd,repo_instance,branch,project_name)
    logger.debug("[prometheus] git push...")
    push_changes(git_ssh_cmd, repo_instance, branch)

