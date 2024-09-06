<a href="https://mijn.host" target="_blank">
    <center>
        <img src="https://assets.eu.apidog.com/app/apidoc-image/custom/20240626/f1508b02-a360-4b89-b7a9-b939a9180c0e.png"
        alt="mijn.host"
        />
    </center>
</a>

# [mijn.host](https://mijn.host) DNS Certbot Authenticator Plugin

The [mijn.host](https://mijn.host) DNS Certbot Plugin automates SSL/TLS certificate creation by enabling DNS-01 challenges using the mijn.host API. This plugin is designed to work with the Certbot tool, allowing seamless integration for automated certificate management.

## Requirements

To use the plugin, you'll need the following:

- A mijn.host account
- An API key from mijn.host

## Installation

You can install the plugin using `pip`:

```bash
pip install certbot-dns-mijn-host
```

## Arguments

| Argument                            | Example           | Description                                                                                     |
| ----------------------------------- | ----------------- | ----------------------------------------------------------------------------------------------- |
| --authenticator                     | dns-mijn-host     | Specifies that Certbot should use this plugin. Use dns-mijnhost as the value.                   |
| --dns-mijn-host-credentials         | ./credentials.ini | Points to the credentials file containing your mijn.host API key. Required.                     |
| --dns-mijn-host-propagation-seconds | 60                | Sets the wait time in seconds before Certbot checks the TXT record. The default is 120 seconds. |

## Credentials File

```ini
dns_mijn_host_api_key = YOUR_API_KEY
```

Make sure the file is stored securely and not accessible by unauthorized users.

## Example usage

```bash
certbot certonly \
  --authenticator dns-mijn-host \
  --dns-mijn-host-credentials /path/to/credentials.ini \
  --dns-mijn-host-propagation-seconds 60 \
  --agree-tos \
  --rsa-key-size 4096 \
  -d 'example.com' \
  -d '*.example.com'
```

The plugin will create a TXT record for the DNS-01 challenge in your mijn.host DNS zone. After the challenge is verified, the plugin will delete the TXT record.

## Local Development

For local development and testing, it’s recommended to use a Python virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python setup.py sdist bdist_wheel
pip install -e .
```

This will install the plugin in the local environment, allowing you to make changes without reinstalling.

When running Certbot locally, you may need to specify --logs-dir, --config-dir, and --work-dir to avoid permission issues with global directories.

## Support

If you encounter issues or have suggestions, please open an issue on the GitHub repository.

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](./LICENSE) file for details.

## Related Plugins

If you need to use a different DNS service, check out the [Certbot DNS plugins](https://eff-certbot.readthedocs.io/en/latest/using.html#dns-plugins) for other providers.
