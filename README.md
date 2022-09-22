# charm-jobbergate-cli

## Usage

Follow the steps below to get started.

### Build the charm

Running the following command will produce a `.charm` file, `new-jobbergate-cli.charm`:

```bash
make charm
```

### Create the jobbergate-cli charm config

`jobbergate-cli.yaml`

```yaml
jobbergate-cli:
  backend-base-url: "<jobbergate-api-backend-base-url>"
  oidc-domain: "<jobbergate-oidc-domain>"
  oidc-audience: "<jobbergate-oidc-audience>"
  oidc-client-id: "<jobbergate-oidc-client-id>"
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
juju run-action jobbergate-cli/leader upgrade version="3.2.4"
```

This will result in the jobbergate-cli package upgrade to 3.2.4.

### Additional Configuration Options

If you wish to install a particular version of jobbergate-cli, you may add it in
`jobbergate-cli.yaml` also:

```yaml
jobbergate-cli:
  version: 3.2.4
```

If you need to be able to upload user logs to S3, you will need to include in the config:

```yaml
jobbergate-cli:
  s3-log-bucket: <bucket_name>  # Usually the default is fine here
  aws-access-key-id: <key_id>
  aws-secret-access-key: <secret-key>

If you want error events to be sent to Sentry, you can add the DSN to the config:

```yaml
jobbergate-cli:
  sentry-dsn: <sentry_dsn>  # Find this in Sentry Project Settings under "Client Keys".
```

## License

* MIT (see `LICENSE` file in this directory for full preamble)
