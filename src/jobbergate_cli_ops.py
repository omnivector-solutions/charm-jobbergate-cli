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

    _PYTHON_BIN = Path("/opt/python/3.8.16/bin/python3.8")
    _PACKAGE_NAME = "jobbergate-cli"
    _VENV_DIR = Path("/srv/new-jobbergate-cli-venv")
    _VENV_PYTHON = _VENV_DIR.joinpath("bin", "python").as_posix()
    _ETC_DEFAULT = Path("/etc/default/jobbergate3-cli")
    _PROFILE = Path("/etc/profile.d/new-jobbergate-cli.sh")

    def __init__(self, charm):
        """Create class level variables."""
        self._charm = charm

    def install(self):
        """Install package from private pypi."""

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
            self._VENV_PYTHON,
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
            self._VENV_PYTHON,
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

    def upgrade(self, version: str):
        """Upgrade armada-agent."""
        pip_install_cmd = [
            self._VENV_PYTHON,
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

    def get_version_info(self):
        """Show version and info about new-jobbergate-cli."""
        cmd = [
            self._VENV_PYTHON,
            "-m",
            "pip",
            "show",
            self._PACKAGE_NAME
        ]

        out = subprocess.check_output(cmd, env={}).decode().strip()

        return out

    def remove(self):
        """
        Remove the things we have created.
        """
        rmtree(self._VENV_DIR.as_posix())

    def configure_executable_alias(self, alias_name):
        """
        Set an alias for the jobbergate executable.

        It aims to avoid conflicts between legacy and new versions of jobbergate-cli.
        """
        executable_path = self._VENV_DIR / "bin" / "jobbergate"
        file_content = "alias {}='{}'".format(alias_name, executable_path.as_posix())

        logger.debug(f"Writing executable alias to {self._PROFILE}: {file_content}")
        self._PROFILE.write_text(file_content)

    def configure_etc_default(self, ctxt):
        """Render and write out the file."""

        ctxt_to_render = {
            **ctxt,
        }

        env_template = Path(
            "./src/templates/jobbergate-cli.defaults.template"
        ).read_text()

        rendered_template = env_template.format(**ctxt_to_render)

        if self._ETC_DEFAULT.exists():
            self._ETC_DEFAULT.unlink()

        self._ETC_DEFAULT.write_text(rendered_template)
