"""
JobbergateCliOps.
"""
import logging
import subprocess

from shutil import rmtree

from pathlib import Path


logger = logging.getLogger()


class JobbergateCliOps:
    """Track and perform jobbergate-cli ops."""

    _JOBBERGATE_CLI_PACKAGE_NAME = "jobbergate-cli"
    _LOG_DIR = Path("/var/log/jobbergate-cli")
    _CONFIG_DIR = Path("/etc/jobbergate-cli")
    _ETC_DEFAULT = Path("/etc/default/jobbergate-cli")
    _SYSTEMD_BASE_PATH = Path("/usr/lib/systemd/system")
    _JOBBERGATE_CLI_VENV_DIR = Path("/srv/jobbergate-cli-venv")
    _PIP_CMD = _JOBBERGATE_CLI_VENV_DIR.joinpath("bin", "pip3").as_posix()

    def __init__(self, charm):
        """Initialize jobbergate-cli-ops."""
        self._charm = charm

    def install(self):
        """Install jobbergate-cli and setup ops."""
        pypi_url = self._charm.model.config["pypi-url"]
        pypi_username = self._charm.model.config["pypi-username"]
        pypi_password = self._charm.model.config["pypi-password"]

        # Create log dir
        if not self._LOG_DIR.exists():
            self._LOG_DIR.mkdir(parents=True)

        # Create config dir
        if not self._CONFIG_DIR.exists():
            self._CONFIG_DIR.mkdir(parents=True)

        # Create the virtualenv
        create_venv_cmd = [
            "python3",
            "-m",
            "venv",
            self._JOBBERGATE_CLI_VENV_DIR.as_posix(),
        ]
        subprocess.call(create_venv_cmd)
        logger.debug("jobbergate-cli virtualenv created")

        # Ensure we have the latest pip
        upgrade_pip_cmd = [
            self._PIP_CMD,
            "install",
            "--upgrade",
            "pip",
        ]
        subprocess.call(upgrade_pip_cmd)

        # Install PyYAML
        subprocess.call(["./src/templates/install_pyyaml.sh"])

        # Install jobbergate-cli
        url = pypi_url.split("://")[1]
        pip_install_cmd = [
            self._PIP_CMD,
            "install",
            "-f",
            f"https://{pypi_username}:{pypi_password}@{url}",
            self._JOBBERGATE_CLI_PACKAGE_NAME,
        ]
        out = subprocess.check_output(pip_install_cmd).decode().strip()
        if "Successfully installed" not in out:
            logger.error("Trouble installing jobbergate-cli, please debug")
        else:
            logger.debug("jobbergate-cli installed")

    def upgrade(self, version: str):
        """Upgrade jobbergate-cli."""
        pypi_url = self._charm.model.config["pypi-url"]
        pypi_username = self._charm.model.config["pypi-username"]
        pypi_password = self._charm.model.config["pypi-password"]

        url = pypi_url.split("://")[1]
        pip_install_cmd = [
            self._PIP_CMD,
            "install",
            "--upgrade",
            "-f",
            f"https://{pypi_username}:{pypi_password}@{url}",
            f"{self._JOBBERGATE_CLI_PACKAGE_NAME}=={version}",
        ]

        out = subprocess.check_output(pip_install_cmd).decode().strip()
        if "Successfully installed" not in out:
            logger.error("Trouble upgrading jobbergate-cli, please debug")
        else:
            logger.debug("jobbergate-cli installed")

    def configure_etc_default(self):
        """Get the needed config, render and write out the file."""
        charm_config = self._charm.model.config
        backend_base_url = charm_config.get("backend-base-url")
        log_base_dir = str(self._LOG_DIR)

        ctxt = {
            "backend_base_url": backend_base_url,
            "log_dir": log_base_dir,
        }

        etc_default_template = Path(
            "./src/templates/jobbergate-cli.defaults.template").read_text()

        rendered_template = etc_default_template.format(**ctxt)

        if self._ETC_DEFAULT.exists():
            self._ETC_DEFAULT.unlink()

        self._ETC_DEFAULT.write_text(rendered_template)

    def remove_jobbergate_cli(self):
        """
        Remove the things we have created.
        """
        self._ETC_DEFAULT.unlink()
        rmtree(self._CONFIG_DIR.as_posix())
        rmtree(self._LOG_DIR.as_posix())
        rmtree(self._JOBBERGATE_CLI_VENV_DIR.as_posix())
