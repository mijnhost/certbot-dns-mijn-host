import unittest
from unittest.mock import patch, Mock

import json
from certbot import errors
from certbot_dns_mijn_host.mijn_host import MijnHostClient


class TestMijnHostClient(unittest.TestCase):
    def setUp(self):
        self.api_key = "test"
        self.client = MijnHostClient(self.api_key)

    @patch("requests.get")
    def test_list_domains(self, mock_get):
        # Mocking the API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"domains": ["example.com"]}
        mock_get.return_value = mock_response

        # Call the list_domains method
        response = self.client.list_domains()

        # Assert that the GET request was made to the correct URL
        mock_get.assert_called_once_with(
            "https://mijn.host/api/v2/domains", headers={"API-Key": self.api_key}
        )

        # Assert the response is as expected
        self.assertEqual(response, {"domains": ["example.com"]})

    @patch("requests.get")
    def test_get_records(self, mock_get):
        # Mocking the API response
        domain = "example.com"
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "records": [{"type": "TXT", "name": "example.com", "value": "some_value"}]
        }
        mock_get.return_value = mock_response

        # Call the get_records method
        response = self.client.get_records(domain)

        # Assert that the GET request was made to the correct URL
        mock_get.assert_called_once_with(
            f"https://mijn.host/api/v2/domains/{domain}/dns",
            headers={"API-Key": self.api_key},
        )

        # Assert the response is as expected
        self.assertEqual(
            response,
            {
                "records": [
                    {"type": "TXT", "name": "example.com", "value": "some_value"}
                ]
            },
        )

    @patch("requests.get")
    def test_handle_response_non_ok_status(self, mock_get):
        # Mocking the API response with a non-OK status code
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_get.return_value = mock_response

        with self.assertRaises(errors.PluginError) as context:
            self.client.list_domains()

        self.assertIn(
            "Received non-OK status from Mijn Host API", str(context.exception)
        )

    @patch("requests.get")
    def test_handle_response_invalid_json(self, mock_get):
        # Mocking the API response with invalid JSON
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "Invalid JSON"
        mock_response.json.side_effect = json.decoder.JSONDecodeError(
            "Expecting value", "Invalid JSON", 0
        )
        mock_get.return_value = mock_response

        with self.assertRaises(errors.PluginError) as context:
            self.client.list_domains()

        self.assertIn("API response with non-JSON", str(context.exception))


if __name__ == "__main__":
    unittest.main()
