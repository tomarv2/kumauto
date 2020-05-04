import logging
import ruamel.yaml as yaml
basefile_list = '/Users/varun.tomar/Documents/personal_github/mauto/data/demo-data/monitoring/config.yaml'

with open(basefile_list, 'r') as stream:
    print("loading the yaml")
    out = yaml.load(stream, Loader=yaml.Loader)
    print(out['route'])

