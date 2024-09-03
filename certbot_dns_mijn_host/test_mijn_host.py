import unittest
from unittest.mock import patch, MagicMock
import requests
import urllib

import json
from certbot import errors
from certbot_dns_mijn_host.mijn_host import MijnHostClient


BASE_URL = "https://mijn.host/api/v2/"


class TestMijnHostClient(unittest.TestCase):
    def setUp(self):
        self.api_key = "test-api-key"
        self.client = MijnHostClient(api_key=self.api_key)
        self.domain = "example.com"
        self.headers = {
            "API-Key": self.api_key,
        }

    @patch("requests.get")
    def test_get_records(self, mock_get):
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": {"records": []}}
        mock_get.return_value = mock_response

        records = self.client.get_records(self.domain)

        mock_get.assert_called_once_with(
            urllib.parse.urljoin(BASE_URL, f"domains/{self.domain}/dns"),
            headers=self.headers,
        )
        self.assertEqual(records, {"data": {"records": []}})

    @patch("requests.put")
    @patch("requests.get")
    def test_add_txt_record(self, mock_get, mock_put):
        mock_get_response = MagicMock(spec=requests.Response)
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = {"data": {"records": []}}
        mock_get.return_value = mock_get_response

        mock_put_response = MagicMock(spec=requests.Response)
        mock_put_response.status_code = 200
        mock_put_response.json.return_value = {"success": True}
        mock_put.return_value = mock_put_response

        self.client.add_txt_record(self.domain, "test", "test_content", 3600)

        expected_records = [
            {
                "type": "TXT",
                "name": "test.",
                "value": "test_content",
                "ttl": 3600,
            }
        ]

        mock_put.assert_called_once_with(
            urllib.parse.urljoin(BASE_URL, f"domains/{self.domain}/dns"),
            headers=self.headers,
            data=json.dumps({"records": expected_records}),
        )

    @patch("requests.put")
    @patch("requests.get")
    def test_del_txt_record(self, mock_get, mock_put):
        mock_get_response = MagicMock(spec=requests.Response)
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = {
            "data": {
                "records": [
                    {
                        "type": "TXT",
                        "name": "test.",
                        "value": "test_content",
                        "ttl": 3600,
                    }
                ]
            }
        }
        mock_get.return_value = mock_get_response

        mock_put_response = MagicMock(spec=requests.Response)
        mock_put_response.status_code = 200
        mock_put.return_value = mock_put_response

        self.client.del_txt_record(self.domain, "test", "test_content")

        mock_put.assert_called_once_with(
            urllib.parse.urljoin(BASE_URL, f"domains/{self.domain}/dns"),
            headers=self.headers,
            data=json.dumps({"records": []}),
        )

    @patch("requests.get")
    def test_handle_response_non_ok_status(self, mock_get):
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_get.return_value = mock_response

        with self.assertRaises(errors.PluginError):
            self.client.get_records(self.domain)

    @patch("requests.get")
    def test_handle_response_non_json(self, mock_get):
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.text = "Non-JSON Response"
        mock_response.json.side_effect = json.decoder.JSONDecodeError(
            "Expecting value", "doc", 0
        )
        mock_get.return_value = mock_response

        with self.assertRaises(errors.PluginError):
            self.client.get_records(self.domain)


if __name__ == "__main__":
    unittest.main()
