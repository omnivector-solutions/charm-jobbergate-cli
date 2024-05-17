"""
JobbergateCliOps.
"""

import logging
from pathlib import Path
from shutil import rmtree

from environment_manager import EnvironmentManager


logger = logging.getLogger()


class JobbergateCliOps:
    """Track and perform jobbergate-cli ops."""

    _VENV_DIR = Path("/srv/new-jobbergate-cli-venv")
    _ETC_DEFAULT = Path("/etc/default/jobbergate3-cli")
    _PROFILE = Path("/etc/profile.d/new-jobbergate-cli.sh")

    def __init__(self, charm):
        """Create class level variables."""
        self._charm = charm
        self.environment_manager = EnvironmentManager(base_path=self._VENV_DIR)

    def install(self):
        """Install package."""

        self._VENV_DIR.mkdir(parents=True, exist_ok=True)
        self.environment_manager.write_config_file()
        self.environment_manager.install(clear_install=True)
        self.create_symbolic_link()

    def create_symbolic_link(self):
        """
        Create a symbolic link to the new location of the bin directory.

        It changed after hatch was introduced as the virtual environment manager.
        The link ensures the previous bin path is still valid for backward compatibility.
        """
        new_bin_path = self._VENV_DIR / "env" / "virtual" / "default" / "bin"
        previous_bin_path = self._VENV_DIR / "bin"

        if previous_bin_path.exists():
            previous_bin_path.unlink()

        previous_bin_path.symlink_to(new_bin_path, target_is_directory=True)

    def upgrade(self, version: str):
        """Upgrade package."""
        self.environment_manager.write_config_file(
            target_version=version,
            application_specific_environments=self._charm.model.config.get(
                "application-specific-environments", ""
            ),
        )
        self.environment_manager.install(clear_install=True)

    def get_version_info(self):
        """Show version and info about new-jobbergate-cli."""
        return self.environment_manager.get_version_info()

    def remove(self):
        """
        Remove the things we have created.
        """
        rmtree(self._VENV_DIR.as_posix())
        self._ETC_DEFAULT.unlink(missing_ok=True)

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
