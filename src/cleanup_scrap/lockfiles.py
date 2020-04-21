#https://stackoverflow.com/questions/7829499/using-hashlib-to-compute-md5-digest-of-a-file-in-python-3
#https://stackoverflow.com/questions/32815640/how-to-get-the-difference-between-two-dictionaries-in-python

import hashlib
from functools import partial
from filelock import FileLock
import shutil
import logging
logger = logging.getLogger(__name__)

lock_path = "deploy.lock"
source_dir = '/Users/devops/Documents/github/prometheus/prometheus/qa/static_files/project1-blackbox.yaml'
destination_dir = '/Users/devops/Documents/github/prometheus/prometheus/qa/static_files/project2-blackbox.yaml'
base_file_checksum = []
backup_file_checksum = []


def md5sum(filename):
    with open(filename, mode='rb') as f:
        d = hashlib.md5()
        for buf in iter(partial(f.read, 128), b''):
            d.update(buf)
    return d.hexdigest()


def lockfiles_setup(base_file, backup_file):
    logger.info("locking file - base_file: %s", base_file)
    logger.info("locking file - backup_file: %s", backup_file)
    base_file_checksum.append(md5sum(base_file))
    backup_file_checksum.append(md5sum(backup_file))
    lock = FileLock(lock_path)
    with lock:
        logger.info("-" * 50)
        logger.debug("\nbefore lock...")
    lock.acquire()
    try:
        logger.info("-" * 50)
        logger.debug("during lock...")
        logger.info("-" * 50)
        try:
            shutil.copy2(base_file, backup_file)
        except:
            logger.debug("unable to write to destination")
            raise SystemExit

    finally:
        logger.info("-" * 50)
        logger.debug("releasing lock...")
        lock.release()


lockfiles_setup(source_dir, destination_dir)
print("df", base_file_checksum, backup_file_checksum)

