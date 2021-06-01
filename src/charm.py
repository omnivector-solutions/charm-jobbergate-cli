#!/usr/bin/env python3
"""JobbergateCLICharm"""
import logging

from ops.charm import CharmBase
from ops.framework import StoredState
from ops.main import main
from ops.model import ActiveStatus, BlockedStatus

from jobbergate_cli_ops import JobbergateCliOps


logger = logging.getLogger()


class JobbergateCliCharm(CharmBase):
    """Facilitate Jobbergate lifecycle."""

    _stored = StoredState()

    def __init__(self, *args):
        """Initialize and observe."""
        super().__init__(*args)

        self._stored.set_default(backend_base_url=str())

        self._jobbergate_cli_ops = JobbergateCliOps(self)

        event_handler_bindings = {
            self.on.install: self._on_install,
            self.on.config_changed: self._on_config_changed,
            self.on.remove: self._on_remove,
            self.on.upgrade_action: self._on_upgrade_action,
        }
        for event, handler in event_handler_bindings.items():
            self.framework.observe(event, handler)

    def _on_install(self, event):
        """Install jobbergate-cli."""
        self._jobbergate_cli_ops.install()
        self._stored.installed = True
        # Log and set status
        logger.debug("jobbergate-cli installed")
        self.unit.status = ActiveStatus("jobbergate-cli installed")

    def _on_remove(self, event):
        """Remove directories and files created by jobbergate-cli charm."""
        self._jobbergate_cli_ops.remove()

    def _on_upgrade_action(self, event):
        version = event.params["version"]
        self._jobbergate_cli_ops.upgrade(version)

    def _on_config_changed(self, event):
        """Configure jobbergate-cli."""

        # Get the backend-url from the charm config
        backend_base_url = self.model.config.get("backend-base-url")

        if not backend_base_url:
            logger.dedub("Need backend base url")
            self.unit.status = BlockedStatus("Need 'backend-base-url'")
            event.defer()
            return

        if backend_base_url != self._stored.backend_base_url:
            self._stored.backend_base_url = backend_base_url

        ctxt = {
            "backend_base_url": backend_base_url,
        }
        self._jobbergate_cli_ops.configure_etc_default(ctxt)


if __name__ == "__main__":
    main(JobbergateCliCharm)
