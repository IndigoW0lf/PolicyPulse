import pytest
from unittest.mock import patch
from policyapp.utils.congress_api import ApiState, make_request, manage_api_state

@pytest.fixture
def api_state_fixture():
    return ApiState()

# Test for manage_api_state
def test_manage_api_state(api_state_fixture):
    api_state_fixture.batch_counter = 49
    commit_needed = manage_api_state(api_state_fixture, 50)
    assert commit_needed == True
    assert api_state_fixture.batch_counter == 0

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