#!/usr/bin/env python3
"""JobbergateCLICharm"""
import logging
from pathlib import Path

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
            self.on.upgrade_charm: self._on_upgrade,
            self.on.config_changed: self._on_config_changed,
            self.on.remove: self._on_remove,
            self.on.upgrade_action: self._on_upgrade_action,
            self.on.show_version_action: self._on_show_version_action,
        }
        for event, handler in event_handler_bindings.items():
            self.framework.observe(event, handler)

    def _on_install(self, event):
        """Install jobbergate-cli."""
        self.unit.set_workload_version(Path("version").read_text().strip())

        self._jobbergate_cli_ops.install()
        self._stored.installed = True
        # Log and set status
        logger.debug("new-jobbergate-cli installed")
        self.unit.status = ActiveStatus("new-jobbergate-cli installed")

    def _on_upgrade(self, event):
        """Perform upgrade operations."""
        self.unit.set_workload_version(Path("version").read_text().strip())

    def _on_remove(self, event):
        """Remove directories and files created by new-jobbergate-cli charm."""
        self._jobbergate_cli_ops.remove()

    def _on_upgrade_action(self, event):
        version = event.params["version"]
        try:
            self._jobbergate_cli_ops.upgrade(version)
            event.set_results({"upgrade": "success"})
            self.unit.status = ActiveStatus(f"Updated to version {version}")
        except Exception:
            self.unit.status = BlockedStatus(f"Error updating to version {version}")
            event.fail()

    def _on_show_version_action(self, event):
        """Show the info and version of new-jobbergate-cli."""
        info = self._jobbergate_cli_ops.get_version_info()
        event.set_results({"new-jobbergate-cli": info})

    def _on_config_changed(self, event):
        """Configure jobbergate-cli."""

        # Get settings from the charm config
        ctxt_keys = {
            "backend-base-url",
            "sentry-dsn",
            "sentry-env",
            "s3-log-bucket",
            "aws-access-key-id",
            "aws-secret-access-key",
            "oidc-domain",
            "oidc-audience",
            "oidc-client-id",
            "compatibility-mode",
            "legacy-name-convention",
            "default-cluster-name",
            "sbatch-path",
            "cache-dir",
            "alias-name",
        }
        ctxt = {k: self.model.config.get(k) for k in ctxt_keys}

        backend_base_url = ctxt.get("backend-base-url")

        if not backend_base_url:
            logger.debug("Need backend base url")
            self.unit.status = BlockedStatus("Need 'backend-base-url'")
            event.defer()
            return

        if backend_base_url != self._stored.backend_base_url:
            self._stored.backend_base_url = backend_base_url

        self._jobbergate_cli_ops.configure_etc_default(ctxt)
        self._jobbergate_cli_ops.configure_executable_alias(
            alias_name=ctxt.get("alias-name", "jobbergate")
        )


if __name__ == "__main__":
    main(JobbergateCliCharm)
