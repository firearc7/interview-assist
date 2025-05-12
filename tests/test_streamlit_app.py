import unittest
from unittest.mock import patch, MagicMock, call
import sys
import os
from datetime import datetime
import json

# Add src to sys.path to allow direct import of streamlit_app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Create a more sophisticated Session State class for mocking
class SessionState(dict):
    """Mock for streamlit's session_state that supports both dict and attribute access"""
    def __getattr__(self, name):
        if name in self:
            return self[name]
        return None
    
    def __setattr__(self, name, value):
        self[name] = value

# Create a comprehensive mock for Streamlit
class MockStreamlit:
    def __init__(self):
        self.session_state = SessionState()
        self.query_params = MagicMock()
        self.query_params.get = MagicMock(return_value=None)
        self.query_params.update = MagicMock()
        
        # Set up common methods used in the app
        self.title = MagicMock()
        self.header = MagicMock()
        self.subheader = MagicMock()
        self.markdown = MagicMock()
        self.write = MagicMock()
        self.info = MagicMock()
        self.success = MagicMock()
        self.error = MagicMock()
        self.warning = MagicMock()
        self.progress = MagicMock()
        self.spinner = MagicMock(return_value=MagicMock(__enter__=MagicMock(), __exit__=MagicMock()))
        self.rerun = MagicMock()
        self.stop = MagicMock()
        self.divider = MagicMock()
        self.expander = MagicMock(return_value=MagicMock(__enter__=MagicMock(), __exit__=MagicMock()))
        self.set_page_config = MagicMock()
        
        # Mock form and form elements
        self.form = MagicMock(return_value=MagicMock(__enter__=MagicMock(), __exit__=MagicMock()))
        self.form_submit_button = MagicMock()
        
        # For text inputs, always return empty string as default to prevent StopIteration
        self.text_input = MagicMock(return_value="")
        self.text_area = MagicMock(return_value="")
        
        self.select_slider = MagicMock()
        self.slider = MagicMock()
        self.button = MagicMock(return_value=False)  # Default to False for buttons
        
        # Create columns that return the right number based on the input
        def _columns_mock(*args, **kwargs):
            # If a number is passed, return that many column mocks
            if args and isinstance(args[0], int):
                return [MagicMock() for _ in range(args[0])]
            # If a list is passed, return that many column mocks
            elif args and isinstance(args[0], list):
                return [MagicMock() for _ in range(len(args[0]))]
            # Default case
            return [MagicMock()]
        
        self.columns = MagicMock(side_effect=_columns_mock)
    
    # Additional method to reset all mocks for a clean test state
    def reset_all(self):
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if isinstance(attr, MagicMock) and attr_name != "session_state":
                attr.reset_mock()
        
        # Keep session_state dictionary but clear its contents
        self.session_state.clear()
        
        # Reset query_params specially
        self.query_params.get.reset_mock()
        self.query_params.update.reset_mock()
        self.query_params.get.return_value = None

# Create a global mock instance
mock_st = MockStreamlit()

