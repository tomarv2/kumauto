import os
import docker
import hashlib, time
import logging
from staticconf.loader import yaml_loader
from kazoo.client import KazooClient
import ruamel.yaml as yaml

client = docker.from_env()
logger = logging.getLogger(__name__)


def get_application_type(project_name):
    application_type = ([y for x in project_name for y in x])
    application_type = ''.join(application_type)
    try:
        return application_type.split('-')[-1]
    except BaseException:
        return 0


def get_sample_file(config_yaml, env, application_type):
    with open(config_yaml, 'r') as stream_config:
        out_config = yaml.load(stream_config, Loader=yaml.Loader)
        if 'qa' in env:
            if application_type in ['transform', 'spark']:
                return out_config['prometheus']['monitoring']['rules']['qa_sample_file_spark'][0]
            else:
                return out_config['prometheus']['monitoring']['rules']['qa_sample_file'][0]
        else:
            if application_type in ['transform', 'spark']:
                return out_config['prometheus']['monitoring']['rules']['sample_file_spark'][0]
            else:
                return out_config['prometheus']['monitoring']['rules']['sample_file'][0]


def get_alert_type(user_input_env):
    if 'QA' in user_input_env.upper() or 'STG' in user_input_env.upper():
        return 'email'
    else:
        return 'pagerduty'


def convert_list_to_str(list):
    return ','.join([item for array in list for item in array])


def get_index_name(project_name, namespace):
    if get_application_type(project_name) == 'service' or get_application_type(project_name) == 0:
        if namespace == 'demo':
            return 'dw-demo-app-logs-*'
        else:
            return 'dw-services-app-logs-*'
    if get_application_type(project_name) == 'sync':
        return 'nifi-logs-*'
    if get_application_type(project_name) == 'transform':
        return 'spark-logs-*'


def convert_list_to_array(list):
    return '\n  - '.join([item for array in list for item in array])


def parse_query(input_query):
    new_query = input_query.replace("\\", "\\\\")
    new_query = new_query.replace('\"', "\\\"")
    new_query = '\"' + new_query + '\"'
    #logger.error("new query %s", new_query)
    return new_query


def convert_list_to_ea_query(list):
    query_string = '\n- query: \n   query_string:\n    query:  '.join(
        [parse_query(item) for array in list for item in array])
    return query_string


def read_logfile_location(config_yaml):
    with open(config_yaml, 'r') as stream_config:
        out_config = yaml.load(stream_config)
        print("------------")
        print (out_config['log']['filename'])
        return out_config['log']['filename']


def read_log_level(config_yaml):
    with open(config_yaml, 'r') as stream_config:
        out_config = yaml.load(stream_config)
        return out_config['log']['level'][0].upper()


def ensure_dir_exists(dir_name):
    if not os.path.exists(dir_name):
        try:
            print("creating dir: ", dir_name)
            os.makedirs(dir_name)
        except OSError:
            print("Unable to create directory: %s", dir_name)
            pass


def ensure_file_exists_append_mode(file_path):
    print("inside ensure_file_exists_append_mode, filepath: ", file_path)
    dir_name = os.path.dirname(file_path)
    ensure_dir_exists(dir_name)
    if os.path.exists(file_path):
        os.utime(file_path, None)
    else:
        open(file_path, 'a').close()
#ensure_file_exists_append_mode('/tmp/test.txt')


def get_project_name(requirements_yaml_path):
    with open(requirements_yaml_path, 'r') as stream_config:
        out_config = yaml.load(stream_config)
        return out_config['monitoring']['project'][0]


def get_project_name_env(requirements_yaml_path, env):
    with open(requirements_yaml_path, 'r') as stream_config:
        out_config = yaml.load(stream_config)
        return env + '-' + out_config['monitoring']['project'][0]


def convert_list_to_slack_channel(list):
    query_string = '\n    - send_resolved: true \n      api_url: https://hooks.slack.com/services/XYZ\n      channel:  '.join(
        [parse_query(item) for array in list for item in array])
    return query_string


def get_list_env(env):
    list_env = []
    if env in ['aws']:
        list_env.append('aws')
    elif env in ['aws-stg']:
        list_env.append('aws-stg')
    return list_env


def get_topic(kafka_image, zk_server_name):
    get_topics = []
    list_cmd = f'/bin/kafka-topics.sh --zookeeper {zk_server_name} --list'
    #logger.error("get topics cmd: %s", list_cmd)
    get_topics.append(client.containers.run(f'{kafka_image}', list_cmd))
    return get_topics


def describe_topic(kafka_image, zk_server_name, topic_name):
    try:
        describe_cmd = f'/bin/kafka-topics.sh --describe --zookeeper {zk_server_name} --topic {topic_name}'
        #logger.error("describe topics cmd: %s", describe_cmd)
        return (client.containers.run(f'{kafka_image}', describe_cmd))
    except:
        #logger.error(f'unable to describe topic: {topic_name} in zookeeper: {zk_server_name}')
        pass


