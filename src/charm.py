#!/usr/bin/env python3
"""JobbergateCLICharm."""
import logging

from ops.charm import CharmBase
from ops.framework import StoredState
from ops.main import main
from ops.model import ActiveStatus

from jobbergate_cli_ops import JobbergateCliOps


logger = logging.getLogger()


class JobbergateCliCharm(CharmBase):
    """Facilitate Jobbergate CLI lifecycle."""

    _stored = StoredState()

    def __init__(self, *args):
        """Initialize and observe."""
        super().__init__(*args)

        self._stored.set_default(installed=False)
        self._stored.set_default(backend_base_url=str())

        self._jobbergate_cli_ops = JobbergateCliOps(self)

        event_handler_bindings = {
            self.on.install: self._on_install,
            self.on.start: self._on_start,
            self.on.config_changed: self._on_config_changed,
            self.on.remove: self._on_remove,
            self.on.upgrade_action: self._upgrade_jobbergate_cli,
        }
        for event, handler in event_handler_bindings.items():
            self.framework.observe(event, handler)

    def _on_install(self, event):
        """Install jobbergate-cli."""
        self._jobbergate_cli_ops.install()
        self._stored.installed = True
        # Log and set status
        logger.debug("jobbergate-cli agent installed")
        self.unit.status = ActiveStatus("jobbergate-cli installed")

    def _on_config_changed(self, event):
        """Configure jobbergate-cli."""

        # Get the backend-base-url from the charm config and check if it has changed.
        backend_base_url_from_config = self.model.config.get("backend-base-url")
        if backend_base_url_from_config != self._stored.backend_base_url:
            self._stored.backend_base_url = backend_base_url_from_config

    def _on_remove(self, event):
        """Remove directories and files created by jobbergate-cli charm."""
        self._jobbergate_cli_ops.remove_jobbergate_cli()

    def _upgrade_to_latest(self, event):
        version = event.params["version"]
        self._jobbergate_cli_ops.upgrade(version)


if __name__ == "__main__":
    main(JobbergateCliCharm)
