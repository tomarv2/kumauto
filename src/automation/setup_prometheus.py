import os
import re
import time
import ruamel.yaml as yaml
import logging
import sys
sys.path.append("..")


import in_place
from shutil import copyfile
logger = logging.getLogger(__name__)
from automation.core.base_function import *
from .git_push_prometheus import update_github_prometheus

current_values_in_prometheus_config = []


# ----------------------------------------------------
#
# BUILD THE FILES OF PROMETHEUS
#
# ----------------------------------------------------
def build_prometheus(config_yaml,
                     user_input_env,
                     monitoring_config_file_path,
                     monitoring_rules_dir,
                     monitoring_static_file_dir,
                     project_name,
                     targets_to_monitor,
                     monitoring_rules_sample_file,
                     monitoring_static_file_sample_file,
                     modules,
                     project_name_without_env
                     ):
    prometheus_fileloc = monitoring_config_file_path
    prometheus_rules_dir = monitoring_rules_dir
    prometheus_staticfiles_dir = monitoring_static_file_dir
    logger.debug("[prometheus] file location: %s", prometheus_fileloc)
    logger.debug("[prometheus] rules dir: %s", prometheus_rules_dir)
    logger.debug("[prometheus] static_files dir: %s", prometheus_staticfiles_dir)
    logger.debug("[prometheus] verifying if config already exists...")
    if not os.path.exists(os.path.join(prometheus_rules_dir, user_input_env)):
        try:
            os.makedirs(os.path.join(prometheus_rules_dir, user_input_env))
        except OSError:
            logger.debug("[prometheus] directory does not exist...")
            pass
    try:
        if prometheus_validate_current_setup(prometheus_fileloc, project_name, convert_list_to_str(modules), user_input_env) == 0:
            try:
                logger.debug('[prometheus] updating config for: %s', user_input_env)
                prometheus_config(prometheus_fileloc, project_name, user_input_env)
            except:
                logger.debug("[prometheus] unable to update config...")
            try:
                logger.debug('[prometheus] updating rules for: %s', user_input_env)
                logger.debug('[prometheus] rules dir: %s', os.path.join(prometheus_rules_dir, user_input_env))
                logger.debug("[prometheus] sample rule file :%s", monitoring_rules_sample_file)
                logger.debug("[prometheus] project_name and user_input_env: %s, %s", project_name, user_input_env)
                monitoring_rules_sample_file = get_sample_file(config_yaml, user_input_env, get_application_type(project_name))
                rules_setup(os.path.join(prometheus_rules_dir, user_input_env),
                            monitoring_rules_sample_file, project_name, user_input_env, project_name_without_env)
            except:
                logger.error('[prometheus] unable to setup rules...')
            try:
                logger.error('[prometheus] updating static files for: %s', user_input_env)
                static_files_setup(prometheus_staticfiles_dir, monitoring_static_file_sample_file,
                    project_name, convert_list_to_array(targets_to_monitor), user_input_env)
            except:
                logger.error('[prometheus] unable to setup static files...')
        else:
            logger.debug("[prometheus] there is an existing configuration: %s", project_name)
            logger.debug("[prometheus] validating if endpoints have changed...")
            update_targets(os.path.join(prometheus_staticfiles_dir, user_input_env), project_name,
                convert_list_to_str(targets_to_monitor), convert_list_to_str(modules), user_input_env)
    except BaseException:
        logger.error("[prometheus] verification stage failed...")


# ----------------------------------------------------
#
# CHECK WHETHER THE PROJECT ALREADY EXIST IN PROMETHEUS CONFIG FILE
#
# ----------------------------------------------------
def prometheus_validate_current_setup(prometheus_basefile, project, module, env):
    logger.debug("[prometheus] validating if alert already exists...")
    logger.debug("[prometheus] config file: %s", prometheus_basefile)
    logger.debug("[prometheus] project name: %s", project)
    logger.debug("[prometheus] module name: %s", module)
    logger.debug("[prometheus] env name: %s", env)
    final_project_name = project + '-' + module
    logger.error("[prometheus] final configured project name: %s", final_project_name)
    with open(prometheus_basefile, 'r') as stream:
        out = yaml.load(stream, Loader=yaml.Loader)
        try:
            current_values_in_prometheus_config.append(out['scrape_configs'])
        except BaseException:
            logger.error("[prometheus] unable to get list of currently monitored projects, exiting...")
            raise SystemExit
    values = []
    try:
        for i in [x for x in current_values_in_prometheus_config]:
            for j in i:
                values.append(j)
    except:
        logger.error("[prometheus] no project config exists...")
        pass
    try:
        if final_project_name in (str(values)):
            logger.error("[prometheus] config entry already exists for: %s", project)
        else:
            logger.error("[prometheus] config entry does not exist for: %s", project)
            return 0
    except:
        logger.error("[prometheus] no matching project found...")
        pass