def update_topic_retention(kafka_image, zk_server_name, topic_name):
    try:
        update_retention_cmd = f'/bin/kafka-topics.sh --zookeeper {zk_server_name} --alter --topic {topic_name} --config retention.ms=1'
        #logger.error("update retention cmd: %s", update_retention_cmd)
        client.containers.run(f'{kafka_image}', update_retention_cmd)
    except:
        #logger.error('topic: {topic_name} does not exists in zookeeper: {zk_server_name}')
        pass


def delete_topic(kafka_image, zk_server_name, topic_name):
    try:
        delete_topic_cmd = f'/bin/kafka-topics.sh --zookeeper {zk_server_name} --delete --topic {topic_name}'
        #logger.error("delete topics cmd: %s", delete_topic_cmd)
        client.containers.run(f'{kafka_image}', delete_topic_cmd)
    except:
        #logger.error(f'unable to delete topic: {topic_name} from zookeeper: {zk_server_name}')
        pass


def get_zk(zk_server_name, node, topic_name):
    zk = KazooClient(hosts=zk_server_name)
    zk.start()
    topic_path = os.path.join('/', node, 'brokers/topics', topic_name)
    #logger.error('topic_path: ', topic_path)
    try:
        if zk.exists(topic_path):
            #logger.error(f'topic exists: {topic_name} in zookeeper: {zk_server_name}')
            try:
                zk.delete(topic_path, recursive=True)
                zk.stop()
                return 0
            except:
                #logger.error('unable to delete topic')
                zk.stop()
                raise SystemExit
        else:
            #logger.error(f'topic: {topic_name} does not exists')
            pass
    except:
        pass
    zk.stop()


def validate_yaml(yaml_file):
    try:
        yaml_loader(yaml_file)
        return True
    except IOError:
        raise Exception('yaml file: %s not found!', yaml_file)
    except yaml.scanner.ScannerError as e:
        raise Exception('Could not parse yaml file %s: %s' % (yaml_file, e))


def cleanup(prometheus_rules_dir, prometheus_static_file_dir, prometheus_config_file_path, alertmanager_config_file_path):
    rules_files = os.listdir(prometheus_rules_dir)
    for rule_file in rules_files:
        if "-updated.yaml" in rule_file:
            try:
                os.remove(os.path.join(prometheus_rules_dir, rule_file))
            except BaseException:
                # logger.error("[prometheus] unable to delete file: %s", os.path.join(prometheus_rules_dir, rule_file))
                pass

    static_files = os.listdir(prometheus_static_file_dir)
    for static_file in static_files:
        if "-updated.yaml" in static_file:
            try:
                os.remove(os.path.join(prometheus_static_file_dir, static_file))
            except BaseException:
                # logger.error("[prometheus] unable to delete file: %s", os.path.join(prometheus_static_file_dir, static_file))
                pass

    if os.path.exists(prometheus_config_file_path + "-updated.yaml"):
        try:
            os.remove(prometheus_config_file_path + "-updated.yaml")
        except BaseException:
            # logger.error("[prometheus] unable to delete file: %s", prometheus_config_file_path + "-updated.yaml")
            pass

    if os.path.exists(alertmanager_config_file_path + "-updated.yaml"):
        try:
            os.remove(alertmanager_config_file_path + "-updated.yaml")
        except BaseException:
            # logger.error("[prometheus] unable to delete file: %s", alertmanager_config_file_path + "-updated.yaml")
            pass


# compare the content of two files, if mismatches, return false
def compare_files(file1, file2):
    # logger.error('comparing files: %s %s' % (file1, file2))
    # logger.error('comparing files...')
    file1_md5 = hashlib.md5(open(file1, 'rb').read()).hexdigest()
    file2_md5 = hashlib.md5(open(file2, 'rb').read()).hexdigest()
    if file1_md5 == file2_md5:
        return True
    else:
        return False


# TO DO: return the repo url of the specified project
def get_project_repo(project_name):
    # logger.error('navigate git repos to extract the project repo path')
    return None


# return the name of the project
def get_project_name_from_path(file_name):
    # logger.error('parse file name to extract project name')
    # TO DO: manage the case where words like spark, transform, nifi, are added
    return os.path.splitext(file_name)[0]


# TO DO: update the config_path (path of user_input.yaml) by adding the rule
# rule_file_path for the environment  env
def modify_config(rule_file_path, env, config_path):
    # logger.error('locate the elastalert queries in the user_input.yaml file in the corresponding project and change them')
    print("locate the elastalert queries in the user_input.yaml file in the corresponding project and change them")


# ensure the path for the added rule exists in prometheus config file
def rule_path_exists(rule_file_path, prometheus_config_path):
    if rule_file_path not in open(prometheus_config_path).read():
        rule_route = []
        with open(prometheus_config_path, "r") as asmr:
            for line in asmr.readlines():
                if "PROMETHEUS RULES FILE LOCATION PATH ABOVE" in line:
                    rule_route += "  - \'%s\'\n" % rule_file_path
                rule_route += line
        with open(prometheus_config_path + "-copy.yaml", "w") as asmw:
            asmw.writelines(rule_route)
        os.rename(prometheus_config_path + "-copy.yaml", prometheus_config_path)
        time.sleep(1)
