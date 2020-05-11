import re
import ruamel.yaml as yaml
import in_place
from shutil import copyfile
from automation.base.base_function import *
from jinja2 import Environment, FileSystemLoader
from automation.config import config

logger = logging.getLogger(__name__)
current_values_in_prometheus_config = []
alert_route_path = '/mnt/monitoring/prometheus/monitoring'
config_path = '/mnt/monitoring/prometheus/monitoring'
templates_directory = config("TEMPLATES_DIRECTORY")
prometheus_config = config("PROMETHEUS_CONFIG")


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
    logger.debug("[prometheus] file location: [{}]" .format(prometheus_fileloc))
    logger.debug("[prometheus] rules dir: [{}]" .format(prometheus_rules_dir))
    logger.debug("[prometheus] static files dir: [{}]" .format(prometheus_staticfiles_dir))
    logger.debug("[prometheus] user input env: [{}]".format(user_input_env))
    logger.debug("[prometheus] verifying if config already exists")
    if not os.path.exists(os.path.join(prometheus_rules_dir, user_input_env)):
        try:
            os.makedirs(os.path.join(prometheus_rules_dir, user_input_env))
        except OSError:
            logger.error("[prometheus] directory does not exists")
            pass
    try:
        if prometheus_validate_current_setup(prometheus_fileloc, project_name, convert_list_to_str(modules), user_input_env) == 0:
            try:
                logger.debug('[prometheus] updating config for: %s', user_input_env)
                prometheus_config(prometheus_fileloc, project_name, user_input_env)
            except:
                logger.error("[prometheus] unable to update config")
            try:
                logger.debug("[prometheus] updating rules for:  {}" .format(user_input_env))
                logger.debug("[prometheus] rules dir:  {}" .format(os.path.join(prometheus_rules_dir, user_input_env)))
                logger.debug("[prometheus] sample rule file: {}" .format(monitoring_rules_sample_file))
                logger.debug("[prometheus] project_name [{}] user_input_env [{}]" .format(project_name, user_input_env))
                monitoring_rules_sample_file = get_sample_file(config_yaml, user_input_env, get_application_type(project_name))
                rules_setup(os.path.join(prometheus_rules_dir, user_input_env),
                            monitoring_rules_sample_file, project_name, user_input_env, project_name_without_env)
            except:
                logger.error("[prometheus] unable to setup rules")
            try:
                static_files_setup(prometheus_staticfiles_dir, monitoring_static_file_sample_file,
                    project_name, convert_list_to_array(targets_to_monitor), user_input_env)
            except:
                logger.error("[prometheus] unable to setup static files")
        else:
            logger.debug("[prometheus] there is an existing configuration: " .format(project_name))
            logger.debug("[prometheus] validating if endpoints have changed")
            update_targets(os.path.join(prometheus_staticfiles_dir, user_input_env), project_name,
                convert_list_to_str(targets_to_monitor), convert_list_to_str(modules), user_input_env)
    except BaseException:
        logger.error("[prometheus] verification stage failed")


# ----------------------------------------------------
#
# CHECK WHETHER THE PROJECT ALREADY EXIST IN PROMETHEUS CONFIG FILE
#
# ----------------------------------------------------
def prometheus_validate_current_setup(prometheus_basefile, project, module, env):
    logger.debug("[prometheus] validating if alert is already configured")
    logger.debug("[prometheus] config file: [{}]" .format(prometheus_basefile))
    logger.debug("[prometheus] project name: [{}]" .format(project))
    logger.debug("[prometheus] module name: [{}]" .format(module))
    logger.debug("[prometheus] env name: [{}]" .format(env))
    final_project_name = project + '-' + module
    logger.debug("[prometheus] project to configure: [{}]" .format(final_project_name))
    logger.debug("[prometheus] prometheus config file: [{}]" .format(prometheus_basefile))
    with open(prometheus_basefile, 'r') as stream:
        logger.debug("prometheus basefile: [{}]" .format(prometheus_basefile))
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
        logger.error("[prometheus] no project config exists")
        pass
    try:
        if final_project_name in (str(values)):
            logger.info("[prometheus] config entry already exists for: {}" .format(project))
        else:
            logger.info("[prometheus] config entry does not exist for: {}" .format(project))
            return 0
    except:
        logger.debug("[prometheus] no matching project found")
        pass


