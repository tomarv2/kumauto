from .logging import configure_logging
from .validation import *
from .config import config
import click
from tabulate import tabulate
from automation.plugins.am_setup.am import am_config
from automation.plugins.prometheus_setup.pm import pm_config
from automation.plugins.ea_setup.ea import ea_config

config_yaml = config("CONFIG_YAML_FILE")
requirements_yaml = config("REQUIREMENTS_YAML_FILE")
user_input_env = config("USER_INPUT_ENV")
logger = logging.getLogger(__name__)


@click.group()
def automation_cli():
    """Command-line interface to mauto."""
    configure_logging()

# ----
@automation_cli.group("develop")
def develop_product():
    """Develop components"""
    pass


@develop_product.command("alertmanager")
def develop_am():
    """develop component: alertmanager"""
    am_config()


@develop_product.command("prometheus")
def develop_pm():
    """develop component: prometheus monitoring (monitoring , blackbox)"""
    pm_config()


@develop_product.command("elastalert")
def develop_ea():
    """develop component: elastalert"""
    ea_config()


@develop_product.command('git')
def develop_git():
    """develop component: push to git"""


# ----
@automation_cli.group("components")
def components_group():
    """All commands for component manipulation."""
    pass


@components_group.command("list")
def list_available_components():
    """Shows all available components"""
    table = [['am', '0.1', 'demo', 'demo']]
    # for p in plugins.all():
    #     table.append([p.title, p.slug, p.version, p.type, p.author, p.description])
    click.secho(
        tabulate(table, headers=["Component", "Version", "Author", "Description"]),
        fg="blue",
    )


# -----
@automation_cli.group("remove")
def project_cleanup():
    """Command to remove project"""
    pass


@project_cleanup.command("all", help="all components")
def remove_all_projects():
    """testing"""


@project_cleanup.command("one-component", help="remove one component")
def remove_one_project():
    """testing"""

# -----
@automation_cli.group("deploy")
def all_components():
    """Deploy components: (alertmanager, prometheus, blackbox)"""
    pass


@all_components.command("dryrun", help="no changes are implemented")
def validate_project():
    """testing"""


@all_components.command("all", help="deploy everything")
def test():
    entrypoint_to_all()


def entrypoint_to_all():
    # ----------------------------------------------------
    #
    # Build files entered by user:
    # 1. user_input.yaml
    # 2. config.yaml
    #
    # ----------------------------------------------------
    if validate_yaml(requirements_yaml) and validate_yaml(config_yaml):
        am_config()
        pm_config()
        ea_config()


def entrypoint():
    """The entry that the CLI is executed from"""
    try:
        automation_cli()
    except Exception as e:
        click.secho(f"ERROR: {e}", bold=True, fg="red")


if __name__ == "__main__":
    entrypoint()
