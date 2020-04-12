import shutil, os, sys
from core.git_actions import *
from core.base_function import *
import yaml
from core.logging_function import logger

config_yaml = '/automation/config.yaml'


def update_github_elastalert(elastalert_rules_dir, project_name, env):
    # prase config file
    with open(config_yaml, 'r') as stream_config:
            out_config = yaml.load(stream_config)
            ssh_key_path = out_config['ssh_key_path'][0]
            branch = out_config['branch'][0]
            repo_path = out_config['elastalert']['repo_path'][0]
            repo_url = out_config['elastalert']['repo_url'][0]
            rules_repo_name = out_config['elastalert']['rules_repo_name'][0]

    logger.info("=" * 75)
    logger.info("elastalert: push to git...")
    logger.info("elastalert_rules_dir %s", elastalert_rules_dir)
    logger.info("project_name: %s", project_name)
    logger.info("env: %s", env)
    git_ssh_cmd = 'ssh -o StrictHostKeyChecking=no -i %s' % ssh_key_path
    env_directory = '%s/%s/%s' % (repo_path, rules_repo_name, env)
    try:
        logger.debug("elastalert: verify if repo exists locally: %s", repo_path)
        if os.path.exists(repo_path):
            logger.debug("elastalert: deleting existing files...")
            shutil.rmtree(repo_path)
        repo_instance = clone_repo(git_ssh_cmd, repo_url, repo_path, branch)
    except BaseException:
        logger.error('elastalert: unable to clone...')
        raise SystemExit
    logger.debug("elastalert: checkout branch: %s", branch)
    checkout_branch(git_ssh_cmd, repo_instance, branch)
    logger.debug( "elastalert: list dir and copy from: %s to : %s",  elastalert_rules_dir, env_directory)
    src_files = os.listdir(elastalert_rules_dir)
    for rule_file_name in src_files:
        logger.debug("elastalert: copying file: %s", rule_file_name)
        rule_file_path = os.path.join(elastalert_rules_dir, rule_file_name)
        logger.debug("elastalert: rule_file_path: %s", rule_file_path)
        if os.path.isfile(rule_file_path):
            try:
                if not os.path.exists(env_directory):
                    try:
                        os.makedirs(env_directory)
                    except OSError:
                        logger.debug("directory does not exist...")
                        pass
            except BaseException:
                logger.info(
                    "elastalert: directory/files already exists: %s",
                    elastalert_rules_dir)
            try:
                logger.info("elastalert: copying files")
                if not os.path.exists(os.path.join(env_directory,rule_file_name)):
                    shutil.copy(rule_file_path, env_directory)
                else:
                    logger.info("elastalert: path exists, compare it then remove it if different  ")
                    if not compare_files(rule_file_path,os.path.join(env_directory,rule_file_name)):
                        logger.info("elastalert: different content ")
                        os.remove(os.path.join(env_directory,rule_file_name))
                        shutil.copy(rule_file_path, env_directory)


            except BaseException:
                logger.error("elastalert: copy failed")
    logger.debug("elastalert: git commit...")
    commit_changes(
        git_ssh_cmd,
        repo_instance,
        branch,
        project_name)
    logger.debug("elastalert: git push...")
    push_changes(git_ssh_cmd, repo_instance, branch)
