#!/usr/bin/env python3
"""Jobbergate-cli charm."""
import subprocess

from ops.charm import CharmBase
from ops.main import main
from ops.model import (
    ActiveStatus
)


class CharmJobbergate(CharmBase):
    """Jobbergate."""

    def __init__(self, *args):
        """Initialize charm and configure states and events to observe."""
        super().__init__(*args)

        event_handler_bindings = {
            self.on.install:
            self._on_install,

            self.on.upgrade_charm:
            self._on_upgrade_charm,
        }
        for event, handler in event_handler_bindings.items():
            self.framework.observe(event, handler)

    def _on_install(self, event):
        """Install the jobbergate-cli snap."""
        subprocess.run([
            "snap",
            "install",
            self.model.resources.fetch('jobbergate-snap'),
            "--dangerous",
            "--classic"
        ])
        self.unit.status = ActiveStatus("Jobbergate Installed")

    def _on_upgrade_charm(self, event):
        """Upgrade the charm."""

        # place holder until snap available
        subprocess.run([
            "snap",
            "refresh",
            self.model.resources.fetch('jobbergate-snap'),
            "--dangerous",
            "--classic"
        ])
        self.unit.status = ActiveStatus("Jobbergate upgraded")


if __name__ == "__main__":
    main(CharmJobbergate)
