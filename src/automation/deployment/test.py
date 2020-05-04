import ruamel.yaml as yaml

try:
    with open('/Users/varun.tomar/Documents/personal_github/automation/src/config.yaml', 'r') as stream:
        try:
            out_config = yaml.load(stream, Loader=yaml.Loader)
            print("[elastalert] out_config:--- ", out_config)
        except yaml.YAMLError as e:
            print(e)
except IOError:
    print('error')