# ------------------------------------------------------
#
# ADD THE NEW PROJECT IN PROMETHEUS CONFIG FILE
#
# ------------------------------------------------------
def prometheus_config(prometheus_fileloc, prj_name, env):
    alert_route = []
    alert_receiver = []
    logger.debug("In prometheus_config function...")
    logger.debug("[prometheus] updating prometheus rules section...")
    logger.debug("[prometheus] taking backup of file...")
    copyfile(prometheus_fileloc, prometheus_fileloc + '.bak')
    with open(prometheus_fileloc, "r") as asmr:
        for line in asmr.readlines():
            if "PROMETHEUS RULES FILE LOCATION PATH ABOVE" in line:
                # we have a match,we want something but we before that...
                alert_route += '''  - '/mnt/monitoring/prometheus/monitoring/rules/{0}/{1}-blackbox.yaml-updated.yaml'\n'''.format(
                    env, prj_name)
            alert_route += line
    with open(prometheus_fileloc + "-updated.yaml", "w") as asmw:
        asmw.writelines(alert_route)
    # os.rename(prometheus_fileloc + "-updated.yaml", prometheus_fileloc)
    time.sleep(1)

    logger.error("[prometheus] updating job section...")
    # todo: move to sample file format
    with open(prometheus_fileloc + "-updated.yaml", "r") as asmr:
        for line in asmr.readlines():
            if "PROMETHEUS JOB SECTION ABOVE" in line:
                # we have a match,we want something but we before that...
                alert_receiver += '''#################################################################
  - job_name: '{0}-blackbox'
    scrape_interval: 60s
    scrape_timeout: 10s
    metrics_path: /probe
    params:
      module: [http_check]
    file_sd_configs:
      - files:
        - /mnt/monitoring/prometheus/monitoring/static_files/{1}/{0}-blackbox.yaml-updated.yaml
    relabel_configs:
      - source_labels: [__address__]
        regex: (.*)(:80)?
        target_label: __param_target
        replacement: {2}
      - source_labels: [__param_target]
        regex: (.*)
        target_label: instance
        replacement: {2}
      - source_labels: []
        regex: .*
        target_label: __address__
        replacement: prometheus-blackbox:9115
      - source_labels: [checker]
        regex: (.*)
        target_label: __param_module
        replacement: '{2}'\n'''.format(prj_name, env, "${1}")
            alert_receiver += line
    # write the file with the new content
    with open(prometheus_fileloc + "-updated.yaml", "w") as asmw:
        asmw.writelines(alert_receiver)    


# ---------------------------------------------------
#
# ADD NEW RULE FOR THE PROJECT 
#
# ---------------------------------------------------
def rules_setup(rules_dir, sample_file, project_name, env, project_name_without_env):
    #current_list_of_projects = []
    rules_file_name = os.path.join(rules_dir, project_name) + '-blackbox.yaml' + "-updated.yaml"
    logger.debug("[prometheus] rules_setup function...")
    logger.debug("[prometheus] rules dir: %s", rules_dir)
    logger.debug("[prometheus] rules sample file: %s", sample_file)
    logger.debug("[prometheus] rules project_name: %s", project_name)
    try:
        if not os.path.exists(rules_dir):
            os.makedirs(rules_dir)
    except IOError:
        logger.error("[prometheus] unable to create rule folder...")
        raise SystemExit
    try:
        logger.debug("[prometheus] copy sample file: %s to %s", sample_file, rules_file_name)
        copyfile(sample_file, rules_file_name)
    except:
        logger.error("[prometheus] unable to copy files")
        raise SystemExit
    # for (dirpath, dirnames, filenames) in os.walk(rules_dir):
    #     current_list_of_projects.extend(filenames)
    #     break
    # todo: find a better way to do this (to be rewritten)
    with open(rules_file_name, 'r') as f:
        filedata = f.read()
    # todo: find a better way to do this
    newdata = filedata.replace("USER_INPUT_PROJECT_NAME", project_name)
    with open(rules_file_name, 'w') as f:
        f.write(newdata)
    f.close()
    # updating the env
    with open(rules_file_name, 'r') as f:
        filedata = f.read()
    # todo: find a better way to do this
    newdata = filedata.replace("ENVIRONMENT", env.upper())
    with open(rules_file_name, 'w') as f:
        f.write(newdata)
    # extracting the POD NAME
    with open(rules_file_name, 'r') as f:
        filedata = f.read()
    # todo: find a better way to do this
    pod_name = re.sub(r"-service", "-[^sync|transform]", project_name_without_env)
    newdata = filedata.replace("POD_NAME", pod_name)
    with open(rules_file_name, 'w') as f:
        f.write(newdata)


