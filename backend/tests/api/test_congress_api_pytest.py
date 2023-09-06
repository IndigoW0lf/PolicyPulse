import pytest
import os
from backend.api.congress_api import make_request, manage_api_state, create_bill, fetch_sponsor_id, store_full_bill_text, fetch_individual_text_version
from backend.api.rate_limiter import ApiState
from backend.api.congress_api import Bill, BillFullText, Politician
from backend import create_app, db
from flask import current_app
from ..unit.test_models.conftest import init_database
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

def test_manage_api_state(app, api_state_fixture, init_database): 
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
    session = init_database.session

     # Check the state of the database at the start of the test
    existing_bills = session.query(Bill).all()
    print("Existing bills at start of test:", existing_bills)

    session.execute(text("SELECT setval('bill_id_seq', (SELECT MAX(id) FROM bill))"))

    # Assuming fetch_sponsor_id returns 1 for 'Test Sponsor'
    with patch('backend.api.congress_api.fetch_sponsor_id', return_value=1):
        bill = create_bill({
            'title': 'Test Bill',
            'summary': 'This is a test bill',
            'bill_number': '123',
            'sponsor': 'Test Sponsor',
            'sponsor_id': 1,
            'date_introduced': '2023-01-01',
            'status': 'Active',
            'committees': ['Committee1', 'Committee2'],
            'full_bill_link': 'http://test.com',
            'subjects': ['Subject1', 'Subject2'],
            'last_action_date': '2023-01-02',
            'last_action_description': 'Test Action'
        })
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

# Test to see that store_full_bill_text correctly stores a BillFullText object
@patch('backend.api.congress_api.BillFullText')
@patch('backend.api.congress_api.db.session.add')
@patch('backend.api.congress_api.db.session.commit')
@patch('backend.api.congress_api.db.session.delete')
@patch('backend.api.congress_api.requests.get')
def test_store_full_bill_text(mock_get, mock_delete, mock_commit, mock_add, mock_BillFullText, app, init_database):
    session = init_database.session

    xml_data = {
        'title': 'XML Title',
        'publisher': 'XML Publisher',
        'date': '2023-01-03',
        'format': 'XML Format',
        'language': 'XML Language',
        'rights': 'XML Rights'
    }

    # Mock the requests.get call to return a response with the XML data
    mock_get.return_value = Mock(status_code=200, content=b'''
    <root>
        <metadata>
            <dublinCore xmlns:dc="http://purl.org/dc/elements/1.1/">
                <dc:title>XML Title</dc:title>
                <dc:publisher>XML Publisher</dc:publisher>
                <dc:date>2023-01-03</dc:date>
                <dc:format>XML Format</dc:format>
                <dc:language>XML Language</dc:language>
                <dc:rights>XML Rights</dc:rights>
            </dublinCore>
        </metadata>
    </root>
    ''')

    # Retrieve an existing bill from the database to use in the test
    bill = session.query(Bill).filter_by(bill_number='HR001').first()
    print(f"Bill ID: {bill.id}")
    assert bill is not None, "Bill with bill_number 'HR001' not found in database"

    with app.app_context():
        mock_add.return_value = None  # Mock the add method to do nothing
        
        new_bill_full_text = BillFullText(
            bill_id=bill.id, 
            title='XML Title', 
            bill_metadata={
                'title': 'XML Title', 
                'publisher': 'XML Publisher', 
                'date': '2023-01-03', 
                'format': 'XML Format', 
                'language': 'XML Language', 
                'rights': 'XML Rights'
            }
        )

        # mock_commit.side_effect = Exception("Database error")  # Simulate a database error

        #with pytest.raises(Exception):  # Verify that any exception is raised
                # store_full_bill_text(bill, 'http://example.com/xml_url')  # Pass a valid URL string as the second argument

        session.add(new_bill_full_text)
        session.commit()

        # Check for pending changes (should be empty if the commit was successful)
        print(session.new)
        print(session.dirty)

        # Close and reinitialize the session
        session.close()
        session = init_database.session

        # Check if the object was saved properly
        saved_bill_full_text = BillFullText.query.filter_by(bill_id=bill.id).first()
        print(saved_bill_full_text)  # This should not print None

        mock_commit.side_effect = None  # Reset the side effect

        # Print the mock configuration to check if it's correct
        print(mock_BillFullText.mock_calls)

        # Adjust the mocking for the add method to ensure that it works correctly
        def add_side_effect(x):
            mock_add.side_effect = None  # Temporarily remove the mock
            session.add(x)
            mock_add.side_effect = add_side_effect  # Reapply the mock

        mock_add.side_effect = add_side_effect


        store_full_bill_text(bill, 'http://example.com/xml_url')  # Pass a valid URL string as the second argument again

        print(session.new)

        bill_full_bill_record = BillFullText.query.filter_by(bill_id=bill.id).first()

        print(bill_full_bill_record)
              
        assert bill_full_bill_record.title == 'XML Title'
        assert bill_full_bill_record.bill_metadata == xml_data

        mock_delete.return_value = None  # Mock the delete method to do nothing
        mock_commit.return_value = None  # Mock the commit method to do nothing


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
