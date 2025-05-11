import unittest
from unittest.mock import patch, MagicMock
import subprocess
import os

# We need to import main from the script.
# This can be tricky if it's not structured as a module.
# A common way is to import the module and call its main function.
from src import main as launcher_main # Assuming main.py is in src

class TestMainLauncher(unittest.TestCase):

    @patch('os.path.exists')
    @patch('subprocess.run')
    def test_main_streamlit_app_exists(self, mock_subprocess_run, mock_os_path_exists):
        mock_os_path_exists.return_value = True # Simulate streamlit_app.py exists
        
        launcher_main.main()

        streamlit_app_path = os.path.join(os.path.dirname(launcher_main.__file__), "streamlit_app.py")
        mock_os_path_exists.assert_called_once_with(streamlit_app_path)
        mock_subprocess_run.assert_called_once_with(["streamlit", "run", streamlit_app_path], check=True)

    @patch('os.path.exists')
    @patch('src.interview_flow.start_interview')
    def test_main_streamlit_app_does_not_exist(self, mock_start_interview, mock_os_path_exists):
        mock_os_path_exists.return_value = False  # Streamlit app doesn't exist
        
        # Mock the sys.modules to ensure interview_flow is correctly found
        interview_flow_mock = MagicMock()
        interview_flow_mock.start_interview = mock_start_interview
        
        with patch.dict('sys.modules', {'interview_flow': interview_flow_mock}):
            # Need to import main inside the patch context
            from src.main import main
            main()
        
        # Verify the expected flow
        mock_os_path_exists.assert_called()
        mock_start_interview.assert_called_once()

    @patch('os.path.exists', return_value=True)
    @patch('subprocess.run', side_effect=FileNotFoundError("Streamlit not found"))
    @patch('builtins.print')
    def test_main_streamlit_not_found(self, mock_print, mock_subprocess_run, mock_os_path_exists):
        launcher_main.main()
        mock_print.assert_any_call("Error: Streamlit is not installed or not in PATH.")

    @patch('os.path.exists', return_value=True)
    @patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, "cmd"))
    @patch('builtins.print')
    def test_main_streamlit_called_process_error(self, mock_print, mock_subprocess_run, mock_os_path_exists):
        launcher_main.main()
        mock_print.assert_any_call(unittest.mock.ANY) # Check if any error message is printed

    @patch('os.path.exists', return_value=False) # Ensure terminal path is taken
    @patch('builtins.print')
    def test_main_interview_flow_import_error(self, mock_print, mock_os_path_exists):
        # To test the ImportError for interview_flow, we make it unimportable temporarily
        # by removing it from sys.modules if it was somehow already there (unlikely for a clean test run)        # and more importantly, by patching where it's imported in main.py or ensuring it's not in path.
        # The easiest way is to patch the import mechanism for the specific module.
        # Since main.py uses a direct `import interview_flow`, we can patch `builtins.__import__`.
        
        original_import = __builtins__['__import__']
        def import_mock(name, globals=None, locals=None, fromlist=(), level=0):
            if name == 'interview_flow' or name == 'src.interview_flow':
                raise ImportError("Simulated import error for interview_flow")
            return original_import(name, globals, locals, fromlist, level)

        with patch('builtins.__import__', side_effect=import_mock):
            try:
                launcher_main.main()
            except Exception:
                # Catch any other exception that might occur due to the mock, though ideally it shouldn't
                pass
        
        mock_print.assert_any_call("Error: Could not import interview_flow module for terminal version.")
        # Reset import to original to avoid affecting other tests
        __builtins__['__import__'] = original_import


if __name__ == '__main__':
    unittest.main()
