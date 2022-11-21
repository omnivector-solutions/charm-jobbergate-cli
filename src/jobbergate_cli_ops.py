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

    _PACKAGE_NAME = "jobbergate-cli"
    _LOG_DIR = Path("/var/log/jobbergate-cli")
    _VENV_DIR = Path("/srv/jobbergate-cli-venv")
    _PIP_CMD = _VENV_DIR.joinpath("bin", "pip3").as_posix()
    _ETC_DEFAULT = Path("/etc/default/jobbergate-cli")
    _PROFILE = Path("/etc/profile.d/jobbergate-cli.sh")

    def __init__(self, charm):
        """Create class level variables."""
        self._charm = charm

    def _derived_pypi_url(self):
        url = self._charm.model.config["pypi-url"]
        url = url.split("://")[1]
        pypi_username = self._charm.model.config["pypi-username"]
        pypi_password = self._charm.model.config["pypi-password"]
        return f"https://{pypi_username}:{pypi_password}@{url}/simple"

    def install(self):
        """Install package from private pypi."""

        # Create log dir
        if not self._LOG_DIR.exists():
            self._LOG_DIR.mkdir(parents=True)

        # Create the virtualenv
        create_venv_cmd = [
            "python3",
            "-m",
            "venv",
            self._VENV_DIR.as_posix(),
        ]
        subprocess.call(create_venv_cmd)
        logger.debug("virtualenv created")

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

        # Install package from private pypi
        package_version = self._charm.model.config.get("version")
        target_package = f"{self._PACKAGE_NAME}~=1.0"  # latest legacy version
        if package_version:
            target_package += f"=={self._charm.model.config['version']}"
        pip_install_cmd = [
            self._PIP_CMD,
            "install",
            "--index-url",
            self._derived_pypi_url(),
            target_package,
        ]
        out = subprocess.check_output(pip_install_cmd).decode().strip()
        if "Successfully installed" not in out:
            logger.error(f"Error installing {target_package}")
        else:
            logger.debug(f"{target_package} installed")

        self._PROFILE.write_text(
            f"export PATH=$PATH:{self._VENV_DIR.as_posix()}/bin"
        )

    def upgrade(self, version: str):
        """Upgrade armada-agent."""
        pip_install_cmd = [
            self._PIP_CMD,
            "install",
            "--upgrade",
            "--index-url",
            self._derived_pypi_url(),
            f"{self._PACKAGE_NAME}=={version}",
        ]

        out = subprocess.check_output(pip_install_cmd).decode().strip()
        if "Successfully installed" not in out:
            logger.error(
                f"Trouble upgrading {self._PACKAGE_NAME}, please debug"
            )
        else:
            logger.debug(f"{self._PACKAGE_NAME} installed")

    def remove(self):
        """
        Remove the things we have created.
        """
        rmtree(self._LOG_DIR.as_posix())
        rmtree(self._VENV_DIR.as_posix())

    def configure_etc_default(self, ctxt):
        """Render and write out the file."""

        ctxt_to_render = {
            "log_dir": self._LOG_DIR.as_posix(),
            **ctxt,
        }

        env_template = Path(
            "./src/templates/jobbergate-cli.defaults.template").read_text()

        rendered_template = env_template.format(**ctxt_to_render)

        if self._ETC_DEFAULT.exists():
            self._ETC_DEFAULT.unlink()

        self._ETC_DEFAULT.write_text(rendered_template)
