import json
import logging
from pathlib import Path
import re
import subprocess
from sys import executable
from typing import Iterable


logger = logging.getLogger()


class EnvironmentManager:

    def __init__(self, base_path: Path = Path.cwd()):
        """Initialize the class."""
        self.base_path = base_path

        self.python_bin = executable

        self.hatch_cmd = (
            self.python_bin,
            "-m",
            "hatch",
            "--data-dir",
            ".",
        )
        self.hatch_template_path = Path("./src/templates/pyproject.toml.template")
        self.hatch_template = self.hatch_template_path.read_text()

        self.package_name = "jobbergate-cli"

    def write_config_file(
        self, target_version: str = "", application_specific_environments: str = ""
    ):
        """Write the pyproject.toml file."""
        target_package = self.package_name
        if target_version:
            target_package += f"=={target_version}"

        config_file = self.base_path / "pyproject.toml"
        content = self.hatch_template.format(
            target_package=target_package,
            application_specific_environments=application_specific_environments,
            base_directory=self.base_path.absolute().as_posix(),
            python_bin=self.python_bin,
        )
        config_file.write_text(content)

    def install(self, *, clear_install: bool = False):
        """Install the environments."""
        if clear_install:
            self.prune()
        for env in self.iter_envs():
            logger.info(f"Installing virtual environment: {env}")
            self.run("env", "create", env)
        logger.info("All virtual environments installed")

    def get_version_info(self) -> str:
        """Get version info for the package."""
        info = self.run("env", "run", "pip", "show", self.package_name).stdout
        if match := re.search(r"Version: (.+)", info):
            return match.group(1)
        raise RuntimeError(f"Failed to get version info for {self.package_name}")

    def prune(self):
        """Prune the environments."""
        logger.info("Pruning virtual environments")
        self.run("env", "prune")
        logger.info("Virtual environments pruned")

    def run(self, *cmd: str, **kwargs) -> subprocess.CompletedProcess:
        """Run hatch a command."""
        complete_command = list(self.hatch_cmd)
        complete_command.extend(cmd)
        logger.debug(
            "Running command '{}' with kwargs: {}".format(
                " ".join(complete_command), kwargs
            )
        )
        try:
            result = subprocess.run(
                complete_command,
                cwd=self.base_path.as_posix(),
                capture_output=True,
                text=True,
                check=True,
                shell=False,
                **kwargs,
            )
            logger.debug(
                f"Command returned code {result.returncode} with result: {result.stdout}"
            )
            return result
        except subprocess.CalledProcessError as e:
            message = f"Failed to run command with code {e.returncode}: {e.stderr or e.stdout}"
            logger.error(message)
            raise RuntimeError(message) from e

    def iter_envs(self) -> Iterable[str]:
        """Iterate over all environments."""
        completed_process = self.run("env", "show", "--json")
        try:
            data = json.loads(completed_process.stdout)
        except json.JSONDecodeError as e:
            message = f"Failed to decode JSON: {completed_process.stdout}"
            logger.error(message)
            raise RuntimeError(message) from e
        return (key for key in data.keys() if not key.startswith("hatch-"))
