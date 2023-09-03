import pytest
import os
from unittest.mock import patch
from policyapp.utils.congress_api import ApiState, make_request, manage_api_state
from policyapp import create_app, db
from flask import current_app

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

def test_manage_api_state(app, api_state_fixture):  # Pass the 'app' fixture as an argument
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
    data = make_request('fake_endpoint', api_state=api_state_fixture)
    assert data == [1, 2, 3]

# Test for make_request with unsuccessful API call
@patch('requests.get')
def test_make_request_error(mock_get, api_state_fixture):
    mock_get.return_value.status_code = 400
    data = make_request('fake_endpoint', api_state=api_state_fixture)
    assert data == []