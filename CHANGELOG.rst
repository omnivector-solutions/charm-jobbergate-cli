============
 Change Log
============

This file keeps track of all notable changes to charm-jobbergate-cli

Unreleased
----------
- Fixed JOBBERGATE_CACHE_DIR not being writen to the config file

1.0.4 - 2023-12-11
------------------
- Added new configuration: JOBBERGATE_LEGACY_NAME_CONVENTION
- Added new configuration: SBATCH_PATH [ASP-4238]
- Added new configuration: JOBBERGATE_CACHE_DIR [ASP-4053]
- Dropped support for CentOS 8
- Installed Python 3.12 to run the CLI

1.0.3 - 2023-09-07
------------------
- Set jobbergate-cli to run with Python 3.8.

1.0.2 - 2023-08-07
------------------
- Added support for Rocky Linux and Ubuntu Jammy.

1.0.0 - 2022-12-15
------------------
- Added an action to show the version of new-jobbergate-cli.
- Started versioning the charm.
