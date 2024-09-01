from certbot import errors
from certbot.plugins import dns_common
from certbot.plugins.dns_common import CredentialsConfiguration
import requests
import json
import logging
from typing import Any, Optional, Callable
import urllib

logger = logging.getLogger(__name__)

BASE_URL = "https://mijn.host/api/v2/"


class Authenticator(dns_common.DNSAuthenticator):
    def __init__(self, *args, **kwargs):
        super(Authenticator, self).__init__(*args, **kwargs)
        self.credentials: Optional[CredentialsConfiguration] = None
        self.ttl = 120

    @classmethod
    def add_parser_arguments(
        cls, add: Callable[..., None], default_propagation_seconds: int = 10
    ) -> None:
        super().add_parser_arguments(add, default_propagation_seconds)
        add("credentials", help="mijn.host credentials INI file.")

    def more_info(self) -> str:
        return "This plugin configures a DNS TXT record to respond to a dns-01 challenge using the mijn.host API."

    def _validate_credentials(self, credentials: CredentialsConfiguration) -> None:
        api_key = credentials.conf("api-key")
        if not api_key:
            raise errors.PluginError("No API key provided")

    def _setup_credentials(self) -> None:
        self.credentials = self._configure_credentials(
            "credentials",
            "mijn-host credentials INI file",
            None,
            self._validate_credentials,
        )

    def _perform(self, domain, validation_name, validation):
        self._get_mijn_host_client().add_txt_record(
            domain, validation_name, validation, self.ttl
        )

    def _cleanup(self, domain, validation_name, validation):
        self._get_mijn_host_client().del_txt_record(domain, validation_name, validation)

    def _get_mijn_host_client(self):
        if not self.credentials:
            raise errors.PluginError("Plugin not initialized")
        return MijnHostClient(self.credentials.conf("api-key"))


class MijnHostClient(object):
    def __init__(self, api_key):
        logger.debug("Creating MijnHostClient")
        self.headers = {
            "API-Key": api_key,
        }

    def _handle_response(self, resp: requests.Response) -> Any:
        if resp.status_code not in (200, 202):
            raise errors.PluginError(
                f"Received non-OK status from Mijn Host API {resp.status_code}"
            )
        try:
            return resp.json()
        except json.decoder.JSONDecodeError:
            raise errors.PluginError(f"API response with non-json: {resp.text}")

    def list_domains(self):
        url = urllib.parse.urljoin(BASE_URL, "domains")
        req = requests.get(url, headers=self.headers)
        resp = self._handle_response(req)
        return resp

    def get_records(self, domain):
        url = urllib.parse.urljoin(BASE_URL, f"domains/{domain}/dns")
        req = requests.get(url, headers=self.headers)
        resp = self._handle_response(req)
        return resp

    def update_records(self, domain, records):
        url = urllib.parse.urljoin(BASE_URL, f"domains/{domain}/dns")
        req = requests.put(
            url, headers=self.headers, data=json.dumps({"records": records})
        )
        resp = self._handle_response(req)
        return resp

    def add_txt_record(
        self, domain: str, record_name: str, record_content: str, ttl: int
    ):
        records = self.get_records(domain).get("records", [])
        new_record = {
            "type": "TXT",
            "name": record_name,
            "value": record_content,
            "ttl": ttl,
        }
        filtered_records = [
            r for r in records if not (r["type"] == "TXT" and r["name"] == record_name)
        ]
        filtered_records.append(new_record)
        self.update_records(domain, filtered_records)

    def del_txt_record(
        self, domain: str, record_name: str, record_content: str
    ) -> None:
        records = self.get_records(domain)
        records_list = [
            r
            for r in records
            if not (
                r["type"] == "TXT"
                and r["name"] == record_name
                and r["value"] == record_content
            )
        ]
        self.update_records(domain, records_list)
