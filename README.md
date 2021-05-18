# charm-jobbergate-cli


# Usage
Follow the steps below to get started.

### Build the charm

Running the following command will produce a .charm file, `jobbergate-cli.charm`
```bash
charmcraft build
```

### Create the jobbergate-cli charm config

`jobbergate-cli.yaml`

```yaml
jobbergate-cli:
  jobbergate-api-backend-base-url: "<jobbergate-api-backend>"
  pypi-url: "<pypi-url>"
  pypi-username: "<pypi-username>"
  pypi-password: "<pypi-password>"
```

### Deploy the charm
Using the built charm and the defined config, run the command to deploy the charm.
```bash
juju deploy ./jobbergate-cli.charm \
    --config ./jobbergate-cli.yaml \
    --series centos7
```

### Charm Actions
The jobbergate-cli charm exposes additional functionality to facilitate jobbergate-cli
package upgrades.

To upgrade the jobbergate-cli to a new version or release:
```bash
juju run-action jobbergate-cli/leader upgrade version="7.7.7"
```

This will result in the jobbergate-cli package upgrade to 7.7.7.

#### License
* MIT (see `LICENSE` file in this directory for full preamble)
