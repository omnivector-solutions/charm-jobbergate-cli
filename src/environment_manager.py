from contextlib import contextmanager, redirect_stderr, redirect_stdout
from io import StringIO
import json
import logging
import os
from pathlib import Path
import re
import subprocess
import sys
from sys import executable
from typing import Iterable

from hatch.cli import main


logger = logging.getLogger()


@contextmanager
def argv_replacer(*argv: str):
    """Replace sys.argv with the given arguments."""
    original_argv = sys.argv
    sys.argv = list(argv)
    try:
        yield
    finally:
        sys.argv = original_argv


@contextmanager
def cwd_replacer(new_cwd: Path):
    """Replace the current working directory with the given path."""
    original_cwd = os.getcwd()
    os.chdir(new_cwd)
    try:
        yield
    finally:
        os.chdir(original_cwd)


class EnvironmentManager:

    def __init__(self, base_path: Path = Path.cwd()):
        """Initialize the class."""
        self.base_path = base_path.absolute()

        self.python_bin = executable

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

    def run(self, *cmd: str) -> subprocess.CompletedProcess:
        """
        Run hatch a command with the provided arguments.

        This is a wrapper around hatch.cli.main that allows us to run hatch commands
        emulating the command line, but from Python instead of using subprocess.run.

        The best practices in charm development recommend using Python instead of shell:
        https://juju.is/docs/sdk/styleguide#heading--when-to-use-python-or-shell

        Relying on subprocess.run was first attempted, but it proved to be challenging to
        locate hatch executable in the virtual environment, and the workaround to it
        produced some other issues. Therefore, the decision was made to use the hatch.cli.main.
        """
        complete_command = [
            "hatch",
            "--data-dir",
            self.base_path.as_posix(),
        ] + list(cmd)

        logger.debug("Running command '{}'".format(" ".join(complete_command)))

        with (
            argv_replacer(*complete_command),
            cwd_replacer(self.base_path),
            redirect_stdout(StringIO()) as stdout_buffer,
            redirect_stderr(StringIO()) as stderr_buffer,
        ):
            try:
                main()
                code = 0
            except SystemExit as e:
                code = e.code
        stdout_contents = stdout_buffer.getvalue()
        stderr_contents = stderr_buffer.getvalue()
        logger.debug(f"Command returned code {code} with result: {stdout_contents}")
        if code != 0:
            message = f"Command failed with code {code}: {stderr_contents}"
            logger.error(message)
            raise RuntimeError(message)
        return subprocess.CompletedProcess(
            args=complete_command,
            returncode=code,
            stdout=stdout_contents,
            stderr=stderr_contents,
        )

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
