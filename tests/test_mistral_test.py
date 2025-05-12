import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import requests
import runpy

# Add src to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestMistralTestScript(unittest.TestCase):

    @patch('os.getenv')
    @patch('requests.post')
    @patch('builtins.print')
    def test_script_success(self, mock_print, mock_requests_post, mock_os_getenv):
        mock_os_getenv.return_value = "fake_api_key"
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'choices': [{'message': {'content': 'Mistral says hi!'}}]}
        mock_response.raise_for_status = MagicMock() # Ensure it doesn't raise
        mock_requests_post.return_value = mock_response

        # Execute using module path for consistency
        script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src', 'mistral_test.py')
        
        runpy.run_path(script_path) 

        mock_os_getenv.assert_called_once_with("MISTRAL_API_KEY")
        mock_requests_post.assert_called_once()
        args, kwargs = mock_requests_post.call_args
        self.assertEqual(kwargs['json']['model'], 'mistral-tiny')
        mock_print.assert_any_call("Response from Mistral:")
        mock_print.assert_any_call("Mistral says hi!")

    @patch('os.getenv')
    @patch('requests.post')
    @patch('builtins.print')
    def test_script_request_failure(self, mock_print, mock_requests_post, mock_os_getenv):
        mock_os_getenv.return_value = "fake_api_key"
        mock_requests_post.side_effect = requests.exceptions.RequestException("Connection error")

        script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src', 'mistral_test.py')
        runpy.run_path(script_path)

        mock_print.assert_any_call("Request failed:")
        mock_print.assert_any_call(unittest.mock.ANY) # Check for the error message

    @patch('os.getenv', return_value=None) # No API key
    @patch('builtins.print')
    def test_script_no_api_key(self, mock_print, mock_os_getenv):
        script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src', 'mistral_test.py')
        with self.assertRaises(ValueError) as context:
            runpy.run_path(script_path)
        self.assertIn("MISTRAL_API_KEY environment variable not set", str(context.exception))

if __name__ == '__main__':
    unittest.main()
