import yaml
import in_place
import sys
from shutil import copyfile
from itertools import islice
import logging
logger = logging.getLogger(__name__)

job_name = 'pipelinesample-sync-team'
sourcefile = 'alertmanager.yaml'
fileloc = 'alertmanager.yaml'
prj_name = 'pipelinesample-sync-team'
tools = 'alertmanager'

d1 = {}
v1 = []
main_list = []

print("taking backup of file...")
copyfile(sourcefile, sourcefile + '.bak')


def update_values(file_to_update, old, new):
    with in_place.InPlace(file_to_update) as file:
        for line in file:
            line = line.replace(old, new)
            file.write(line)
    sys.stdout.write(line)


def update_values(file_to_update, old, new):
    with in_place.InPlace(file_to_update) as file:
        for line in file:
            line = line.replace(old, new)
            file.write(line)


def get_value(file_to_update, end_point):
    print("file_to_update: ", file_to_update)
    print("endpoint: ", end_point)
    with open(file_to_update, 'r') as stream:
        main_list = []
        out = yaml.load(stream)
        print("updating 1st dict: ")
        main_list.append((out['receivers']))
        main_list = ([y for x in main_list for y in x])

        for l in main_list:
            d5 = {}
            d5.update(l)
            for (k1, v1), (k2, v2) in zip(d5.items(), islice(d5.items(), 1, None)):
                list_1 = []
                if v1 == job_name:
                    for i in v2:
                        list_1.append(i)
                d6 = {}
                for i in list_1:
                    d6.update(i)
                for k,v in d6.items():
                    if k == 'to':
                        print (v,k)
                        if v != end_point:
                            update_values(file_to_update, v, end_point)
        raise SystemExit


to_email_list = 'varun@a.com,tomar@b.com'
logger.info("fileloc: %s", fileloc)
logger.info("project name: %s", prj_name)
logger.info("to_email_list: %s", to_email_list)
tag = "# DO NOT REMOVE TAG:" + prj_name
final_to_email_list = to_email_list + ' ' + tag
