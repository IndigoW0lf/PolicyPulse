
from datetime import datetime
from unittest.mock import Mock, patch
from lxml import etree
import pytest
from backend.utils.xml_helper import get_text, parse_date
from backend.utils.xml_bill_parser import parse_bill, parse_amendments, parse_amendment_actions, parse_amendment_links,parse_laws, parse_amended_bill, parse_actions, parse_bill_titles, parse_cosponsors, parse_related_bills, parse_subjects, parse_notes, parse_committees, parse_recorded_votes, parse_policy_area, get_or_create_politician
from backend.database.models import Action, ActionCode, ActionType, AmendedBill, Amendment, AmendmentAction, AmendmentLink, Bill, BillFullText, BillTitle, Committee, CoSponsor, Law, LOCSummary, LOCSummaryCode, Note, PolicyArea, Politician, RecordedVote, RelatedBill, Subject, VetoMessage


@pytest.fixture
def xml_root():
    from lxml import etree
    with open('backend/data/text.xml', 'r') as file:  
        xml_content = file.read()
    return etree.fromstring(xml_content)

@pytest.fixture
def session():
    class MockSession:
        def query(self, *args, **kwargs):
            return self

        def filter_by(self, *args, **kwargs):
            return self

        def first(self):
            return None

        def add(self, obj):
            pass

        def commit(self):
            pass

        def flush(self):
            pass

    return MockSession()


# Tests for get_text function
def test_get_text():
    xml_content = '<root><child>text content</child></root>'
    root = etree.fromstring(xml_content)
    
    # Test case 1: Element found and has text content
    assert get_text(root, 'child') == 'text content'
    
    # Test case 2: Element not found
    assert get_text(root, 'not_found') is None
    
    # Test case 3: Element found but has no text content
    assert get_text(root, 'child/no_text') is None

# Tests for parse_date function
def test_parse_date():
    
    # Test case 1: Valid date string
    assert parse_date('2023-04-01') == datetime(2023, 4, 1)
    
    # Test case 2: Invalid date string
    with pytest.raises(ValueError):
        parse_date('invalid date')
    
    # Test case 3: None input
    assert parse_date(None) is None



def test_parse_bill(mock_session, xml_root):
    # Mocking the functions called within parse_bill
    with patch('xml_bill_parser.parse_amendments') as mock_parse_amendments, \
         patch('xml_bill_parser.parse_committees') as mock_parse_committees, \
         patch('xml_bill_parser.parse_related_bills') as mock_parse_related_bills, \
         patch('xml_bill_parser.parse_actions') as mock_parse_actions, \
         patch('xml_bill_parser.parse_sponsors') as mock_parse_sponsors, \
         patch('xml_bill_parser.parse_subjects') as mock_parse_subjects, \
         patch('xml_bill_parser.parse_titles') as mock_parse_titles, \
         patch('xml_bill_parser.parse_summary') as mock_parse_summary:

        # Set return values for the mocks if necessary
        # For example:
        mock_parse_amendments.return_value = ...
        
        # Call the function under test
        bill = parse_bill(xml_root, mock_session)

        # Now you would add assertions to check the attributes of the returned bill object
        # The exact assertions will depend on your implementation of parse_bill
        # For example:
        assert bill.bill_number == 'U123'



# Now, let's write the test case for the parse_amendments method
def test_parse_amendments(mock_session, bill_details):
    # Import the method to be tested
    from backend.utils.xml_bill_parser import parse_amendments

    # Call the method with the mocked session and sample bill_details
    amendments = parse_amendments(mock_session, bill_details, 1)

    # Verify the output
    assert len(amendments) == 2

    # Verify the details of the first amendment
    assert amendments[0].amendment_number == "1"
    assert amendments[0].amendment_type == "Main"
    assert amendments[0].description == "Amendment Description 1"
    assert amendments[0].proposed_date == "2023-09-01"
    assert amendments[0].status == "Accepted"
    assert amendments[0].text == "Amendment Text 1"

    # Verify the details of the second amendment
    assert amendments[1].amendment_number == "2"
    assert amendments[1].amendment_type == "Additional"
    assert amendments[1].description == "Amendment Description 2"
    assert amendments[1].proposed_date == "2023-09-02"
    assert amendments[1].status == "Rejected"
    assert amendments[1].text == "Amendment Text 2"


def test_parse_amendment_actions(mock_session, amendment_actions_details):
    amendment_actions = parse_amendment_actions(amendment_actions_details, mock_session)
    
    assert len(amendment_actions) == 2
    
    assert amendment_actions[0].action_date == '2023-04-01'
    assert amendment_actions[0].chamber == 'Senate'
    assert amendment_actions[0].action_desc == 'Action Description 1'
    
    assert amendment_actions[1].action_date == '2023-04-02'
    assert amendment_actions[1].chamber == 'House'
    assert amendment_actions[1].action_desc == 'Action Description 2'


# Test case for parse_amendment_links function
def test_parse_amendment_links(xml_amendment_links_root):
    amendment_links = parse_amendment_links(xml_amendment_links_root)
    
    assert len(amendment_links) == 2
    
    assert amendment_links[0].name == "Link 1"
    assert amendment_links[0].url == "http://example.com/link1"
    
    assert amendment_links[1].name == "Link 2"
    assert amendment_links[1].url == "http://example.com/link2"


