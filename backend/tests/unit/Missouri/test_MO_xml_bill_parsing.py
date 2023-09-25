import pytest
import requests
from unittest.mock import patch, Mock

from backend.utils.missouri.MO_xml_bill_parsing import fetch_initial_xml

def mock_successful_response(*args, **kwargs):
    class MockResponse:
        @staticmethod
        def raise_for_status():
            pass

        @property
        def text(self):
            return "<xml>sample content</xml>"

    return MockResponse()

def test_fetch_initial_xml():
    url = "https://example.com/sample.xml"
    with patch.object(requests, "get", mock_successful_response):
        result = fetch_initial_xml(url)
        assert result == "<xml>sample content</xml>"
