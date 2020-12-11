#!/usr/bin/env python3
"""Jobbergate-cli charm."""
from hashlib import sha256
import logging
import re
import shlex
import subprocess

from ops.charm import CharmBase
from ops.framework import StoredState
from ops.main import main
from ops.model import ActiveStatus


log = logging.getLogger()


ENCODING = "utf-8"
SNAP_INSTALL = "snap install --classic --dangerous {snap_res}"
JOBBERGATE_VERSION = "jobbergate-cli.jobbergate --version"
VERSION_RX = re.compile(r"version (\S+)\b")
READ_CHUNK = 65536


def run(template, **kwargs):
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
        # downgrade non-ascii text to ascii for unpredictable log contexts
        log.error("\n".join([f"** failed {cmd!r}:", f"{ascii(ret.stdout)}"]))
        raise


def digest_file(filename):
    """
    Digest the contents of ``filename'' with sha256 -> hexdigest
    """
    hash_ = sha256()

    with open(filename, "rb") as opened:
        buf = opened.read(READ_CHUNK)
        while len(buf) > 0:
            hash_.update(buf)
            buf = opened.read(READ_CHUNK)

    return hash_.hexdigest()


class CharmJobbergate(CharmBase):
    """Jobbergate."""

    _stored = StoredState()

    def __init__(self, *args):
        """Initialize charm and configure states and events to observe."""
        super().__init__(*args)

        self._stored.set_default(
            last_snap_digest="",
        )

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
        run(SNAP_INSTALL, snap_res=res)
        ver = run(JOBBERGATE_VERSION).stdout
        ver = VERSION_RX.search(ver).group(1)
        self.model.unit.set_workload_version(ver)
        log.info(f"Installed version {ver}")

    def _on_install(self, event):
        """Install the jobbergate-cli snap."""
        snap_res = self.model.resources.fetch("jobbergate-snap")
        digest = digest_file(snap_res)
        self.install_snap_resource(res=snap_res)
        self._stored.last_snap_digest = digest
        self.unit.status = ActiveStatus("Jobbergate Installed")

    def _on_upgrade_charm(self, event):
        """Upgrade the charm."""
        snap_res = self.model.resources.fetch("jobbergate-snap")
        digest = digest_file(snap_res)
        # only process this as an upgrade if the snap has actually changed
        if digest != self._stored.last_snap_digest:
            self.install_snap_resource(res=snap_res)
            self._stored.last_snap_digest = digest
            self.unit.status = ActiveStatus("Jobbergate upgraded")
        else:
            # status is unchanged but replace the message
            _was = self.unit.status.name
            _new = self.unit.status.from_name(_was, "skipping upgrade, snap unchanged")
            self.unit.status = _new


if __name__ == "__main__":  # pragma: nocoverage
    main(CharmJobbergate)
