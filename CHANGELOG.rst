============
 Change Log
============

This file keeps track of all notable changes to charm-jobbergate-cli

Unreleased
----------
- Enabled shell completion for the jobbergate-cli [ASP-4624]
- Removed alias name now that legacy is decommissioned, create a symlink on `/usr/local/bin` instead
- Remove support for CentOS

1.0.6 - 2024-07-01
------------------
- Replace venv by hatch as the virtual environment manager enabling the creation of application-specific virtual environments [ASP-4933]
- Removed the `version` configuration option since it was ambiguous with the update action


1.0.5 - 2024-02-15
------------------
- Fixed JOBBERGATE_CACHE_DIR not being writen to the config file
- Added new configuration: MULTI_TENANCY_ENABLED [ASP-2045]

1.0.4 - 2023-12-11
------------------
- Added new configuration: JOBBERGATE_LEGACY_NAME_CONVENTION [ASP-4069]
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
