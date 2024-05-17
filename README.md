# charm-new-jobbergate-cli

## Usage

Follow the steps below to get started.

### Build the charm

Running the following command will produce a `.charm` file, `new-jobbergate-cli.charm`:

```bash
make charm
```

### Create the new-jobbergate-cli charm config

`new-jobbergate-cli.yaml`

```yaml
new-jobbergate-cli:
  backend-base-url: "<jobbergate-api-backend-base-url>"
  oidc-domain: "<jobbergate-oidc-domain>"
  oidc-audience: "<jobbergate-oidc-audience>"
  oidc-client-id: "<jobbergate-oidc-client-id>"
```

### Deploy the charm

Using the built charm and the defined config, run the command to deploy the charm.

```bash
juju deploy ./new-jobbergate-cli.charm \
    --config ./new-jobbergate-cli.yaml \
    --series centos7
```

### Release the charm

To make a new release of the Jobbergate-cli Charm:

1. Update the CHANGELOG.rst file, moving the changes under the Unreleased section to the new version section. Always keep an `Unreleased` section at the top.
2. Create a new commit with the title `Release x.y.z`
3. Create a new annotated Git tag, adding a summary of the changes in the tag message:

  ```bash
  git tag --annotate --sign x.y.z
  ```

4. Push the new tag to GitHub:

  ```bash
  git push --tags
  ```

### Charm Actions

The new-jobbergate-cli charm exposes additional functionality to facilitate new-jobbergate-cli
package upgrades.

To upgrade the new-jobbergate-cli to a new version or release:

```bash
juju run-action new-jobbergate-cli/leader upgrade version="3.2.4"
```

This will result in the new-jobbergate-cli package upgrade to 3.2.4.

### Additional Configuration Options

If you need to be able to upload user logs to S3, you will need to include in the config:

```yaml
new-jobbergate-cli:
  s3-log-bucket: <bucket_name>  # Usually the default is fine here
  aws-access-key-id: <key_id>
  aws-secret-access-key: <secret-key>

If you want error events to be sent to Sentry, you can add the DSN to the config:

```yaml
new-jobbergate-cli:
  sentry-dsn: <sentry_dsn>  # Find this in Sentry Project Settings under "Client Keys".
```

Application-specific environments can be set in the config option `application-specific-environments`. They are managed as hatch environments, please refer to the [Hatch documentation](https://hatch.pypa.io/dev/config/environment/overview/) for more information. For instance, an environment named `application` can be set as follows:

```toml
[tool.hatch.envs.application]
extra-dependencies = [
  "foo",
  "bar",
  "baz",
]
```

It will inherit `jobbergate-cli` and its dependencies from the base environment and add the extra dependencies `foo`, `bar`, and `baz`.
Application-specific environments are available at `/srv/new-jobbergate-cli-venv/env/virtual/<env_name>/lib`.
The application workflow file (e.g. `jobbergate.py`) can enable them at runtime by using `sys.path.append` to add the path to the environment.

## License

* MIT (see `LICENSE` file in this directory for full preamble)
