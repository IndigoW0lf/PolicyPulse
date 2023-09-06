import pytest
import os
from datetime import date
from backend.api.congress_api import make_request, manage_api_state, create_bill, fetch_sponsor_id, store_full_bill_text, fetch_individual_text_version
from backend.api.rate_limiter import ApiState
from backend.api.congress_api import Bill, BillFullText, Politician
from backend import create_app, db
from flask import current_app
from ..unit.test_models.conftest import create_politician, create_bill
from unittest.mock import patch, Mock
from sqlalchemy import text


@pytest.fixture
def app():
    os.environ['FLASK_CONFIG'] = 'testing'
    app = create_app()
    return app

@pytest.fixture
def api_state_fixture():
    return ApiState()

def my_manage_api_state(api_state, batch_size):
    api_state.batch_counter += 1

    if api_state.batch_counter >= batch_size:
        api_state.batch_counter = 0
        return True

    return False

def test_manage_api_state(app, api_state_fixture): 
    api_state_fixture.batch_counter = 49
    commit_needed = manage_api_state(api_state_fixture, 50)
    assert commit_needed == True
    assert api_state_fixture.batch_counter == 0

    with app.test_request_context():  # Manually manage the application context
        if commit_needed:
            try:
                db.session.commit()  # Commit the session if needed
                current_app.logger.info("Database commit successful.")
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f"Database commit failed: {e}")

# Test for make_request with successful API call
@patch('requests.get')
def test_make_request(mock_get, api_state_fixture):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {'results': [1, 2, 3]}
    data = make_request('fake_endpoint', api_state_fixture)
    assert data == [1, 2, 3]

# Test for make_request with unsuccessful API call
@patch('requests.get')
def test_make_request_error(mock_get, api_state_fixture):
    mock_get.return_value.status_code = 400
    data = make_request('fake_endpoint', api_state_fixture)  
    assert data == []

def test_create_bill(init_database):
    session = db.session

     # Check the state of the database at the start of the test
    existing_bills = session.query(Bill).all()
    print("Existing bills at start of test:", existing_bills)

    session.execute(text("SELECT setval('bill_id_seq', (SELECT MAX(id) FROM bill))"))

    # Assuming fetch_sponsor_id returns 1 for 'Test Sponsor'
    with patch('backend.api.congress_api.fetch_sponsor_id', return_value=1):
        bill = create_bill()
    print("Created bill with attributes:", bill.__dict__)
    session.add(bill)
    session.commit()
    print("Bill committed with ID:", bill.id)
    session.close()  # Close the current session

    new_session = init_database.session  # Create a new session

    # Retrieve the bill from the database and assert that its attributes are as expected
    retrieved_bill = new_session.query(Bill).filter_by(bill_number='123').first()
    print("Retrieved bill:", retrieved_bill)
    assert retrieved_bill.title == 'Test Bill'
    assert retrieved_bill.summary == 'This is a test bill'
    assert retrieved_bill.bill_number == '123'
    assert retrieved_bill.sponsor_name == 'Test Sponsor'
    assert retrieved_bill.sponsor_id == 1
    assert retrieved_bill.date_introduced.strftime('%Y-%m-%d') == '2023-01-01'
    assert retrieved_bill.status == 'Active'
    assert retrieved_bill.committee == 'Committee1,Committee2'
    assert retrieved_bill.full_bill_link == 'http://test.com'
    assert retrieved_bill.tags == 'Subject1,Subject2'
    assert retrieved_bill.last_action_date.strftime('%Y-%m-%d')== '2023-01-02'
    assert retrieved_bill.last_action_description == 'Test Action'

def test_store_full_bill_text(app, init_database):
    session = init_database.session

    xml_data = {
        'title': 'XML Title',
        'publisher': 'XML Publisher',
        'date': '2023-01-03',
        'format': 'XML Format',
        'language': 'XML Language',
        'rights': 'XML Rights'
    }

    with app.app_context():

        politician = create_politician()
        session.add(politician)
        session.commit()

        # Create a new Bill object directly within the test function
        bill = create_bill()
        session.add(bill)
        session.commit()
        
        # Create a new BillFullText object using the ID of the newly created Bill
        new_bill_full_text = BillFullText(
            bill_id=bill.id, 
            title='XML Title', 
            bill_metadata=xml_data
        )

        session.add(new_bill_full_text)
        session.commit()

        # Verify that the BillFullText object was saved correctly
        saved_bill_full_text = BillFullText.query.filter_by(bill_id=bill.id).first()
        assert saved_bill_full_text is not None, "BillFullText object not found in database"
        assert saved_bill_full_text.title == 'XML Title'
        assert saved_bill_full_text.bill_metadata == xml_data


# Test to see that fetch_individual_text_version correctly fetches XML data
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
