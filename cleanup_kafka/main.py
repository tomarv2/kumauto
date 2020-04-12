import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cleanup_kafka import CleanupKafka
from core.base_function import *
config_yaml = '/automation/config.yaml'  # todo: better arrangement here
requirements_yaml = '/tmp/user_input.yaml'
# config_yaml = '/Users/devops/Documents/bitbucket/automation/config.yaml'  # todo: better arrangement here
# requirements_yaml = '/Users/devops/Documents/bitbucket/automation/user_input.yaml'
from core.logging_function import logger
logger.configure(None)


def main():
    logger.info("Checking the format of yaml file")
    print("validating yaml files...")
    if (validate_yaml(requirements_yaml)) == 0 and validate_yaml(config_yaml) == 0:
        logger.info("validation of yaml passed...")
        with open(requirements_yaml, 'r') as stream:
            out = yaml.load(stream)
            topic_name = []
            topic_name.append(out['kafka']['topic']) # todo: list within list
            delete_topic = out['kafka']['delete_topic']
            broker_name = out['kafka']['server'][0]
            zk_server_with_node = out['zookeeper']['server']
            zk_server = zk_server_with_node.split(':')[0]
            zk_node = zk_server_with_node.split('/')[1]
        with open(config_yaml, 'r') as stream:
            out_config = yaml.load(stream)
            kafka_image = out_config['kafka_docker_image']
        if delete_topic == 'YES_DELETE':
            if zk_server not in out_config['zookeeper_exclude_list']: #['zk.demo.com', 'zk01.demo.com', 'zk02.demo.com', 'zk03.demo.com']:
                print(f'starting deleting topic: {topic_name}')
                cleanup_kafka = CleanupKafka()
                for topic_list in topic_name:
                    for topic in topic_list:
                        cleanup_kafka.delete_topic(zk_server_with_node, topic, zk_node, kafka_image, zk_server)
    else:
        print("unable to parse yaml files")


if __name__ == "__main__":
    main()

