import ruamel.yaml as yaml
import logging

logger = logging.getLogger(__name__)

try:
    with open('/Users/varun.tomar/Documents/personal_github/mauto/src/automation/config.yaml', 'r') as stream:
        try:
            out_config = yaml.load(stream, Loader=yaml.Loader)
            logger.debug("[elastalert] out_config:--- ", out_config)
        except yaml.YAMLError as e:
            logger.error(e)
except IOError:
    logger.error('error')
