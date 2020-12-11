"""
Test the jobbergate-cli charm
"""
import subprocess
from unittest.mock import ANY, Mock, call, patch

from ops.testing import Harness
from pytest import fixture, raises

import charm


@fixture
def harness():
    """
    Use the ops framework test harness to drive
    """
    return Harness(charm.CharmJobbergate)


@fixture
def snapfile(tmpdir):
    """
    A temporary file with known contents
    """
    pth = tmpdir / "my.snap"
    pth.write_binary(b"oh no")
    yield pth
    pth.remove()


@fixture
def patched_run():
    """
    Patch subprocess.run to be a no-op
    """
    with patch.object(subprocess, "run", autospec=True) as m:
        m.return_value.stdout = "hello"
        yield m


@fixture
def patched_log():
    """
    Stub out the log system for mocks
    """
    with patch.object(charm, "log", autospec=True) as m:
        yield m


def test_run(snapfile, patched_log):
    """
    Do I run programs, and do I catch errors from running programs?
    """
    assert charm.run(f"ls {snapfile!s}").stdout == str(snapfile) + "\n"

    bad_ls = "ls /0ewr89gyhwaesr0g8h"
    with raises(subprocess.CalledProcessError):
        charm.run(bad_ls)
    arg = patched_log.error.call_args[0][0]
    assert arg.startswith(f"** failed {bad_ls!r}:")


def test_digest_file(snapfile):
    """
    Do I digest the file contents reliably?
    """
    assert (
        charm.digest_file(snapfile)
        == "0efea166568eee1c3747bdbfb5b18df82e8873e385e10f5f65bc7f4f0de69b10"
    )


@fixture
def install_subprocesses():
    """
    Just some simple mocks to represent the expected subprocess.run() calls
    """
    return [
        Mock(stdout="woo snap installed"),
        Mock(stdout="release version 19"),
    ]


def test_install(harness, patched_run, install_subprocesses):
    """
    Do I install a snap resource at install-time?
    """
    harness.add_resource("jobbergate-snap", "scooby dooby data")
    patched_run.side_effect = install_subprocesses
    harness.begin_with_initial_hooks()
    assert patched_run.call_args_list == [
        call(
            [
                "snap",
                "install",
                "--classic",
                "--dangerous",
                ANY,
            ],
            stdout=ANY,
            stderr=ANY,
            check=False,
            encoding=ANY,
        ),
        call(
            ["/snap/bin/jobbergate-cli.jobbergate", "--version"],
            stdout=ANY,
            stderr=ANY,
            check=False,
            encoding=ANY,
        ),
    ]
    assert harness.get_workload_version() == "19"


def test_upgrade_unchanged(harness, patched_run, install_subprocesses):
    """
    Test upgrade scenario: snap resource is unchanged from previous install
    """
    harness.add_resource("jobbergate-snap", "scooby dooby data")
    patched_run.side_effect = install_subprocesses

    # install hook will set charm._stored.last_snap_digest value
    harness.begin_with_initial_hooks()

    harness.charm._on_upgrade_charm(Mock())
    assert harness.model.unit.status.message == "skipping upgrade, snap unchanged"


def test_upgrade_changed(harness, patched_run, install_subprocesses):
    """
    Test upgrade scenario: snap resource is new
    """
    patched_run.side_effect = install_subprocesses
    harness.begin()

    harness.add_resource("jobbergate-snap", "scooby doo and snappy too")
    harness.charm._on_upgrade_charm(Mock())
    assert harness.model.unit.status.message == "Jobbergate upgraded"
