import shutil
import yaml
import os, sys

sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from core.git_actions import *
from core.base_function import *
from core.logging_function import logger
logger.configure(None)

config_yaml = '/automation/config.yaml'

with open(config_yaml, 'r') as stream_config:
    out_config = yaml.load(stream_config)
    env_list = out_config['env']
    ssh_key_path = out_config['ssh_key_path'][0]
    branch = out_config['branch'][0]
    #### NFS paths
    alertmanager_config_nfs_path = out_config['prometheus']['alertmanager']['config']['nfs_path'][0]
    prometheus_config_nfs_path = out_config['prometheus']['monitoring']['config']['nfs_path'][0]
    prometheus_rules_nfs_path = out_config['prometheus']['monitoring']['rules']['dir'][0]
    prometheus_static_files_nfs_path = out_config['prometheus']['monitoring']['static_file']['dir'][0]
    #### Repo paths
    prometheus_repo_url = out_config['prometheus']['monitoring']['repo']['url'][0]
    prometheus_repo_path = out_config['prometheus']['monitoring']['repo']['path'][0]

git_ssh_cmd = 'ssh -o StrictHostKeyChecking=no -i %s' % ssh_key_path


class UpdatePrometheus:
    def __init__(self):
        logger.info("_init_ function")
        logger.info(
            'clone repos url %s in repo %s, triggered from changes on branch %s',
            prometheus_repo_url,
            prometheus_repo_path,
            branch)
        if os.path.exists(prometheus_repo_path):
            shutil.rmtree(prometheus_repo_path)
        clone_repo(
            git_ssh_cmd,
            prometheus_repo_url,
            prometheus_repo_path,
            branch)

    def main(self):
        for env in env_list:
            if not (os.path.exists(os.path.join(prometheus_rules_nfs_path, env)) or (os.path.exists(os.path.join(prometheus_static_files_nfs_path, env)))):
                logger.info('break for env %s',env)
                continue

            alertmanager_config_repo_path = os.path.join(prometheus_repo_path, 'alertmanager/config/', env, 'config.yaml')
            prometheus_config_repo_path = os.path.join(prometheus_repo_path, 'monitoring/config/', env, 'config.yaml')
            prometheus_rules_repo_path = os.path.join(prometheus_repo_path, 'monitoring/rules/', env)
            prometheus_static_files_repo_path = os.path.join(prometheus_repo_path, 'monitoring/static_files/', env)

            self.update_alertmanager_config(alertmanager_config_nfs_path, alertmanager_config_repo_path)
            self.update_prometheus_config(prometheus_config_nfs_path, prometheus_config_repo_path)
            self.update_prometheus_rules(os.path.join(prometheus_rules_nfs_path, env), prometheus_rules_repo_path, env, prometheus_config_nfs_path)
            self.update_prometheus_static_files(os.path.join(prometheus_static_files_nfs_path, env), prometheus_static_files_repo_path, env)


    # update alertmanager config file in nfs/efs
    def update_alertmanager_config(self, alertmanager_config_nfs_path, alertmanager_config_repo_path):
        logger.info("update_prometheus_config function")
        if not compare_files(alertmanager_config_repo_path, alertmanager_config_nfs_path):
            logger.info('copy from %s to %s',alertmanager_config_repo_path, alertmanager_config_nfs_path)
            shutil.copyfile(alertmanager_config_repo_path, alertmanager_config_nfs_path)


    # update prometheus config file in nfs/efs
    def update_prometheus_config(self, prometheus_config_nfs_path, prometheus_config_repo_path):
        logger.info("update_prometheus_config function")
        if not compare_files(prometheus_config_repo_path, prometheus_config_nfs_path):
            logger.info("copy from %s to %s", prometheus_config_repo_path, prometheus_config_nfs_path)
            shutil.copyfile(prometheus_config_repo_path, prometheus_config_nfs_path)


    # Update prometheus rules in nfs/efs and push 
    # the changed files to their corresponding projct repo in git
    def update_prometheus_rules(self, prometheus_rules_nfs_path, prometheus_rules_repo_path, env, prometheus_config_nfs_path):
        logger.info("update_prometheus_rules function")
        
        if os.path.exists(prometheus_rules_repo_path):
            src_files = os.listdir(prometheus_rules_repo_path)
            for rule_file in src_files:
                logger.info("rule file name: %s", rule_file)
                nfs_file_path = os.path.join(prometheus_rules_nfs_path, rule_file)
                logger.info("nfs_file_path: %s", nfs_file_path)
                rule_file_path = os.path.join(prometheus_rules_repo_path, rule_file)
                logger.info("rule_file_path: %s", rule_file_path)

                update_repo = False
                if not os.path.exists(nfs_file_path):
                    logger.info('copy from %s to %s', rule_file_path, nfs_file_path)
                    shutil.copyfile(rule_file_path, nfs_file_path)
                    update_repo = True
                else:
                    if not compare_files(nfs_file_path, rule_file_path):
                        logger.info("updating %s content", nfs_file_path)
                        logger.info('copy from %s to %s', rule_file_path, nfs_file_path)
                        shutil.copyfile(rule_file_path, nfs_file_path)
                        update_repo = True

                # Ensure that prometheus config includes the path for this rule file
                # NOTE: If enabled, we should update the config in prometheus repo and push again!!
                # rule_path_exists(nfs_file_path, prometheus_config_nfs_path)
                
                ##############################################################################
                #  This part should be enabled if we decide to update the users project repos
                ##############################################################################   
                # if update_repo:
                #     project_name = get_project_name_from_path(rule_file)
                #     logger.info("project_name: %s", project_name)

                #     project_repo_url = get_project_repo(project_name)
                #     logger.info("project_repo_url: %s", project_repo_url)
                #     if project_repo_url is not None:
                #         project_repo_path = '/tmp/update_project_git_repo/%s' % project_name
                #         logger.info("project_repo_path: %s", project_repo_path)
                            
                #         # Clone repo, checkout 'development' branch, override user_input.yaml
                #         # file, commit and push to git
                #         logger.debug("Clone project repo")
                #         repo_instance = clone_repo(git_ssh_cmd,project_repo_url, project_repo_path, branch)
                #         logger.debug("Checkeout branch %s", branch)
                #         checkout_branch(git_ssh_cmd, repo_instance, branch)
                #         config_path = os.path.join(repo_instance,'user_input.yaml')
                #         modify_config(rule_file_path, env, config_path)
                #         logger.debug("Commit changes of %s for rule %s in environment %s", config_path, rule_file_path, env)
                #         commit_changes(git_ssh_cmd, repo_instance, branch, project_name)
                #         logger.debug("Push changes")
                #         push_changes(git_ssh_cmd, repo_instance, branch)


    # Update prometheus static files in nfs/efs and push 
    # the changed files to their corresponding projct repo in git
    def update_prometheus_static_files(self, prometheus_static_files_nfs_path, prometheus_static_files_repo_path, env):
        logger.info("update_prometheus_static_files function")
        
        if os.path.exists(prometheus_static_files_repo_path):
            src_files = os.listdir(prometheus_static_files_repo_path)
            for static_file in src_files:
                logger.info("rule file name: %s", static_file)
                nfs_file_path = os.path.join(prometheus_static_files_nfs_path, static_file)
                logger.info("nfs_file_path: %s", nfs_file_path)
                static_file_path = os.path.join(prometheus_static_files_repo_path, static_file)
                logger.info("static_file_path: %s", static_file_path)

                update_repo = False
                if not os.path.exists(nfs_file_path):
                    logger.info('copy from %s to %s', static_file_path, nfs_file_path)
                    shutil.copyfile(static_file_path, nfs_file_path)
                    update_repo = True
                else:
                    if not compare_files(nfs_file_path, static_file_path):
                        logger.info("updating %s content", nfs_file_path)
                        logger.info('copy from %s to %s', static_file_path, nfs_file_path)
                        shutil.copyfile(static_file_path, nfs_file_path)
                        update_repo = True

                ##############################################################################
                #  This part should be enabled if we decide to update the users project repos
                ##############################################################################   
                # if update_repo:
                #     project_name = get_project_name_from_path(static_file)
                #     logger.info("project_name: %s", project_name)

                #     project_repo_url = get_project_repo(project_name)
                #     logger.info("project_repo_url: %s", project_repo_url)
                #     if project_repo_url is not None:
                #         project_repo_path = '/tmp/update_project_git_repo/%s' % project_name
                #         logger.info("project_repo_path: %s", project_repo_path)
                            
                #         # Clone repo, checkout 'development' branch, override user_input.yaml
                #         # file, commit and push to git
                #         logger.debug("Clone project repo")
                #         repo_instance = clone_repo(git_ssh_cmd,project_repo_url, project_repo_path, branch)
                #         logger.debug("Checkeout branch %s", branch)
                #         checkout_branch(git_ssh_cmd, repo_instance, branch)
                #         config_path = os.path.join(repo_instance,'user_input.yaml')
                #         modify_config(static_file_path, env, config_path)
                #         logger.debug("Commit changes of %s for rule %s in environment %s", config_path, static_file_path, env)
                #         commit_changes(git_ssh_cmd, repo_instance, branch, project_name)
                #         logger.debug("Push changes")
                #         push_changes(git_ssh_cmd, repo_instance, branch)


process = UpdatePrometheus()
process.main()
