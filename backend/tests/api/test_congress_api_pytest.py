# import pytest
# import os
# import logging
# from datetime import date
# from unittest.mock import patch
# from backend.api.congress_api import (
#     make_request, manage_api_state, fetch_sponsor_id, 
#     store_full_bill_text, fetch_individual_text_version, 
#     create_bill, fetch_list_of_bills, fetch_individual_bill_details, 
#     fetch_text_versions_of_bill, store_bill, main
# )
# from backend.database.models import Bill, BillFullText, Politician
# from backend.tests.factories.bill_factory import BillFactory
# from backend import create_app, db

# logger = logging.getLogger(__name__)

# # Set environment variable at the beginning of the file
# os.environ['FLASK_CONFIG'] = 'testing'

# @pytest.fixture
# def app(session):
#     app = create_app('testing')
#     with app.app_context():
#         yield app

# @pytest.fixture
# def bill_factory(session):
#     def _bill_factory(**kwargs):
#         bill = BillFactory(**kwargs)
#         session.add(bill)
#         session.commit()
#         return bill
#     return _bill_factory

# @pytest.fixture
# def politician(politician_factory):
#     return politician_factory(name="Test Politician")

# @pytest.fixture
# def bill_full_text(bill_full_text_factory, bill):
#     xml_data = {
#         'title': 'XML Title',
#         'publisher': 'XML Publisher',
#         'date': '2023-01-03',
#         'format': 'XML Format',
#         'language': 'XML Language',
#         'rights': 'XML Rights'
#     }
#     return bill_full_text_factory(bill_id=bill.id, title='XML Title', bill_metadata=xml_data)

# @pytest.fixture
# def api_state_fixture():
#     from backend.api.rate_limiter import ApiState
#     return ApiState()

# def test_create_bill(session, client, bill_factory):
#     bill_data = {
#         "title": "Test Bill",
#         "summary": "This is a test bill",
#         "bill_number": "123",
#         "sponsor": "Test Sponsor",
#         "sponsor_id": 1,
#         "date_introduced": date(2023, 1, 2),
#         "status": "Active",
#         "committee": "Committee1,Committee2",
#         "full_bill_link": "http://test.com",
#         "tags": "Subject1,Subject2",
#         "last_action_date": date(2023, 1, 2),
#         "last_action_description": "Test Action"
#     }
#     bill = bill_factory(**bill_data)
#     session.add(bill)
#     session.commit()
    
#     response = client.post('/bills/', json=bill_data)
    
#     logger.info(f"Creating bill with data: {bill_data}")
    
#     assert response.status_code == 201
#     assert response.json['title'] == "Test Bill"
#     assert response.json['summary'] == "This is a test bill"
#     assert response.json['bill_number'] == "123"
#     assert response.json['sponsor'] == "Test Sponsor"
#     assert response.json['sponsor_id'] == 1
#     assert response.json['date_introduced'] == date(2023, 1, 2)
#     assert response.json['status'] == "Active"
#     assert response.json['committee'] == "Committee1,Committee2"
#     assert response.json['full_bill_link'] == "http://test.com"
#     assert response.json['tags'] == "Subject1,Subject2"
#     assert response.json['last_action_date'] == date(2023, 1, 2)
#     assert response.json['last_action_description'] == "Test Action"
    
#     session.rollback()

# def test_manage_api_state(app, api_state_fixture):
#     with app.app_context():
#         commit_needed = manage_api_state(api_state_fixture, 50)
    
#     logger.info(f"Testing manage_api_state with batch_counter: {api_state_fixture.batch_counter}")
#     assert commit_needed == True
#     assert api_state_fixture.batch_counter == 0

# @patch('requests.get')
# def test_make_request(mock_get, api_state_fixture):
#     mock_get.return_value.status_code = 200
#     mock_get.return_value.json.return_value = {'results': [1, 2, 3]}
    
#     data = make_request('fake_endpoint', api_state_fixture)
    
#     logger.info(f"Testing make_request with data: {data}")
#     assert data == [1, 2, 3]

# @patch('requests.get')
# def test_make_request_error(mock_get, api_state_fixture):
#     mock_get.return_value.status_code = 400
#     data = make_request('fake_endpoint', api_state_fixture)  
    
#     logger.error(f"Testing make_request_error with data: {data}")
#     assert data == []

# @patch('requests.get')
# def test_make_request_error(mock_get, api_state_fixture):
#     mock_get.return_value.status_code = 400
    
#     data = make_request('fake_endpoint', api_state_fixture)
    
#     logger.error(f"Testing make_request_error with data: {data}")
#     assert data == []

# def test_store_full_bill_text(app, session, politician_factory, bill_factory, bill_full_text_factory):
#     with app.app_context():
#         politician = politician_factory()
#         session.add(politician)
#         session.commit()

#         bill = bill_factory()
#         session.add(bill)
#         session.commit()
        
#         bill_full_text = bill_full_text_factory()
#         session.add(bill_full_text)
#         session.commit()

#         saved_bill_full_text = BillFullText.query.filter_by(bill_id=bill.id).first()
#         logger.info(f"Testing store_full_bill_text with saved_bill_full_text: {saved_bill_full_text}")
#         assert saved_bill_full_text is not None
#         assert saved_bill_full_text.title == 'XML Title'
#         assert saved_bill_full_text.bill_metadata == bill_full_text.bill_metadata

# @patch('requests.get')
# def test_fetch_individual_text_version(mock_get):
#     xml_content = """
#     <root>
#         <metadata>
#             <dublinCore>
#                 <dc:title xmlns:dc="http://purl.org/dc/elements/1.1/">XML Title</dc:title>
#                 <dc:publisher xmlns:dc="http://purl.org/dc/elements/1.1/">XML Publisher</dc:publisher>
#                 <dc:date xmlns:dc="http://purl.org/dc/elements/1.1/">2023-01-03</dc:date>
#                 <dc:format xmlns:dc="http://purl.org/dc/elements/1.1/">XML Format</dc:format>
#                 <dc:language xmlns:dc="http://purl.org/dc/elements/1.1/">XML Language</dc:language>
#                 <dc:rights xmlns:dc="http://purl.org/dc/elements/1.1/">XML Rights</dc:rights>
#             </dublinCore>
#         </metadata>
#     </root>
#     """

#     mock_get.return_value.status_code = 200
#     mock_get.return_value.content = xml_content.encode('utf-8')

#     xml_url = 'http://test.com/xml'
#     parsed_data = fetch_individual_text_version(xml_url)

#     logger.info(f"Testing fetch_individual_text_version with parsed_data: {parsed_data}")
#     assert parsed_data == {
#         'title': 'XML Title',
#         'publisher': 'XML Publisher',
#         'date': '2023-01-03',
#         'format': 'XML Format',
#         'language': 'XML Language',
#         'rights': 'XML Rights'
#     }

# if __name__ == "__main__":
#     pytest.main()