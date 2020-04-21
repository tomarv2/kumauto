import os
from git import Repo, Git
import hashlib
from core.logging_function import logger


def update_repo(git_ssh_cmd, repo_path, branch):
    logger.info("=" * 75)
    logger.info("update repo...")
    with Git().custom_environment(GIT_SSH_COMMAND=git_ssh_cmd):
        os.environ['GIT_SSH_COMMAND'] = git_ssh_cmd
        repo_instance = Repo(repo_path)
        repo_instance.git.checkout(branch)
        repo_instance.git.reset('--hard', branch)
        repo_instance.git.pull()
        return repo_instance


def clone_repo(git_ssh_cmd, repo_url, repo_path, clone_branch):
    logger.info("clone repo...")
    with Git().custom_environment(GIT_SSH_COMMAND=git_ssh_cmd):
        os.environ['GIT_SSH_COMMAND'] = git_ssh_cmd
        repo_instance = Repo.clone_from(
            repo_url, repo_path, branch=clone_branch)
        return repo_instance


def checkout_branch(git_ssh_cmd, repo_instance, new_branch):
    logger.info("checkout branch, function")
    with Git().custom_environment(GIT_SSH_COMMAND=git_ssh_cmd):
        os.environ['GIT_SSH_COMMAND'] = git_ssh_cmd
        git = repo_instance.git
        try:
            logger.debug("checking out branch: %s", new_branch)
            git.checkout('-B', new_branch)
            # repo_instance.git.pull('origin',new_branch)
        except BaseException:
            raise SystemExit
        logger.info("end checkout branch...")


def commit_changes(git_ssh_cmd, repo_instance, branch, project_name):
    logger.info("commit changes...")
    with Git().custom_environment(GIT_SSH_COMMAND=git_ssh_cmd):
        os.environ['GIT_SSH_COMMAND'] = git_ssh_cmd
        try:
            repo_instance.git.pull('origin', branch)
            repo_instance.git.add('.')
            repo_instance.git.commit(
                '-m', '''Updates pushed using automation repo''')
            logger.debug('end commit changes')
        except BaseException:
            logger.error('elastalert: error/nothing to commit...')


def push_changes(git_ssh_cmd, repo_instance, branch):
    logger.info("push changes...")
    with Git().custom_environment(GIT_SSH_COMMAND=git_ssh_cmd):
        try:
            os.environ['GIT_SSH_COMMAND'] = git_ssh_cmd
            repo_instance.git.push('-f', '-u', 'origin', branch)
            logger.info('end push changes')
        except BaseException:
            logger.error('unable to push changes to git...')


