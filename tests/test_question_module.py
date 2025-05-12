import unittest
from unittest.mock import patch
import sys
import os

# Add src to sys.path to allow direct import of src modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src import question_module

class TestQuestionModule(unittest.TestCase):

    def test_parse_questions_from_text(self):
        text_response_1 = "1. Question one?\n2. Question two?\n3. Question three."
        expected_1 = ["Question one?", "Question two?", "Question three."]
        self.assertEqual(question_module.parse_questions_from_text(text_response_1), expected_1)

        text_response_2 = "Question one without number.\nAnother question."
        expected_2 = ["Question one without number.", "Another question."]
        self.assertEqual(question_module.parse_questions_from_text(text_response_2), expected_2)

        text_response_3 = "1) Q1\n2) Q2"
        expected_3 = ["Q1", "Q2"]
        self.assertEqual(question_module.parse_questions_from_text(text_response_3), expected_3)
        
        text_response_empty = ""
        self.assertEqual(question_module.parse_questions_from_text(text_response_empty), [])

        text_response_none = None
        self.assertEqual(question_module.parse_questions_from_text(text_response_none), [])

        text_response_single_line = "Just one question here."
        self.assertEqual(question_module.parse_questions_from_text(text_response_single_line), ["Just one question here."])

        text_response_with_empty_lines = "\n1. Q1\n\n2. Q2\n"
        expected_empty_lines = ["Q1", "Q2"]
        self.assertEqual(question_module.parse_questions_from_text(text_response_with_empty_lines), expected_empty_lines)

    @patch('src.question_module.generate_text')  # Updated patch path
    def test_generate_questions_success(self, mock_generate_text):
        mock_generate_text.return_value = "1. Mocked Question 1?\n2. Mocked Question 2?"
        config = {"job_role": "Tester", "difficulty": "Easy", "job_description": "Test software."}
        questions = question_module.generate_questions(config, num_questions=2)
        self.assertEqual(len(questions), 2)
        self.assertEqual(questions[0], "Mocked Question 1?")
        mock_generate_text.assert_called_once()

    @patch('src.question_module.generate_text')  # Updated patch path
    def test_generate_questions_api_failure_fallback(self, mock_generate_text):
        mock_generate_text.return_value = None # Simulate API failure
        config = {"job_role": "Software Engineer", "difficulty": "Medium", "job_description": "Dev"}
        questions = question_module.generate_questions(config, num_questions=3)
        self.assertEqual(len(questions), 3)
        # Check if it's using fallback questions
        self.assertIn("Tell me about a challenging project you worked on.", questions)

    @patch('src.question_module.generate_text')  # Updated patch path
    def test_generate_questions_parsing_failure_fallback(self, mock_generate_text):
        # To truly test parsing failure leading to fallback, parse_questions_from_text should return []
        # Let's mock parse_questions_from_text for this specific scenario
        mock_generate_text.return_value = "Some text that genai might return" 
        
        with patch('src.question_module.parse_questions_from_text', return_value=[]) as mock_parse:
            config = {"job_role": "Analyst", "difficulty": "Hard", "job_description": "Analyze data."}
            questions = question_module.generate_questions(config, num_questions=2)
            
            mock_parse.assert_called_once_with("Some text that genai might return")
            self.assertEqual(len(questions), 2)
            # Check if it's using fallback questions
            self.assertIn(f"What interests you about the {config.get('job_role')} role?", questions)

    @patch('src.question_module.generate_text')  # Updated patch path
    def test_generate_questions_num_questions_respected(self, mock_generate_text):
        mock_generate_text.return_value = "1. Q1\n2. Q2\n3. Q3\n4. Q4\n5. Q5"
        config = {"job_role": "Developer", "difficulty": "Medium", "job_description": "Code."}
        
        questions = question_module.generate_questions(config, num_questions=3)
        self.assertEqual(len(questions), 3)
        self.assertEqual(questions, ["Q1", "Q2", "Q3"])

        # Test fallback with num_questions
        mock_generate_text.return_value = None
        questions_fallback = question_module.generate_questions(config, num_questions=2)
        self.assertEqual(len(questions_fallback), 2)


if __name__ == '__main__':
    unittest.main()
