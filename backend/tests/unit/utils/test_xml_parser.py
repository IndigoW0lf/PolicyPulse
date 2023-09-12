import os
import json
import logging
from backend.utils.xml_parser import parse_xml_files, parse_bill
from lxml import etree
import pytest

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Get the absolute path to the directory containing your script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the absolute path to the XML file
xml_file_path = os.path.join(script_dir, '..', '..', 'data', 'test.xml')

# Mock database list to simulate database operations during testing
mock_database = []

def mock_save_to_database(data):
    logging.info("mock_save_to_database called")
    mock_database.append(data)

@pytest.fixture
def xml_data():
    with open(xml_file_path, 'r') as file:
        data = file.read()
    return data

# @pytest.fixture
# def xml_content(xml_data):
#     tree = etree.fromstring(xml_data)
#     xml_json = json.dumps({tree.tag: tree.text, **{child.tag: child.text for child in tree.iterchildren()}})
#     return xml_json

@pytest.fixture
def bill_data():
    return {
        "number": "100",
        "updateDate": "2023-05-15T12:00:00Z",
        "originChamber": "House",
        "type": "HR",
        "introducedDate": "2023-05-01",
        "congress": "118",
        "display_title": "A mock resolution to discuss mock topics on a mock date.",
        "actions": [
            {
                "actionDate": "2023-05-01",
                "actionTime": "10:00:00",
                "text": "Mock action text 1.",
                "type": "Committee",
                "actionCode": "M12345",
                "sourceSystem": {
                    "code": "1",
                    "name": "Mock Source System 1"
                }
            },
            {
                "actionDate": "2023-05-02",
                "actionTime": "11:00:00",
                "text": "Mock action text 2.",
                "type": "Floor",
                "actionCode": "M67890",
                "sourceSystem": {
                    "code": "2",
                    "name": "Mock Source System 2"
                }
            }
        ],
        "sponsors": [
            {
                "bioguideId": "M123456",
                "fullName": "Rep. Mockname, Mock [D-MO]",
                "firstName": "Mock",
                "lastName": "Mockname",
                "party": "D",
                "state": "MO",
                "identifiers": {
                    "bioguideId": "M123456"
                },
                "isByRequest": "N"
            }
        ],
        "committees": [
            {
                "name": "Mock Committee 1",
                "chamber": "House",
                "committee_code": "C12345"
            }
        ],
        "coSponsors": [
            {
                "politician_id": "P12345",
                "bill_id": "B12345"
            }
        ],
        "amendments": [
            {
                "amendment_number": "A12345",
                "description": "Mock Amendment Description 1",
                "date_proposed": "2023-05-10",
                "status": "Proposed"
            }
        ],
        "policyArea": {
            "name": "Mock Policy Area"
        },
        "subjects": {
            "legislativeSubjects": [
                {"name": "Mock Legislative Subject 1"},
                {"name": "Mock Legislative Subject 2"},
                {"name": "Mock Legislative Subject 3"},
                {"name": "Mock Legislative Subject 4"},
                {"name": "Mock Legislative Subject 5"}
            ],
            "policyArea": {
                "name": "Mock Policy Area"
            },
            "billSubjects": [
                {"name": "Mock Bill Subject 1"}
            ],
            "otherSubjects": [
                {
                    "name": "Mock Other Subject 1",
                    "parentSubject": {"name": "Mock Parent Subject 1"}
                }
            ],
            "primarySubjects": [
                {
                    "name": "Mock Primary Subject 1",
                    "parentSubject": {"name": "Mock Parent Subject 1"}
                }
            ]
        },
        "summaries": [
            {
                "versionCode": "01",
                "actionDate": "2023-05-01",
                "actionDesc": "Introduced in House",
                "updateDate": "2023-05-10T14:00:00Z",
                "text": "<p>This mock resolution provides for a mock event on a mock date to discuss mock topics.</p>"
            }
        ],
        "titles": [
            {
                "titleType": "Display Title",
                "title": "A mock resolution to discuss mock topics on a mock date."
            },
            {
                "titleType": "Official Title as Introduced",
                "title": "A mock resolution to discuss mock topics on a mock date."
            }
        ],
        "textVersions": [],
        "fullBillTexts": [
            {
                "title": "Mock Full Bill Text Title 1",
                "bill_metadata": "Mock Bill Metadata 1",
                "actions": "Mock Full Bill Text Actions 1",
                "sections": "Mock Full Bill Text Sections 1"
            }
        ],
        "latestAction": {
            "actionDate": "2023-05-02",
            "text": "Mock latest action text.",
            "actionTime": "11:00:00"
        },
        "relatedBills": [
            {
                "bill_id": "B12345",
                "related_bill_id": "B67890"
            }
        ],
        "vetoMessages": [
            {
                "date": "2023-05-15",
                "message": "Mock Veto Message 1",
                "president": "Mock President 1",
                "text": "Mock Veto Message Text 1"
            }
        ]
    }

@pytest.fixture
def reset_mock_database():
    """Fixture to reset the mock database before each test."""
    mock_database.clear()

def get_text(tree, xpath):
    """Function to get text from an XML element based on the given XPath."""
    element = tree.find(xpath)
    return element.text if element is not None else None

def test_get_text():
    xml_data = '<root><child>Test</child></root>'
    tree = etree.fromstring(xml_data)
    result = get_text(tree, './/child')
    assert result == 'Test', f'Expected "Test", got "{result}"'

def test_parse_bill(xml_data, bill_data):
    """Test the parse_bill function."""
    xml_data = xml_data.replace('<?xml version="1.0" encoding="utf-8" standalone="no"?>', '')
    tree = etree.fromstring(xml_data)
    parsed_data = parse_bill(tree)
    print("Parsed Data:", parsed_data)
    print("Bill Data:", bill_data)
    assert parsed_data == bill_data

def test_save_to_database(bill_data, reset_mock_database):
    """Test the save_to_database function."""
    mock_save_to_database(bill_data)
    assert mock_database[0] == bill_data

def test_parse_xml_files(tmpdir, xml_data, bill_data, reset_mock_database):
    """Test the parse_xml_files function."""
    keywords = ["resolution"]
    
    # Create a temporary directory and XML file for testing
    p = tmpdir.mkdir("sub").join("test.xml")
    p.write(xml_data)

    # Check the xml_data and keywords
    print("XML Data:", xml_data)
    print("Keywords:", keywords)
    
    parse_xml_files(str(tmpdir), keywords, save_function=mock_save_to_database)

    logging.info(f"mock_database: {mock_database}")

    # Check the mock_database list
    print("mock_database:", mock_database)
    
    assert mock_database[0] == bill_data

if __name__ == "__main__":
    pytest.main([__file__])