# -----------------------------------------
#
# ADD NEW STATIC FILE FOR THE PROJECT 
#
# -----------------------------------------
def static_files_setup(prometheus_staticfiles_dir, staticfiles_sample_file, project_name, targets_to_monitor, env):
    #current_list_of_projects = []
    logger.debug("[prometheus] static-files dir: %s", os.path.join(prometheus_staticfiles_dir, env))
    logger.debug("[prometheus] static-files sample file: %s", staticfiles_sample_file)
    full_filename = os.path.join(prometheus_staticfiles_dir, env, project_name) + '-blackbox.yaml' + "-updated.yaml"
    logger.debug("[prometheus] static-file name: %s", full_filename)
    logger.debug("[prometheus] trying to delete: %s", project_name)
    # try:
    #     if os.path.isfile(full_filename):
    #         os.remove(full_filename)
    # except BaseException:
    #     logger.error("[prometheus] unable to delete file: %s",project_name)
    #     pass
    logger.debug("[prometheus] copying sample file from: %s to: %s", staticfiles_sample_file, full_filename)
    try:
        logger.debug("[prometheus] trying...")
        if not os.path.exists(os.path.join(prometheus_staticfiles_dir, env)):
            os.makedirs(os.path.join(prometheus_staticfiles_dir, env))
        copyfile(staticfiles_sample_file, full_filename)
    except:
        logger.error("[prometheus] unable to copy static-file: %s", staticfiles_sample_file)
        raise SystemExit
    # for (dirpath, dirnames, filenames) in os.walk(os.path.join(prometheus_staticfiles_dir, env)):
    #     current_list_of_projects.extend(filenames)
    #     break
    logger.debug("[prometheus] trying to open static file...")
    f = open(full_filename, 'r')
    filedata = f.read()
    f.close()
    # todo: move to sample file format
    logger.debug("[prometheus] job name: %s", project_name)
    newdata = filedata.replace("USER_INPUT_PROJECT_NAME", project_name)

    f = open(full_filename, 'w')
    f.write(newdata)
    f.close()
    ###################
    # logger.error("[prometheus] trying to delete: %s", project_name)
    # try:
    #     if os.path.isfile(full_filename):
    #         os.remove(full_filename)
    #
    # except:
    #     logger.error("[prometheus] unable to delete file: %s", project_name)
    #     pass

    f = open(full_filename, 'r')
    filedata = f.read()
    f.close()
    newdata = filedata.replace("USER_INPUT_ENDPOINT", targets_to_monitor)
    f = open(full_filename, 'w')
    f.write(newdata)
    f.close()


# --------------------------------------------
#
# UPDATE THE TARGETS IN THE STATIC FILES 
#
# --------------------------------------------
def update_targets(prometheus_staticfiles_dir, project_name, end_point, modules, env):
    old_targets = []
    new_targets = []
    clean_list = []
    prometheus_staticfiles_dir = ([y for x in prometheus_staticfiles_dir for y in x])
    prometheus_staticfiles_dir = ''.join(prometheus_staticfiles_dir)
    static_file = os.path.join(prometheus_staticfiles_dir, project_name + '-' + modules + '.yaml')
    logger.debug("[prometheus] static-files location: %s", prometheus_staticfiles_dir)
    logger.debug("[prometheus] project_name: %s", project_name)
    logger.debug("[prometheus] currently configured endpoints: %s", end_point)
    modules = ([y for x in modules for y in x])
    modules = ''.join(modules)
    logger.debug("[prometheus] modules: %s", modules)
    logger.debug("[prometheus] static file: %s", static_file)
    project_filename = project_name + '-' + modules
    logger.debug("[prometheus] job name: %s", project_filename)
    try:
        with open(static_file, 'r') as stream:
            out = yaml.load(stream)
            logger.error("[prometheus]  output as json: %s", out)
            if (out[0]['labels']['job']) == project_filename:
                old_targets.append(out[0]['targets'])
                new_targets.append(end_point)
        new_targets_string = " ".join(str(x) for x in new_targets)
        logger.error("[prometheus] new target: %s", new_targets_string)
        for i in old_targets:
            for j in i:
                clean_list.append(j)
        copyfile(static_file, static_file + "-updated.yaml")
        with in_place.InPlace(static_file + "-updated.yaml") as file:
            for line in file:
                line = line.replace(
                    "".join(
                        str(clean) for clean in clean_list), " ".join(
                        str(x) for x in new_targets))
                file.write(line)
    except IOError:
        logger.error("[prometheus] files does not exist: %s", static_file)