# ------------------------------------------------------
#
# ADD THE NEW PROJECT IN PROMETHEUS CONFIG FILE
#
# ------------------------------------------------------
def prometheus_config(prometheus_fileloc, prj_name, env):
    alert_route = []
    alert_receiver = []
    logger.debug("In prometheus_config function")
    logger.debug("[prometheus] updating prometheus rules section")
    logger.debug("[prometheus] taking backup of file")
    copyfile(prometheus_fileloc, prometheus_fileloc + '.bak')
    with open(prometheus_fileloc, "r") as asmr:
        for line in asmr.readlines():
            if "PROMETHEUS RULES FILE LOCATION PATH ABOVE" in line:
                # we have a match,we want something but we before that...
                alert_route += '''  - '{0}/rules/{1}/{2}-blackbox.yaml-updated.yaml'\n'''.format(alert_route_path, env, prj_name)
            alert_route += line
    with open(prometheus_fileloc + "-updated.yaml", "w") as asmw:
        asmw.writelines(alert_route)
    # os.rename(prometheus_fileloc + "-updated.yaml", prometheus_fileloc)
    time.sleep(1)

    logger.info("[prometheus] updating job section")
    #
    # Load Jinja2 template
    #
    logger.debug("[prometheus] templates_directory: {}".format(templates_directory))
    jinja_env = Environment(loader=FileSystemLoader(templates_directory))
    try:
        template = jinja_env.get_template('prometheus_config')
    except:
        logger.error("[prometheus] error parsing jinja template: {}".format(template))
    try:
        with open(prometheus_fileloc + "-updated.yaml", "r") as asmr:
            logger.debug("[prometheus] file to update: {}" .format(prometheus_fileloc + "-updated.yaml"))
            for line in asmr.readlines():
                if "PROMETHEUS JOB SECTION ABOVE" in line:
                    #
                    # render template using data
                    #
                    alert_receiver += (template.render(name=prj_name, env=env))
                alert_receiver += line
    except:
        logger.debug("[prometheus] unable to open file: {}".format(prometheus_fileloc + "-updated.yaml"))
    try:
        with open(prometheus_fileloc + "-updated.yaml", "w") as asmw:
            asmw.writelines(alert_receiver)
    except:
        logger.debug("[prometheus] unable to write to file: {}".format(prometheus_fileloc + "-updated.yaml"))


# ---------------------------------------------------
#
# ADD NEW RULE FOR THE PROJECT 
#
# ---------------------------------------------------
def rules_setup(rules_dir, sample_file, project_name, env, project_name_without_env):
    # current_list_of_projects = []
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
    logger.debug("[prometheus] copying sample file from: {} to: {}" .format(staticfiles_sample_file, full_filename))
    try:
        logger.debug("[prometheus] copying files")
        if not os.path.exists(os.path.join(prometheus_staticfiles_dir, env)):
            os.makedirs(os.path.join(prometheus_staticfiles_dir, env))
        copyfile(staticfiles_sample_file, full_filename)
    except:
        logger.error("[prometheus] unable to copy static-file: {}" .format(staticfiles_sample_file))
        raise SystemExit
    # for (dirpath, dirnames, filenames) in os.walk(os.path.join(prometheus_staticfiles_dir, env)):
    #     current_list_of_projects.extend(filenames)
    #     break
    logger.debug("[prometheus] trying to open static file")
    f = open(full_filename, 'r')
    filedata = f.read()
    f.close()
    # todo: move to sample file format
    logger.debug("[prometheus] job name: {}" .format(project_name))
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
    logger.debug("[prometheus] static-files location: {}" .format(prometheus_staticfiles_dir))
    logger.debug("[prometheus] project_name: {}" .format(project_name))
    logger.debug("[prometheus] currently configured endpoints: {}" .format(end_point))
    modules = ([y for x in modules for y in x])
    modules = ''.join(modules)
    logger.debug("[prometheus] modules: {}" .format(modules))
    logger.debug("[prometheus] static file: {}" .format(static_file))
    project_filename = project_name + '-' + modules
    logger.debug("[prometheus] job name: {}" .format(project_filename))
    try:
        with open(static_file, 'r') as stream:
            out = yaml.load(stream, Loader=yaml.Loader)
            logger.debug("[prometheus]  output as json: {}" .format(out))
            if (out[0]['labels']['job']) == project_filename:
                old_targets.append(out[0]['targets'])
                new_targets.append(end_point)
        new_targets_string = " ".join(str(x) for x in new_targets)
        logger.debug("[prometheus] new target: {}" .format(new_targets_string))
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
        logger.debug("[prometheus] files does not exist: {}" .format(static_file))


