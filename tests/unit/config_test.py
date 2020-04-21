import mock
import os
import pytest
import yaml
from validate_email import validate_email

monitoring_items_in_requirements = []
requirements_monitoring_yaml = ['project', 'namespace', 'notification', 'tools', 'modules', 'target', 'elastalert']
requirements_cleanup_yaml = ['server', 'topic', 'delete_topic']
available_namespaces = ['demo', 'services']
available_project_name_extensions = ['service', 'transform', 'sync']
env_in_list = ['aws-stg', 'aws']

monitoring_out_list = []
cleanup_out_list = []

ea_items_in_config = []
ea_out_list = []
targets_items_in_config = []
targets_out_list = []


@pytest.mark.file_unit
def test_is_yaml(filename):
    assert filename.endswith('.yaml'), True

# @pytest.mark.name_unit
# def test_print_name(name):
#     print("Displaying name: %s" % name)


@pytest.mark.config_unit
def test_monitoring_values(filename):
    with open(filename, 'r') as stream:
        out = yaml.load(stream)
        # project to monitor
        monitoring_items_in_requirements.append(out['monitoring'])
        ea_items_in_config.append(out['monitoring']['elastalert']['query'])
        targets_items_in_config.append(out['monitoring']['target'])

    for i in monitoring_items_in_requirements:
        for k, v in i.items():
            monitoring_out_list.append(k)
        assert len(monitoring_out_list) == len(requirements_monitoring_yaml) and sorted(monitoring_out_list) == sorted(requirements_monitoring_yaml)

    for i in ea_items_in_config:
        for k, v in i.items():
            ea_out_list.append(k)
        assert len(ea_out_list) == len(env_in_list) and sorted(ea_out_list) == sorted(env_in_list)

    for i in targets_items_in_config:
        for k, v in i.items():
            targets_out_list.append(k)
        assert len(targets_out_list) == len(env_in_list) and sorted(targets_out_list) == sorted(env_in_list)


cleanup_items_in_requirements = []
@pytest.mark.config_unit
def test_cleanup_values(filename):
    with open(filename, 'r') as stream:
        out = yaml.load(stream)
        # project to cleanup
        cleanup_items_in_requirements.append(out['kafka'])
    for j in cleanup_items_in_requirements:
        for k, v in j.items():
            cleanup_out_list.append(k)
        assert len(cleanup_out_list) == len(requirements_cleanup_yaml) and sorted(cleanup_out_list) == sorted(requirements_cleanup_yaml)

email_list_in_requirements = []
#total_email_list = []
@pytest.mark.config_unit
def test_validate_email(filename):
    with open(filename, 'r') as stream:
        out = yaml.load(stream)
        email_list_in_requirements.append(out['monitoring']['notification']['email'])
    for i in email_list_in_requirements:
        for j in i:
            is_valid = validate_email(j)
            assert is_valid

pagerduty_servicekey_in_requirements = []
# service key should be string(alphanumeric)
@pytest.mark.config_unit
def test_pagerduty_servicekey(filename):
    with open(filename, 'r') as stream:
        out = yaml.load(stream)
        pagerduty_servicekey_in_requirements.append(out['monitoring']['notification']['pagerduty']['service_key'])
    for i in pagerduty_servicekey_in_requirements:
        for j in i:
            assert (isinstance(j, str))

# namespace should be either: demo or services
@pytest.mark.config_unit
def test_namespace(filename):
    with open(filename, 'r') as stream:
        out = yaml.load(stream)
        namespace_in_requirements = (out['monitoring']['namespace'][0])
        assert namespace_in_requirements in available_namespaces

# project name  should end with: -services -transform -sync
@pytest.mark.config_unit
def test_project_name(filename):
    with open(filename, 'r') as stream:
        out = yaml.load(stream)
        project_in_requirements = (out['monitoring']['project'][0].split('-')[-1])
        assert project_in_requirements in available_project_name_extensions