# --------------------------------------------------
#
# APPLY CHANGES TO NFS/EFS AND GITHUB FOR PROMETHEUS
#
# --------------------------------------------------
def update_prometheus(env, project_name, monitoring_config_file_path, monitoring_rules_dir, monitoring_static_file_dir):
    try:
        logger.error("promethues: updating repo...")
        update_prometheus_rules_dir(os.path.join(monitoring_rules_dir, env))
        update_prometheus_staticfiles_dir(os.path.join(monitoring_static_file_dir, env))
        update_prometheus_config(monitoring_config_file_path)
        update_github_prometheus(os.path.join(monitoring_rules_dir, env), os.path.join(monitoring_static_file_dir, env),
                                monitoring_config_file_path, project_name, env)
    except BaseException:
        logger.error("promethues: failed to update prometheus files...")


def update_prometheus_config(prometheus_config_file):
    if os.path.exists(prometheus_config_file + "-updated.yaml"):
        with open(prometheus_config_file + "-updated.yaml", 'U') as f:
            newContent = f.read()
            while "-updated.yaml" in newContent:
                newContent=newContent.replace("-updated.yaml", "")
        with open(prometheus_config_file + "-updated.yaml", "w") as f:
            f.write(newContent)  
        try:
            # shutil.move(prometheus_config_file + "-updated.yaml", prometheus_config_file)
            os.rename(prometheus_config_file + "-updated.yaml", prometheus_config_file)
            time.sleep(1)
        except OSError:
            logger.error("can't move %s", prometheus_config_file + "-updated.yaml")
        if os.path.exists(prometheus_config_file + "-updated.yaml"):
            os.remove(prometheus_config_file + "-updated.yaml")


def update_prometheus_rules_dir(prometheus_rules_dir):
    files = os.listdir(prometheus_rules_dir)
    for rule_file in files:
        if "-updated.yaml" in rule_file:
            rule_file_name = rule_file.replace("-updated.yaml", "")
            logger.error("rule_file_name %s and rule_file %s ", rule_file_name, rule_file)
            try:
                if os.path.exists(os.path.join(prometheus_rules_dir, rule_file_name)):
                    logger.error("removing  rule_file_name  %s", os.path.join(prometheus_rules_dir, rule_file_name))
                    os.remove(os.path.join(prometheus_rules_dir, rule_file_name))
            except BaseException:
                logger.error("[prometheus] unable to delete file: %s", os.path.join(prometheus_rules_dir, rule_file_name))
                pass
            try:
                # shutil.move(rule_file, rule_file_name)
                logger.error("renaming %s to  %s", rule_file, rule_file_name)
                os.rename(os.path.join(prometheus_rules_dir, rule_file), os.path.join(prometheus_rules_dir, rule_file_name))
                time.sleep(1)
            except OSError:
                logger.error("can't move %s", os.path.join(prometheus_rules_dir, rule_file))     
            if os.path.exists(os.path.join(prometheus_rules_dir, rule_file)):
                logger.error("removing  rule_file  %s", os.path.join(prometheus_rules_dir, rule_file))
                os.remove(os.path.join(prometheus_rules_dir, rule_file))


def update_prometheus_staticfiles_dir(prometheus_staticfiles_dir):
    files = os.listdir(prometheus_staticfiles_dir)
    for static_file in files:
        if "-updated.yaml" in static_file:
            logger.error("updating staticfile %s", static_file)
            static_file_name = static_file.replace("-updated.yaml", "")
            logger.error("static_file_name %s and static_file  %s", static_file_name, static_file)
            try:
                if os.path.exists(os.path.join(prometheus_staticfiles_dir, static_file_name)):
                    logger.error("removing  static_file_name  %s", os.path.join(prometheus_staticfiles_dir, static_file_name))
                    os.remove(os.path.join(prometheus_staticfiles_dir, static_file_name))
            except BaseException:
                logger.error("Unable to delete file: %s", os.path.join(prometheus_staticfiles_dir, static_file_name))
                pass
            try:
                # shutil.move(static_file, static_file_name)
                logger.error("renaming %s to  %s", static_file, static_file_name)
                os.rename(os.path.join(prometheus_staticfiles_dir, static_file), os.path.join(prometheus_staticfiles_dir, static_file_name))
                time.sleep(1)
            except OSError:
                logger.error("can't move %s", os.path.join(prometheus_staticfiles_dir, static_file))
            if os.path.exists(os.path.join(prometheus_staticfiles_dir, static_file)):
                logger.error("removing  static_file  %s", os.path.join(prometheus_staticfiles_dir, static_file))
                os.remove(os.path.join(prometheus_staticfiles_dir, static_file))