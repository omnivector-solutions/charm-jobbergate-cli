#!/usr/bin/env python3
"""Jobbergate-cli charm."""
import logging
import re
import shlex
import subprocess

from ops.charm import CharmBase
from ops.main import main
from ops.model import ActiveStatus


log = logging.getLogger()


ENCODING = "utf-8"
SNAP_INSTALL = "snap install --classic --dangerous {snap_res}"
JOBBERGATE_VERSION = "jobbergate-cli.jobbergate --version"
VERSION_RX = re.compile(r'version (\S+)\b')


def _run(template, **kwargs):
    """
    Run the command with kwargs formatted into the template
    """
    format_args = {k: shlex.quote(str(v)) for (k, v) in kwargs.items()}
    cmd = template.format(**format_args)
    ret = subprocess.run(
        shlex.split(cmd),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
        encoding=ENCODING,
    )
    try:
        ret.check_returncode()
        return ret
    except subprocess.CalledProcessError:
        log.error("\n".join([f"** failed {cmd!r}:", f"{ret.stdout}"]))
        raise


class CharmJobbergate(CharmBase):
    """Jobbergate."""

    def __init__(self, *args):
        """Initialize charm and configure states and events to observe."""
        super().__init__(*args)

        event_handler_bindings = {
            self.on.install: self._on_install,
            self.on.upgrade_charm: self._on_upgrade_charm,
        }
        for event, handler in event_handler_bindings.items():
            self.framework.observe(event, handler)

    def install_snap_resource(self, cmd, res):
        """
        Use snap to install the resource we just fetched and set properties about it
        """
        _run(cmd, snap_res=res)
        ver = _run(JOBBERGATE_VERSION).stdout
        ver = VERSION_RX.search(ver).group(1)
        self.framework.breakpoint()
        self.model.unit.set_workload_version(ver)

    def _on_install(self, event):
        """Install the jobbergate-cli snap."""
        snap_res = self.model.resources.fetch("jobbergate-snap")
        self.install_snap_resource(cmd=SNAP_INSTALL, res=snap_res)
        self.unit.status = ActiveStatus("Jobbergate Installed")

    def _on_upgrade_charm(self, event):
        """Upgrade the charm."""
        snap_res = self.model.resources.fetch("jobbergate-snap")
        self.install_snap_resource(cmd=SNAP_INSTALL, res=snap_res)
        self.unit.status = ActiveStatus("Jobbergate upgraded")


if __name__ == "__main__":
    main(CharmJobbergate)
