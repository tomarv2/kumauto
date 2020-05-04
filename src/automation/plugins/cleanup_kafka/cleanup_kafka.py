import time
import logging
from base.base_function import *

logger = logging.getLogger(__name__)


class CleanupKafka:
    def __init__(self):
        pass

    def delete_topic(self, zk_server_with_node, topic_name, zk_node, kafka_image, zk_server):
        topic_list = get_topic(kafka_image, zk_server_with_node)
        logger.error('topic to be deleted: %s', topic_name.strip())
        topics = []
        for i in topic_list:
            topics.append(i.decode("utf-8").split('\n'))
        for topic in topics:
            for i in topic:
                if topic_name in i:
                    logger.error(f'updating topic retention: {topic_name}')
                    update_topic_retention(kafka_image, zk_server_with_node, topic_name)
                    logger.error(f'describe topic: {topic_name}')
                    logger.error(describe_topic(kafka_image, zk_server_with_node, topic_name))
                    time.sleep(30)
                    logger.error(f'deleting topic: {topic_name}')
                    delete_topic(kafka_image, zk_server_with_node, topic_name)
                    logger.error(f'topic deleted from kafka: {topic_name}')
                    try:
                        logger.error(f'cleaning topic: {topic_name} from zookeeper: {zk_server_with_node}')
                        try:
                            logger.error(f'starting cleanup: topic: {topic_name} cleaned for zookeeper: {zk_server}')
                            if get_zk(zk_server, zk_node, topic_name) == 0:
                                logger.error(f'topic: {topic_name} cleaned for zookeeper: {zk_server}')
                        except:
                            logger.error(f'topic: {topic_name} does not exist in zookeeper: {zk_server_with_node}')
                    except:
                        raise SystemExit

