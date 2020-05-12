import shutil
from automation.base.base_function import *
from automation.base.git_actions import *
import ruamel.yaml as yaml
import logging
from .config import (
    CONFIG_YAML_FILE
)

logger = logging.getLogger(__name__)


def update_github_alertmanager(alertmanager_config_file, project_name, env):
    #
    #
    # TODO: temp returning TRUE
    #
    #
    return True
    logger.debug("[alertmanager] updating repo")
    #
    # parse config file
    #
    with open(CONFIG_YAML_FILE, 'r') as stream_config:
            out_config = yaml.load(stream_config)
            ssh_key_path = out_config['ssh_key_path'][0]
            branch = out_config['branch'][0]
            repo_path = out_config['prometheus']['monitoring']['repo']['path'][0]
            repo_url = out_config['prometheus']['monitoring']['repo']['url'][0]
    #
    # NOTE: the ssh key should exist in the Dockerfile
    # use environment variables to pass containers
    #
    logger.debug("[prometheus] push to git")
    logger.debug("[prometheus] ssh_key_path: {}" .format(ssh_key_path))
    git_ssh_cmd = 'ssh -o StrictHostKeyChecking=no -i %s' % ssh_key_path
    alertmanager_config_path = os.path.join(repo_path, 'alertmanager', 'config')

    logger.debug("[prometheus] git_ssh_cmd: {}" .format(git_ssh_cmd))
    logger.debug("[prometheus] repo_path: {}" .format(repo_path))
    logger.debug("[prometheus] repo_url: {}" .format(repo_url))
    logger.debug("[prometheus] alrtmanager_env_directory: {}" .format(os.path.join(repo_path, 'alertmanager')))
    logger.debug("[prometheus] alertmanager_config_path: {}" .format(alertmanager_config_path))

    try:
        logger.debug("[prometheus] verify if repo exists locally: {}" .format(repo_path))
        if os.path.exists(repo_path):
            shutil.rmtree(repo_path)
        repo_instance = clone_repo(git_ssh_cmd, repo_url, repo_path, branch)
    except BaseException:
        logger.error("[prometheus] unable to clone")
        raise SystemExit
    logger.debug("[prometheus] checkout branch: {}" .format(branch))
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
                        logger.error("directory does not exist")
                        pass
                try:
                    logger.debug("[prometheus] copying alertmanager config file")
                    if not os.path.exists(os.path.join(alertmanager_config_path_env, 'config.yaml')):
                        shutil.copy(alertmanager_config_file, os.path.join( alertmanager_config_path_env, 'config.yaml'))
                    else:
                        logger.debug("file exists")
                        if not compare_files(alertmanager_config_file, os.path.join(alertmanager_config_path_env, 'config.yaml')):
                            logger.error("different content ")
                            os.remove(os.path.join(alertmanager_config_path_env, 'config.yaml'))
                            shutil.copy(alertmanager_config_file, os.path.join(alertmanager_config_path_env, 'config.yaml'))
                except BaseException:
                    logger.error("[prometheus] alertmanager config.yaml copy failed")
        except BaseException:
            logger.error(
                "[prometheus] directory/files already exists: {}" .format
                (os.path.join(alertmanager_config_path_env, 'config.yaml')))

    # -------------------------------------------------------------------------
    #
    #    Commit and push all changes
    #
    # -------------------------------------------------------------------------
    logger.debug("[prometheus] git commit")
    commit_changes(git_ssh_cmd, repo_instance, branch, project_name)
    logger.debug("[prometheus] git push")
    push_changes(git_ssh_cmd, repo_instance, branch)

