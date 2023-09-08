import pytest
from datetime import date
from ...api.rate_limiter import ApiState 
import os
from backend.api.congress_api import (
    make_request, manage_api_state, fetch_sponsor_id, 
    store_full_bill_text, fetch_individual_text_version, 
    create_bill, fetch_list_of_bills, fetch_individual_bill_details, 
    fetch_text_versions_of_bill, store_bill, main
)
from backend.database.models import Bill, BillFullText, Politician
from backend import create_app, db
from unittest.mock import patch

# Set environment variable at the beginning of the file
os.environ['FLASK_CONFIG'] = 'testing'

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        yield app

@pytest.fixture
def db_session(app):
    with app.app_context():
        db.create_all()
        db.session.begin_nested()
        try:
            yield db.session
        finally:
            db.session.rollback()
            db.drop_all()

@pytest.fixture
def bill(db_session):
    bill = Bill(
        title="Test Bill",
        summary="This is a test bill",
        bill_number="123",
        sponsor_name="Test Sponsor",
        sponsor_id=1,
        date_introduced=date(2023, 1, 1),
        status="Active",
        committee="Committee1,Committee2",
        full_bill_link="http://test.com",
        tags="Subject1,Subject2",
        last_action_date=date(2023, 1, 2),
        last_action_description="Test Action"
    )
    db_session.add(bill)
    db_session.commit()
    return bill

@pytest.fixture
def politician(db_session):
    politician = Politician(name="Test Politician")
    db_session.add(politician)
    db_session.commit()
    return politician

@pytest.fixture
def bill_full_text(db_session, bill):
    xml_data = {
        'title': 'XML Title',
        'publisher': 'XML Publisher',
        'date': '2023-01-03',
        'format': 'XML Format',
        'language': 'XML Language',
        'rights': 'XML Rights'
    }
    bill_full_text = BillFullText(bill_id=bill.id, title='XML Title', bill_metadata=xml_data)
    db_session.add(bill_full_text)
    db_session.commit()
    return bill_full_text

@pytest.fixture
def api_state_fixture():
    return ApiState()

def my_manage_api_state(api_state, batch_size):
    api_state.batch_counter += 1

    if api_state.batch_counter >= batch_size:
        api_state.batch_counter = 0
        return True

    return False

def test_manage_api_state():
    api_state = ApiState()
    api_state.batch_counter = 49
    commit_needed = manage_api_state(api_state, 50)
    
    assert commit_needed == True
    assert api_state.batch_counter == 0

@patch('requests.get')
def test_make_request(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {'results': [1, 2, 3]}
    
    api_state = ApiState()
    data = make_request('fake_endpoint', api_state)
    
    assert data == [1, 2, 3]

# Test for make_request with unsuccessful API call
@patch('requests.get')
def test_make_request_error(mock_get, api_state_fixture):
    mock_get.return_value.status_code = 400
    data = make_request('fake_endpoint', api_state_fixture)  
    assert data == []

@patch('requests.get')
def test_make_request_error(mock_get):
    mock_get.return_value.status_code = 400
    
    api_state = ApiState()
    data = make_request('fake_endpoint', api_state)
    
    assert data == []

def test_create_bill():
    item = {
        'title': 'Test Bill',
        'summary': 'This is a test bill',
        'bill_number': '123',
        'sponsor': 'Test Sponsor',
        'date_introduced': date(2023, 1, 1),
        'status': 'Active',
        'committees': ['Committee1', 'Committee2'],
        'full_bill_link': 'http://test.com',
        'subjects': ['Subject1', 'Subject2'],
        'last_action_date': date(2023, 1, 2),
        'last_action_description': 'Test Action'
    }
    
    with patch('backend.api.congress_api.fetch_sponsor_id', return_value=1):
        bill = create_bill(item)
    
    assert bill.title == 'Test Bill'
    assert bill.summary == 'This is a test bill'
    assert bill.bill_number == '123'
    assert bill.sponsor_name == 'Test Sponsor'
    assert bill.sponsor_id == 1
    assert bill.date_introduced.strftime('%Y-%m-%d') == '2023-01-01'
    assert bill.status == 'Active'
    assert bill.committee == 'Committee1,Committee2'
    assert bill.full_bill_link == 'http://test.com'
    assert bill.tags == 'Subject1,Subject2'
    assert bill.last_action_date.strftime('%Y-%m-%d') == '2023-01-02'
    assert bill.last_action_description == 'Test Action'

def test_store_full_bill_text(app, db_session, politician, bill, bill_full_text):
    session = db_session

    xml_data = {
        'title': 'XML Title',
        'publisher': 'XML Publisher',
        'date': '2023-01-03',
        'format': 'XML Format',
        'language': 'XML Language',
        'rights': 'XML Rights'
    }

    with app.app_context():
        session.add(politician)
        session.commit()

        session.add(bill)
        session.commit()
        
        new_bill_full_text = BillFullText(
            bill_id=bill.id, 
            title='XML Title', 
            bill_metadata=xml_data
        )
        
        session.add(new_bill_full_text)
        session.commit()

        saved_bill_full_text = BillFullText.query.filter_by(bill_id=bill.id).first()
        assert saved_bill_full_text is not None
        assert saved_bill_full_text.title == 'XML Title'
        assert saved_bill_full_text.bill_metadata == xml_data


@patch('requests.get')
def test_fetch_individual_text_version(mock_get):
    xml_content = """
    <root>
        <metadata>
            <dublinCore>
                <dc:title xmlns:dc="http://purl.org/dc/elements/1.1/">XML Title</dc:title>
                <dc:publisher xmlns:dc="http://purl.org/dc/elements/1.1/">XML Publisher</dc:publisher>
                <dc:date xmlns:dc="http://purl.org/dc/elements/1.1/">2023-01-03</dc:date>
                <dc:format xmlns:dc="http://purl.org/dc/elements/1.1/">XML Format</dc:format>
                <dc:language xmlns:dc="http://purl.org/dc/elements/1.1/">XML Language</dc:language>
                <dc:rights xmlns:dc="http://purl.org/dc/elements/1.1/">XML Rights</dc:rights>
            </dublinCore>
        </metadata>
    </root>
    """

    mock_get.return_value.status_code = 200
    mock_get.return_value.content = xml_content.encode('utf-8')

    xml_url = 'http://test.com/xml'
    parsed_data = fetch_individual_text_version(xml_url)

    assert parsed_data == {
        'title': 'XML Title',
        'publisher': 'XML Publisher',
        'date': '2023-01-03',
        'format': 'XML Format',
        'language': 'XML Language',
        'rights': 'XML Rights'
    }

if __name__ == "__main__":
    pytest.main()