def test_parse_committees(xml_root):
    committees_list = parse_committees(xml_root.find('bill'))
    
    assert len(committees_list) == 1
    
    committee = committees_list[0]
    assert committee.system_code == 'UC001'
    assert committee.name == 'Committee on Glitter Regulation'
    assert committee.chamber == 'Senate'
    assert committee.committee_type == 'Standing'
    
    assert len(committee.activities) == 1
    activity = committee.activities[0]
    assert activity.name == 'Debating Glitter Pollution'
    assert activity.date == datetime.date(2023, 4, 2)
    
    assert len(committee.subcommittees) == 1
    subcommittee = committee.subcommittees[0]
    assert subcommittee.system_code == 'UCS01'
    assert subcommittee.name == 'Subcommittee on Unicorn Farts and Climate Change'
    
    assert len(subcommittee.activities) == 1
    activity = subcommittee.activities[0]
    assert activity.name == "Discussing Unicorn Farts' Impact on Global Warming"
    assert activity.date == datetime.date(2023, 4, 3)


def test_parse_cosponsors(xml_root):
    cosponsors_list = parse_cosponsors(xml_root.find('bill'))
    
    assert len(cosponsors_list) == 1
    
    cosponsor = cosponsors_list[0]
    assert cosponsor.bioguide_id == 'U67890'
    assert cosponsor.full_name == 'Rep. Rainbow Sprinklehoof'
    assert cosponsor.first_name == 'Rainbow'
    assert cosponsor.last_name == 'Sprinklehoof'
    assert cosponsor.middle_name == 'Sparkly'
    assert cosponsor.party == 'Harmonious Party'
    assert cosponsor.state == 'Cloud Kingdom'
    assert cosponsor.district == '2'
    assert cosponsor.sponsorship_date == datetime.date(2023, 4, 2)
    assert cosponsor.is_original_cosponsor == True
    assert cosponsor.sponsorship_withdrawn_date == None


def test_parse_laws(xml_root):
    laws_list = parse_laws(xml_root.find('bill'))
    
    assert len(laws_list) == 1
    
    law = laws_list[0]
    assert law.law_type == 'UL'
    assert law.number == '12345'


def test_parse_notes(xml_root):
    notes_list = parse_notes(xml_root.find('bill'))
    
    assert len(notes_list) == 1
    
    note = notes_list[0]
    assert note.text == 'Note: This bill includes provisions to mitigate the effects of unicorn flatulence on the environment.'
    
    assert len(note.links) == 1
    link = note.links[0]
    assert link.name == 'Fart Mitigation Strategies'
    assert link.url == 'https://www.unicornsenate.gov/notes/FartMitigation'


def test_parse_policy_areas(xml_root):
    policy_areas_list = parse_policy_area(xml_root.find('bill'))
    
    assert len(policy_areas_list) == 1
    
    policy_area = policy_areas_list[0]
    assert policy_area.name == 'Unicorn Conservation and Glitter Pollution Control'


def test_parse_related_bills(xml_root):
    related_bills_list = parse_related_bills(xml_root.find('bill'))
    
    assert len(related_bills_list) == 1
    
    related_bill = related_bills_list[0]
    assert related_bill.title == 'The Rainbow Preservation Act'
    assert related_bill.congress == '1'
    assert related_bill.number == 'RB789'
    assert related_bill.bill_type == 'RB'
    assert related_bill.latest_action_date == datetime.date(2023, 4, 4)
    assert related_bill.latest_action_text == 'Debated in the Magical Creatures Council'
    assert related_bill.latest_action_time == '14:00:00'
    
    assert len(related_bill.relationship_details) == 1
    relationship_detail = related_bill.relationship_details[0]
    assert relationship_detail.relationship_type == 'Amendment'
    assert relationship_detail.identified_by == 'MC123'


def test_get_or_create_politician(xml_root):
    sponsors_list = get_or_create_politician(xml_root.find('bill'))
    
    assert len(sponsors_list) == 1
    
    sponsor = sponsors_list[0]
    assert sponsor.bioguide_id == 'U12345'
    assert sponsor.full_name == 'Sen. Sparkle Rainbowdash'
    assert sponsor.first_name == 'Sparkle'
    assert sponsor.last_name == 'Rainbowdash'
    assert sponsor.party == 'Unicorn Party'
    assert sponsor.state == 'Fantasy Land'
    assert sponsor.district == '1'
    assert sponsor.sponsorship_date == datetime.date(2023, 4, 1)


def test_parse_subjects(xml_root):
    legislative_subjects_list = parse_subjects(xml_root.find('bill'))
    
    assert len(legislative_subjects_list) == 2
    
    legislative_subject1 = legislative_subjects_list[0]
    assert legislative_subject1.name == 'Unicorn Habitat Conservation'
    
    legislative_subject2 = legislative_subjects_list[1]
    assert legislative_subject2.name == 'Glitter Pollution Control'
