import unittest
from unittest.mock import patch, call
from src import interview_flow # Assuming interview_flow.py is in src

class TestInterviewFlow(unittest.TestCase):

    @patch('builtins.input')
    @patch('src.interview_flow.config_module.get_interview_configuration')
    @patch('src.interview_flow.question_module.generate_questions')
    @patch('src.interview_flow.evaluation_module.evaluate_response')
    @patch('builtins.print') # To suppress print statements or check them
    def test_start_interview_normal_flow(self, mock_print, mock_evaluate, mock_generate_questions, mock_get_config, mock_input):
        # Setup mocks
        # Num questions, Answer 1, Enter, Answer 2 (no Enter after last question)
        mock_input.side_effect = ["2", "My Answer 1", "", "My Answer 2"] 
        mock_get_config.return_value = {"job_role": "Test Role", "difficulty": "Easy"}
        mock_generate_questions.return_value = ["Question 1?", "Question 2?"]
        mock_evaluate.side_effect = [
            {"score": 8, "strengths": "S1", "areas_for_improvement": "A1", "sample_answer": "SA1"},
            {"score": 7, "strengths": "S2", "areas_for_improvement": "A2", "sample_answer": "SA2"}
        ]

        interview_flow.start_interview()

        # Assertions
        mock_get_config.assert_called_once()
        mock_input.assert_any_call("How many questions would you like to answer? (default is 5): ")
        mock_generate_questions.assert_called_once_with({"job_role": "Test Role", "difficulty": "Easy"}, num_questions=2)
        
        self.assertEqual(mock_evaluate.call_count, 2)
        mock_evaluate.assert_any_call("Question 1?", "My Answer 1", {"job_role": "Test Role", "difficulty": "Easy"})
        mock_evaluate.assert_any_call("Question 2?", "My Answer 2", {"job_role": "Test Role", "difficulty": "Easy"})

        # Check if feedback is printed (simplified check for print calls)
        self.assertGreater(mock_print.call_count, 5) # Welcome, starting, Qs, feedback, finished

    @patch('builtins.input', return_value="1") # Num questions
    @patch('src.interview_flow.config_module.get_interview_configuration')
    @patch('src.interview_flow.question_module.generate_questions', return_value=[]) # No questions
    @patch('src.interview_flow.evaluation_module.evaluate_response') # Should not be called
    @patch('builtins.print')
    def test_start_interview_no_questions_generated(self, mock_print, mock_evaluate, mock_generate_questions, mock_get_config, mock_input):
        mock_get_config.return_value = {"job_role": "Test Role", "difficulty": "Easy"}

        interview_flow.start_interview()

        mock_get_config.assert_called_once()
        mock_generate_questions.assert_called_once()
        mock_evaluate.assert_not_called() # Crucial: evaluation should not happen
        
        # Check for "No questions were generated. Exiting." message
        mock_print.assert_any_call("No questions were generated. Exiting.")

if __name__ == '__main__':
    unittest.main()
