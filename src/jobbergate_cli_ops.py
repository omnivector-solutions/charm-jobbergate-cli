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

    _PYTHON_BIN = Path("/usr/bin/python3.8")
    _PACKAGE_NAME = "jobbergate-cli"
    _LOG_DIR = Path("/var/log/new-jobbergate-cli")
    _VENV_DIR = Path("/srv/new-jobbergate-cli-venv")
    _VENV_PYTHON = _VENV_DIR.joinpath("bin", "python").as_posix()
    _ETC_DEFAULT = Path("/etc/default/new-jobbergate-cli")
    _PROFILE = Path("/etc/profile.d/new-jobbergate-cli.sh")

    def __init__(self, charm):
        """Create class level variables."""
        self._charm = charm

    def install(self):
        """Install package from private pypi."""

        # Create log dir
        if not self._LOG_DIR.exists():
            self._LOG_DIR.mkdir(parents=True)

        # Create the virtualenv
        create_venv_cmd = [
            self._PYTHON_BIN.as_posix(),
            "-m",
            "venv",
            self._VENV_DIR.as_posix(),
        ]
        subprocess.call(create_venv_cmd)
        logger.debug("virtualenv created")

        # Ensure pip
        ensure_pip_cmd = [
            self._VENV_PYTHON,
            "-m",
            "ensurepip",
        ]
        subprocess.call(ensure_pip_cmd)
        logger.debug("pip ensured")

        # Ensure we have the latest pip
        upgrade_pip_cmd = [
            self.self._VENV_PYTHON,
            "-m",
            "pip",
            "install",
            "--upgrade",
            "pip",
        ]
        subprocess.call(upgrade_pip_cmd)

        # Install package from pypi.org
        package_version = self._charm.model.config.get("version")
        target_package = self._PACKAGE_NAME
        if package_version:
            target_package += f"=={self._charm.model.config['version']}"
        pip_install_cmd = [
            self.self._VENV_PYTHON,
            "-m",
            "pip",
            "install",
            target_package,
        ]

        out = subprocess.check_output(pip_install_cmd, env={}).decode().strip()

        if "Successfully installed" not in out:
            logger.error(f"Error installing {target_package}")
        else:
            logger.debug(f"{target_package} installed")

        self._PROFILE.write_text(f"export PATH=$PATH:{self._VENV_DIR.as_posix()}/bin")

    def upgrade(self, version: str):
        """Upgrade armada-agent."""
        pip_install_cmd = [
            self.self._VENV_PYTHON,
            "-m",
            "pip",
            "install",
            "--upgrade",
            f"{self._PACKAGE_NAME}=={version}",
        ]

        out = subprocess.check_output(pip_install_cmd, env={}).decode().strip()

        if "Successfully installed" not in out:
            logger.error(f"Trouble upgrading {self._PACKAGE_NAME}, please debug")
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
            "./src/templates/jobbergate-cli.defaults.template"
        ).read_text()

        rendered_template = env_template.format(**ctxt_to_render)

        if self._ETC_DEFAULT.exists():
            self._ETC_DEFAULT.unlink()

        self._ETC_DEFAULT.write_text(rendered_template)
