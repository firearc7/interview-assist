import unittest
from unittest.mock import patch, MagicMock
import os
import requests

# To test a script, we often import it and run its main execution block,
# or refactor the script into functions.
# For mistral_test.py, we'll assume its code is run when imported or via a main function.
# Let's assume we can call a main-like function from it.
# If mistral_test.py executes directly on import, this is harder.
# For this example, let's assume mistral_test.py has its logic in a function or can be exec'd.

# A common pattern for testing scripts:
# 1. Ensure the script doesn't run automatically on import (e.g. use `if __name__ == "__main__":`)
# 2. Import functions from the script or use `runpy.run_module`.

# For simplicity, we'll mock at the level of `requests.post` and `os.getenv`
# and assume we can trigger the script's logic.
# We'll simulate running the script by importing it and having its main logic in a function,
# or by directly patching and then importing (if it runs on import).

# Let's assume mistral_test.py is refactored to have a main function:
# e.g., in mistral_test.py:
# def run_test():
#    # ... script logic ...
# if __name__ == "__main__":
#    run_test()

# If not, we can use runpy
import runpy

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

        # Execute the script's content. This is the tricky part.
        # Using runpy is a clean way if the script is self-contained.
        # The path should be relative to where tests are run or absolute.
        script_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'mistral_test.py')
        
        # runpy.run_path executes the script in a new module namespace
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

        script_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'mistral_test.py')
        runpy.run_path(script_path)

        mock_print.assert_any_call("Request failed:")
        mock_print.assert_any_call(unittest.mock.ANY) # Check for the error message

    @patch('os.getenv', return_value=None) # No API key
    @patch('builtins.print')
    def test_script_no_api_key(self, mock_print, mock_os_getenv):
        script_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'mistral_test.py')
        with self.assertRaises(ValueError) as context:
            runpy.run_path(script_path)
        self.assertIn("MISTRAL_API_KEY environment variable not set", str(context.exception))

if __name__ == '__main__':
    unittest.main()
