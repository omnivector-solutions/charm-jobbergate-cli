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
    _EXECUTABLE_PATH = _VENV_DIR / "env/virtual/default/bin/jobbergate"
    _EXECUTABLE_LINK = Path("/usr/local/bin/jobbergate")
    _SHELL_COMPLETION = Path("/etc/bash_completion.d/jobbergate_complete")

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
        self.configure_bin_script()
        self.configure_shell_completion()

    def create_symbolic_link(self):
        """
        Create a symbolic link to the new location of the bin directory.

        It changed after hatch was introduced as the virtual environment manager.
        The link ensures the previous bin path is still valid for backward compatibility.
        """
        previous_bin_path = self._VENV_DIR / "bin"

        previous_bin_path.unlink(missing_ok=True)
        previous_bin_path.symlink_to(
            self._EXECUTABLE_PATH.parent, target_is_directory=True
        )

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
        self._SHELL_COMPLETION.unlink(missing_ok=True)

    def configure_bin_script(self):
        """Create a symbolic link for the bin script."""
        self._EXECUTABLE_LINK.unlink(missing_ok=True)
        self._EXECUTABLE_LINK.symlink_to(
            self._EXECUTABLE_PATH, target_is_directory=False
        )

    def configure_etc_default(self, ctxt):
        """Render and write out the file."""
        ctxt_to_render = {**ctxt}

        env_template = Path(
            "./src/templates/jobbergate-cli.defaults.template"
        ).read_text()

        rendered_template = env_template.format(**ctxt_to_render)

        self._ETC_DEFAULT.unlink(missing_ok=True)
        self._ETC_DEFAULT.write_text(rendered_template)

    def configure_shell_completion(self):
        """Render and write out the file."""
        shell_completion_template = Path(
            "./src/templates/bash-completion.template"
        ).read_text()

        self._SHELL_COMPLETION.parent.mkdir(parents=True, exist_ok=True)
        self._SHELL_COMPLETION.write_text(shell_completion_template)
