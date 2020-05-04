# import logging

from starlette.config import Config

env = '/Users/varun.tomar/Documents/personal_github/mauto/src/automation/.env'
config = Config(env)
#
LOG_LEVEL = "DEBUG"
CONFIG_YAML_FILE = config("CONFIG_YAML_FILE")
REQUIREMENTS_YAML_FILE = config("REQUIREMENTS_YAML_FILE")
USER_INPUT_ENV = config("USER_INPUT_ENV")