# --------------------------------------------------
#
# APPLY CHANGES TO NFS/EFS AND GITHUB FOR PROMETHEUS
#
# --------------------------------------------------
def update_prometheus(env,
                      project_name,
                      monitoring_config_file_path,
                      monitoring_rules_dir,
                      monitoring_static_file_dir
                      ):
    try:
        logger.debug("[prometheus] updating repo")
        update_prometheus_rules_dir(os.path.join(monitoring_rules_dir, env))
        update_prometheus_staticfiles_dir(os.path.join(monitoring_static_file_dir, env))
        update_prometheus_config(monitoring_config_file_path)
        #update_github_prometheus(os.path.join(monitoring_rules_dir, env),
                                #  os.path.join(monitoring_static_file_dir, env),
                                # monitoring_config_file_path,
                                #  project_name,
                                #  env)
    except BaseException:
        logger.error("[prometheus] config file does not exist or failed to update")


def update_prometheus_config(prometheus_config_file):
    logger.debug("[prometheus] updating config file")
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
            logger.error("[prometheus] can't move %s", prometheus_config_file + "-updated.yaml")
        if os.path.exists(prometheus_config_file + "-updated.yaml"):
            os.remove(prometheus_config_file + "-updated.yaml")


def update_prometheus_rules_dir(prometheus_rules_dir):
    logger.debug("[prometheus] rules dir: {}" .format(prometheus_rules_dir))
    files = os.listdir(prometheus_rules_dir)
    for rule_file in files:
        if "-updated.yaml" in rule_file:
            rule_file_name = rule_file.replace("-updated.yaml", "")
            logger.info("[prometheus] rule file name %s and rule file %s ", rule_file_name, rule_file)
            try:
                if os.path.exists(os.path.join(prometheus_rules_dir, rule_file_name)):
                    logger.debug("[prometheus] removing rule file name  %s", os.path.join(prometheus_rules_dir, rule_file_name))
                    os.remove(os.path.join(prometheus_rules_dir, rule_file_name))
            except BaseException:
                logger.debug("[prometheus] unable to delete file: %s", os.path.join(prometheus_rules_dir, rule_file_name))
                pass
            try:
                # shutil.move(rule_file, rule_file_name)
                logger.debug("[prometheus] renaming [{}] to [{}]" .format(rule_file, rule_file_name))
                os.rename(os.path.join(prometheus_rules_dir, rule_file), os.path.join(prometheus_rules_dir, rule_file_name))
                time.sleep(1)
            except OSError:
                logger.error("[prometheus] can't move %s", os.path.join(prometheus_rules_dir, rule_file))
            if os.path.exists(os.path.join(prometheus_rules_dir, rule_file)):
                logger.debug("[prometheus] removing file name  %s", os.path.join(prometheus_rules_dir, rule_file))
                os.remove(os.path.join(prometheus_rules_dir, rule_file))


def update_prometheus_staticfiles_dir(prometheus_staticfiles_dir):
    logger.debug("[prometheus] update static files dir")
    files = os.listdir(prometheus_staticfiles_dir)
    for static_file in files:
        if "-updated.yaml" in static_file:
            static_file_name = static_file.replace("-updated.yaml", "")
            logger.debug("[prometheus] static_file_name {} and static_file: {}" .format(static_file_name, static_file))
            try:
                if os.path.exists(os.path.join(prometheus_staticfiles_dir, static_file_name)):
                    logger.debug("[prometheus] removing  static file: %s", os.path.join(prometheus_staticfiles_dir, static_file_name))
                    os.remove(os.path.join(prometheus_staticfiles_dir, static_file_name))
            except BaseException:
                logger.error("[prometheus] unable to delete file: %s", os.path.join(prometheus_staticfiles_dir, static_file_name))
                pass
            try:
                # shutil.move(static_file, static_file_name)
                logger.debug("[prometheus] renaming %s to  %s", static_file, static_file_name)
                os.rename(os.path.join(prometheus_staticfiles_dir, static_file), os.path.join(prometheus_staticfiles_dir, static_file_name))
                time.sleep(1)
            except OSError:
                logger.error("[prometheus] can't move %s", os.path.join(prometheus_staticfiles_dir, static_file))
            if os.path.exists(os.path.join(prometheus_staticfiles_dir, static_file)):
                logger.debug("[prometheus] removing  static_file  %s", os.path.join(prometheus_staticfiles_dir, static_file))
                os.remove(os.path.join(prometheus_staticfiles_dir, static_file))