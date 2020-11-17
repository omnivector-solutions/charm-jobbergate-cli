#! /usr/bin/env python3
"""libraries needed for charm."""
import subprocess

from ops.charm import CharmBase
from ops.main import main
from ops.model import ActiveStatus


class CharmJobbergate(CharmBase):
    """Jobbergate."""

    def __init__(self, *args):
        """Initialize charm and configure states and events to observe."""
        super().__init__(*args)

        event_handler_bindings = {
            self.on.install:
            self._on_install,

            self.on.config_changed:
            self._on_config_changed,

        }
        for event, handler in event_handler_bindings.items():
            self.framework.observe(event, handler)

    def _on_install(self, event):
        # place holder until snap available
        subprocess.run([
            "snap",
            "install",
            self.model.resources.fetch('jobbergate-snap'),
            "--dangerous"
            "--classic"
        ])
        self.unit.status = ActiveStatus("Jobbergate Installed")

    def _on_config_changed(self, event):
        """Set snap mode."""
        
        subprocess.run(
            [
                "snap",
                "set",
                "jobbergate",
                "snap.mode=" + self.model.config["snap-mode"]
            ]
        )
        self.unit.status = ActiveStatus("snap mode set")


if __name__ == "__main__":
    main(CharmJobbergate)
