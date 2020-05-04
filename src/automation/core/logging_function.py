import logging
import os


# function to define logging
def logger():
    tf_log_level = os.getenv('TF_LOG_LEVEL')
    if tf_log_level is None:
        logging.basicConfig(level='WARNING')
    elif tf_log_level == "DEBUG":
        # log level:logged message:full module path:function invoked:line number of logging call
        log_format = "%(levelname)s:%(message)s:%(pathname)s:%(funcName)s:%(lineno)d"
        logging.basicConfig(level=tf_log_level, format=log_format)
    else:
        valid_log_levels = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG']
        if tf_log_level.upper() not in valid_log_levels:
            print("ERROR: invalid log level \"%{}\".  Allowed log levels: {}"). format(
                tf_log_level, ', '.join(valid_log_levels))
            exit(1)


logger = logging.getLogger(__name__)
# we configure the logging level and format
logger()
