#!/usr/bin/env python3
"""Jobbergate-cli charm."""
import shlex
import subprocess

from ops.charm import CharmBase
from ops.main import main
from ops.model import ActiveStatus


SNAP_REFRESH = "snap refresh {snap_res} --dangerous --classic"
JOBBERGATE_VERSION = "jobbergate --version"


def _run_quoted_command(template, capture_output=False, check=True, **kwargs):
    """
    Run the command with kwargs formatted into the template; while safely quoting for the shell
    """
    cmd = shlex.quote(template.format(**kwargs))
    return subprocess.run(cmd, shell=True, check=check, capture_output=capture_output)


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

    def install_snap_resource(self, res):
        """
        Use snap to install the resource we just fetched and set properties about it
        """
        _run_quoted_command(SNAP_REFRESH, snap_res=res)
        ver = _run_quoted_command(JOBBERGATE_VERSION, capture_output=True)
        self.model.unit.set_workload_version(ver.strip())

    def _on_install(self, event):
        """Install the jobbergate-cli snap."""
        snap_res = self.model.resources.fetch("jobbergate-snap")
        self.install_snap_resource(snap_res)
        self.unit.status = ActiveStatus("Jobbergate Installed")

    def _on_upgrade_charm(self, event):
        """Upgrade the charm."""
        snap_res = self.model.resources.fetch("jobbergate-snap")
        self.install_snap_resource(snap_res)
        self.unit.status = ActiveStatus("Jobbergate upgraded")


if __name__ == "__main__":
    main(CharmJobbergate)
