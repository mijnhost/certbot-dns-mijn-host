from certbot import errors
from certbot.plugins import dns_common
import requests
import json
import logging
from typing import Any

logger = logging.getLogger(__name__)

BASE_URL = "https://mijn.host/api/v2/"

print("mijn_host.py loaded")


class Authenticator(dns_common.DNSAuthenticator):
    def __init__(self, *args, **kwargs):
        super(Authenticator, self).__init__(*args, **kwargs)
        self.credentials = None

    @classmethod
    def add_parser_arguments(cls, add):
        super(Authenticator, cls).add_parser_arguments(
            add, default_propagation_seconds=120
        )
        add("credentials", help="credentials INI file.")

    def more_info(self):
        return (
            "This plugin configures a DNS TXT record to respond to a dns-01 "
            + "challenge using the mijn.host API."
        )

    def setup_credentials(self) -> None:
        self.credentials = self._configure_credentials(
            "credentials",
            "IONOS API credentials INI file. Only Bearer token"
            + " authentication is supported",
            {"token": "access token for the IONOS API"},
        )

    def _perform(self, domain, validation_name, validation):
        print("perform called")
        print(domain)
        print(validation_name)
        print(validation)
        print(self)
        print(self.credentials)

    def _cleanup(self, domain, validation_name, validation):
        print("cleanup called")
        print(domain)
        print(validation_name)
        print(validation)
        print(self)
        print(self.credentials)


class MijnHostClient(object):
    def __init__(self, token):
        logger.debug("Creating MijnHostClient")
        self.headers = {
            "API-Key": token,
        }

    def _handle_response(self, resp: requests.Response) -> Any:
        if resp.status_code not in (200, 202):
            print(resp.text)
            raise errors.PluginError(
                f"Received non-OK status from Mijn Host API {resp.status_code}"
            )
        try:
            return resp.json()
        except json.decoder.JSONDecodeError:
            raise errors.PluginError(f"API response with non-JSON: {resp.text}")


if __name__ == "__main__":
    print("mijn_host.py executed")
    client = MijnHostClient("test")
    resp = client._handle_response(
        requests.get(BASE_URL + "domains", headers=client.headers)
    )
    print(resp)
