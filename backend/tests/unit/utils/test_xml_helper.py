
import pytest
from lxml import etree
from datetime import datetime
from backend.utils.xml_helper import get_text, parse_date

# Test data
test_data_get_text = [
    {"xpath": "child1", "default": None, "expected": "Text1"},
    {"xpath": "child2", "default": None, "expected": ""},
    {"xpath": "child3", "default": None, "expected": None},
    {"xpath": "child3", "default": "Default Text", "expected": "Default Text"},
]

# Create XML root element for testing
@pytest.fixture
def xml_root():
    xml_content = '''
    <root>
        <child1>Text1</child1>
        <child2></child2>
    </root>
    '''
    return etree.fromstring(xml_content)

# Test cases for get_text function
@pytest.mark.parametrize("test_data", test_data_get_text)
def test_get_text(xml_root, test_data):
    result = get_text(xml_root, test_data['xpath'], test_data['default'])
    assert result == test_data['expected']

def test_parse_date_with_valid_date():
    date_str = "2023-04-01"
    expected_date = datetime(2023, 4, 1)
    assert parse_date(date_str) == expected_date

def test_parse_date_with_invalid_date():
    date_str = "invalid date"
    assert parse_date(date_str) is None

def test_parse_date_with_none():
    assert parse_date(None) is None
