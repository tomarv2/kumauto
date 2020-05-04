import shutil
import os
import yaml
import logging
from automation.config import config

from base.git_actions import *
from base.base_function import *

logger = logging.getLogger(__name__)
config_yaml = config("CONFIG_YAML_FILE")

with open(config_yaml, 'r') as stream_config:
    out_config = yaml.load(stream_config)
    env_list = out_config['env']
    elastalert_rules_nfs_path = out_config['elastalert']['rules']['nfs_path'][0]
    elastalert_config_nfs_path = out_config['elastalert']['config']['nfs_path'][0]
    elastalert_repo_url = out_config['elastalert']['repo_url'][0]
    elastalert_repo_path = out_config['elastalert']['repo_path'][0]
    ssh_key_path = out_config['ssh_key_path'][0]
    branch = out_config['branch'][0]

git_ssh_cmd = 'ssh -o StrictHostKeyChecking=no -i %s' % ssh_key_path


class UpdateElastalert:
    def __init__(self):
        # clone elastalert repo
        logger.error("_init_ function")
        logger.error('clone repos url %s in repo %s, triggered from changes on branch %s', elastalert_repo_url, elastalert_repo_path,branch)
        if os.path.exists(elastalert_repo_path):
            shutil.rmtree(elastalert_repo_path)
        clone_repo(git_ssh_cmd, elastalert_repo_url, elastalert_repo_path, branch)

    # update elastalert config file in nfs/efs. Same config used for all environments
    def push_elastalert_config(self):
        logger.error("push_elastalert_config function")
        if not compare_files(os.path.join(elastalert_repo_path, 'elastalert/_kube/config.yaml'), os.path.join(elastalert_config_nfs_path, 'config.yaml')):
            logger.error('copy from %s to %s', os.path.join(elastalert_repo_path, 'elastalert/_kube/config.yaml'),
                    os.path.join(elastalert_config_nfs_path, 'config.yaml'))
            shutil.copyfile(os.path.join(elastalert_repo_path,
                    'elastalert/_kube/config.yaml'), os.path.join( elastalert_config_nfs_path, 'config.yaml'))

    # For each environment, update elastalert rules in nfs/efs and push 
    # the changed files to their corresponding projct repo in git
    def push_elastalert_rules(self):
        logger.error("push_elastalert_rules function")
        # for each rule file in the cloned elastalert repo, compare with nfs/efs.
        for env in env_list:
            if not os.path.exists(os.path.join(elastalert_rules_nfs_path, env)):
                continue
                
            elastalert_rules_repo_path = os.path.join(elastalert_repo_path, 'rules', env)
            logger.error("elastalert_rules_repo_path: %s",elastalert_rules_repo_path)
            
            if os.path.exists(elastalert_rules_repo_path):
                src_files = os.listdir(elastalert_rules_repo_path)
                for rule_file in src_files:
                    logger.error("rule file name: %s", rule_file)
                    nfs_file_path = os.path.join(elastalert_rules_nfs_path, env, rule_file)
                    logger.error("nfs_file_path: %s", nfs_file_path)
                    rule_file_path = os.path.join(elastalert_rules_repo_path, rule_file)
                    logger.error("rule_file_path: %s", rule_file_path)

                    update_repo = False
                    if not os.path.exists(nfs_file_path):
                        logger.error('copy from %s to %s', rule_file_path, nfs_file_path)
                        shutil.copyfile(rule_file_path, nfs_file_path)
                        update_repo = True
                    else:
                        if not compare_files(nfs_file_path, rule_file_path):
                            logger.error("updating %s content", nfs_file_path)
                            logger.error('copy from %s to %s', rule_file_path, nfs_file_path)
                            shutil.copyfile(rule_file_path, nfs_file_path)
                            update_repo = True


                    ##############################################################################
                    #  This part should be enabled if we decide to update the users project repos
                    ##############################################################################
                    # if update_repo:
                    #     project_name = get_project_name_from_path(rule_file)
                    #     logger.error("project_name: %s", project_name)

                    #     project_repo_url = get_project_repo(project_name)
                    #     logger.error("project_repo_url: %s", project_repo_url)
                    #     if project_repo_url is not None:
                    #         project_repo_path = '/tmp/update_project_git_repo/%s' % project_name
                    #         logger.error("project_repo_path: %s", project_repo_path)
                            
                    #         # Clone repo, checkout 'development' branch, override user_input.yaml
                    #         # file, commit and push to git
                    #         logger.error("Clone project repo")
                    #         repo_instance = clone_repo(git_ssh_cmd,project_repo_url, project_repo_path, branch)
                    #         logger.error("Checkeout branch %s", branch)
                    #         checkout_branch(git_ssh_cmd, repo_instance, branch)
                    #         config_path = os.path.join(repo_instance,'user_input.yaml')
                    #         modify_config(rule_file_path, env, config_path)
                    #         logger.error("Commit changes of %s for rule %s in environment %s", config_path, rule_file_path, env)
                    #         commit_changes(git_ssh_cmd, repo_instance, branch, project_name)
                    #         logger.error("Push changes")
                    #         push_changes(git_ssh_cmd, repo_instance, branch)

process = UpdateElastalert()
process.push_elastalert_config()
process.push_elastalert_rules() 