# Patch streamlit for tests
@patch.dict(sys.modules, {'streamlit': mock_st})
class TestStreamlitApp(unittest.TestCase):

    def setUp(self):
        # Reset all mocks before each test
        mock_st.reset_all()
        
        # Initialize common session state values
        mock_st.session_state["page"] = "welcome"
        mock_st.session_state["user"] = None
        mock_st.session_state["interview_config"] = None
        mock_st.session_state["questions"] = []
        mock_st.session_state["current_question_idx"] = 0
        mock_st.session_state["responses"] = []
        mock_st.session_state["feedback"] = []
        mock_st.session_state["overall_analysis"] = None
        
        # Import the streamlit_app module from src package
        from src import streamlit_app
        self.streamlit_app = streamlit_app
        
        # Patch st in the already imported module
        patcher = patch.object(streamlit_app, 'st', mock_st)
        patcher.start()
        self.addCleanup(patcher.stop)
                
    def tearDown(self):
        # All patchers added with addCleanup will be automatically stopped
        pass

    @patch('src.streamlit_app.display_welcome_page')
    def test_main_routing_welcome(self, mock_display_welcome):
        mock_st.session_state["page"] = "welcome"
        self.streamlit_app.main()  # Use the saved module reference
        mock_display_welcome.assert_called_once()

    @patch('src.streamlit_app.display_login_page')
    def test_main_routing_login(self, mock_display_login):
        mock_st.session_state["page"] = "login"
        self.streamlit_app.main()  # Use the saved module reference
        mock_display_login.assert_called_once()
    
    # Test initial session state setup in main()
    def test_main_initialization(self):
        # Clear session state to test initialization
        mock_st.session_state.clear()
        
        # Mock main functions to prevent execution
        with patch('src.streamlit_app.display_welcome_page'):
            self.streamlit_app.main()  # Use the saved module reference
            
        # Test only the initialization part
        self.assertEqual(mock_st.session_state["page"], "welcome")
        self.assertIsNone(mock_st.session_state["interview_config"])
        self.assertEqual(mock_st.session_state["questions"], [])

    # --- Test display_navbar ---
    def test_display_navbar_dashboard_button(self):
        mock_st.session_state["user"] = {"username": "testuser"}
        # Set up a specific side effect for this test
        mock_st.button.side_effect = lambda label, key=None, **kwargs: key == "nav_dashboard"

        self.streamlit_app.display_navbar()  # Use the saved module reference
        
        mock_st.button.assert_any_call("🏠 Dashboard", key="nav_dashboard")

    def test_display_navbar_logout_button(self):
        mock_st.session_state["user"] = {"username": "testuser"}
        # Set up a specific side effect for this test only
        mock_st.button.side_effect = lambda label, key=None, **kwargs: key == "nav_logout"

        self.streamlit_app.display_navbar()  # Use the saved module reference
        
        mock_st.button.assert_any_call("🚪 Logout", key="nav_logout")

    # --- Test display_welcome_page ---
    def test_display_welcome_page_logged_in(self):
        mock_st.session_state["user"] = {"username": "testuser"}
        mock_go_to_setup = MagicMock()
        mock_go_to_dashboard = MagicMock()
        
        # Set up button behavior for this test
        def button_side_effect(label, on_click=None, **kwargs):
            if label == "Start Interview Preparation" and on_click:
                on_click()
                return True
            return False
            
        mock_st.button.side_effect = button_side_effect

        self.streamlit_app.display_welcome_page(mock_go_to_setup, MagicMock(), MagicMock(), mock_go_to_dashboard)
        
        mock_st.button.assert_any_call("Start Interview Preparation", on_click=mock_go_to_setup, use_container_width=True)
        mock_st.button.assert_any_call("View Interview History", on_click=mock_go_to_dashboard, use_container_width=True)
        mock_go_to_setup.assert_called_once()

    def test_display_welcome_page_logged_out(self):
        mock_st.session_state["user"] = None
        mock_go_to_login = MagicMock()
        mock_go_to_signup = MagicMock()
        
        # Reset button behavior
        mock_st.button.side_effect = None
        mock_st.button.return_value = False

        self.streamlit_app.display_welcome_page(MagicMock(), mock_go_to_login, mock_go_to_signup, MagicMock())
        
        mock_st.button.assert_any_call("Login", on_click=mock_go_to_login, use_container_width=True)
        mock_st.button.assert_any_call("Sign Up", on_click=mock_go_to_signup, use_container_width=True)

    # --- Test display_login_page ---
    @patch('src.streamlit_app.database.validate_user')
    def test_display_login_page_success(self, mock_validate_user):
        # Set up the form submit button to succeed
        mock_st.form_submit_button.return_value = True
        
        # Set up text input responses
        mock_st.text_input.side_effect = ["testuser", "password"]
        
        # Mock user validation
        mock_validate_user.return_value = {"id": 1, "username": "testuser"}
        mock_go_to_dashboard = MagicMock()

        self.streamlit_app.display_login_page(mock_go_to_dashboard)

        mock_validate_user.assert_called_with("testuser", "password")
        self.assertEqual(mock_st.session_state["user"], {"id": 1, "username": "testuser"})
        mock_go_to_dashboard.assert_called_once()
        
        # Allow for multiple rerun calls - just check it was called at least once
        mock_st.rerun.assert_called()
        mock_st.success.assert_called_once_with("Login successful!")

    @patch('src.streamlit_app.database.validate_user')
    def test_display_login_page_failure(self, mock_validate_user):
        # Set up the form submit button to succeed
        mock_st.form_submit_button.return_value = True
        
        # Reset text_input to prevent StopIteration
        mock_st.text_input.side_effect = None
        mock_st.text_input.side_effect = ["wronguser", "wrongpass"]
        
        # Mock failed validation
        mock_validate_user.return_value = None
        mock_go_to_dashboard = MagicMock()

        self.streamlit_app.display_login_page(mock_go_to_dashboard)
        
        mock_st.error.assert_called_once_with("Invalid username or password")
        mock_go_to_dashboard.assert_not_called()

    def test_display_login_page_signup_button(self):
        # Reset side effects
        mock_st.form_submit_button.return_value = False
        
        # Important: Reset the text_input side_effect
        mock_st.text_input.side_effect = None
        mock_st.text_input.return_value = "test_value"  # Default return value for any input
        
        # Reset button side effect and set up a new one for this test
        mock_st.button.side_effect = None  
        mock_st.button.side_effect = lambda label, **kwargs: label == "Sign Up"

        self.streamlit_app.display_login_page(MagicMock())
        
        self.assertEqual(mock_st.session_state["page"], "signup")
        mock_st.rerun.assert_called()

    # Add similar patterns for the remaining tests...
    # For each test, make sure to:
    # 1. Reset mocks/side_effects that might affect other tests
    # 2. Use specific side_effects for the test case
    # 3. Use proper assertions that match the expected behavior

    # For columns unpacking issues, our improved mock now returns the right number of columns

    # --- Test display_setup_page ---
    @patch('src.streamlit_app.question_module.generate_questions')
    def test_display_setup_page_generate_questions_success(self, mock_generate_questions):
        # Set up form submission
        mock_st.form_submit_button.return_value = True
        
        # IMPORTANT: Remove side_effect for text_input and text_area
        # to prevent StopIteration errors
        mock_st.text_input.side_effect = None
        mock_st.text_input.return_value = "Job Role"
        
        mock_st.text_area.side_effect = None
        mock_st.text_area.return_value = "Job Description"
        
        mock_st.select_slider.return_value = "Medium"
        mock_st.slider.return_value = 3
        
        # Generate questions result
        mock_generate_questions.return_value = ["Q1", "Q2", "Q3"]
        
        # Test callback
        mock_go_to_interview = MagicMock()
        
        # For the button after questions are generated
        mock_st.button.side_effect = None
        mock_st.button.return_value = True

        self.streamlit_app.display_setup_page(mock_go_to_interview)

        # Check expected behavior
        self.assertEqual(mock_st.session_state["interview_config"]["job_role"], "Job Role")
        mock_generate_questions.assert_called_once()
        self.assertEqual(len(mock_st.session_state["questions"]), 3)
        mock_st.success.assert_called_once()
