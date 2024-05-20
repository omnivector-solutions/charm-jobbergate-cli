from contextlib import contextmanager
from pathlib import Path
from subprocess import CompletedProcess
from textwrap import dedent
from unittest import mock

import pytest

from environment_manager import EnvironmentManager


@pytest.fixture
def environment_manager(tmpdir):
    return EnvironmentManager(base_path=Path(tmpdir))


@pytest.fixture
def mock_run(environment_manager):
    @contextmanager
    def helper(stdout: str | None = None):
        with mock.patch.object(
            environment_manager,
            "run",
            return_value=CompletedProcess(
                args=[],
                returncode=0,
                stdout=stdout,
            ),
        ):
            yield

    return helper


def test_install__success(environment_manager, mock_run):
    with mock_run(), mock.patch.object(
        environment_manager, "iter_envs", return_value=["env1", "env2"]
    ):
        environment_manager.install()

        assert environment_manager.run.call_count == 2
        assert environment_manager.run.call_args_list == [
            mock.call("env", "create", "env1"),
            mock.call("env", "create", "env2"),
        ]


def test_get_version_info__success(environment_manager, mock_run):
    with mock_run(stdout="\nVersion: 1.2.3a0\n"):
        assert environment_manager.get_version_info() == "1.2.3a0"
        assert environment_manager.run.call_args == mock.call(
            "env", "run", "pip", "show", "jobbergate-cli"
        )


def test_get_version_info__failure(environment_manager, mock_run):
    with mock_run(stdout=""):
        with pytest.raises(RuntimeError, match="Failed to get version info"):
            environment_manager.get_version_info()


def test_iter_envs(environment_manager, mock_run):
    with mock_run(stdout='{"default": null, "env1": null, "env2": null}'):
        assert list(environment_manager.iter_envs()) == ["default", "env1", "env2"]
        assert environment_manager.run.call_args == mock.call("env", "show", "--json")


def test_iter_envs__decode_error(environment_manager, mock_run):
    with mock_run(stdout="not json"):
        with pytest.raises(RuntimeError, match="Failed to decode JSON"):
            list(environment_manager.iter_envs())


class TestWriteConfigFile:

    @pytest.fixture(autouse=True)
    def mock_python_executable(self, environment_manager) -> str:
        value = "/somewhere/python"
        environment_manager.python_bin = value
        return value

    def test_default_arguments(self, environment_manager):
        environment_manager.write_config_file()
        file_path = environment_manager.base_path / "pyproject.toml"
        assert file_path.exists()

        expected_result = dedent(
            """\
            [project]
            name = "default"

            [tool.hatch.envs.default]
            detached = true
            python = "/somewhere/python"
            dependencies = ["jobbergate-cli"]

            """
        )
        assert file_path.read_text() == expected_result

    def test_set_version(self, environment_manager):
        environment_manager.write_config_file(target_version="1.2.3")
        file_path = environment_manager.base_path / "pyproject.toml"
        assert file_path.exists()

        expected_result = dedent(
            """\
            [project]
            name = "default"

            [tool.hatch.envs.default]
            detached = true
            python = "/somewhere/python"
            dependencies = ["jobbergate-cli==1.2.3"]

            """
        )
        assert file_path.read_text() == expected_result

    def test_set_application_specific_environments(self, environment_manager):
        application_specific_environments = dedent(
            """\
            [tool.hatch.envs.custom]
            dependencies = ["jobbergate-core", "ruff"]
            description = "Some custom environment"
            """
        )
        environment_manager.write_config_file(
            application_specific_environments=application_specific_environments
        )
        file_path = environment_manager.base_path / "pyproject.toml"
        assert file_path.exists()

        expected_result = dedent(
            """\
            [project]
            name = "default"

            [tool.hatch.envs.default]
            detached = true
            python = "/somewhere/python"
            dependencies = ["jobbergate-cli"]

            [tool.hatch.envs.custom]
            dependencies = ["jobbergate-core", "ruff"]
            description = "Some custom environment"
            """
        )
        assert file_path.read_text() == expected_result
