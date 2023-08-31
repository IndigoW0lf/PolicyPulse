import unittest
from unittest.mock import patch
from policyapp.utils.congress_api import ApiState, make_request, manage_api_state

class TestCongressApi(unittest.TestCase):

    def setUp(self):
        self.api_state = ApiState()

    def test_manage_api_state(self):
        # Test if manage_api_state resets batch_counter and returns True
        self.api_state.batch_counter = 49
        commit_needed = manage_api_state(self.api_state, 50)
        self.assertEqual(commit_needed, True)
        self.assertEqual(self.api_state.batch_counter, 0)

    @patch('requests.get')
    def test_make_request(self, mock_get):
        # Mocking the API response
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {'results': [1, 2, 3]}

        # Test if make_request returns correct data
        data = make_request('fake_endpoint', api_state=self.api_state)
        self.assertEqual(data, [1, 2, 3])

    @patch('requests.get')
    def test_make_request_error(self, mock_get):
        # Mocking the API response for an error
        mock_get.return_value.status_code = 400

        # Test if make_request returns an empty list on error
        data = make_request('fake_endpoint', api_state=self.api_state)
        self.assertEqual(data, [])

if __name__ == '__main__':
    unittest.main()
