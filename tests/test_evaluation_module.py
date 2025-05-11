import unittest
from unittest.mock import patch
import json
from src import evaluation_module

class TestEvaluationModule(unittest.TestCase):

    def test_parse_feedback_from_text(self):
        valid_json_text = '{"score": 8, "strengths": "Clear", "areas_for_improvement": "More detail", "sample_answer": "A good answer."}'
        expected_dict = {"score": 8, "strengths": "Clear", "areas_for_improvement": "More detail", "sample_answer": "A good answer."}
        self.assertEqual(evaluation_module.parse_feedback_from_text(valid_json_text), expected_dict)

        invalid_json_text = 'This is not JSON'
        self.assertIsNone(evaluation_module.parse_feedback_from_text(invalid_json_text))

        empty_text = ""
        self.assertIsNone(evaluation_module.parse_feedback_from_text(empty_text))
        
        none_text = None
        self.assertIsNone(evaluation_module.parse_feedback_from_text(none_text))

    @patch('src.evaluation_module.generate_text')
    def test_evaluate_response_success(self, mock_generate_text):
        feedback_json = {"score": 9, "strengths": "Excellent", "areas_for_improvement": "None", "sample_answer": "Perfect."}
        mock_generate_text.return_value = json.dumps(feedback_json)
        
        config = {"job_role": "Engineer", "difficulty": "Hard"}
        question = "What is your biggest achievement?"
        response = "My biggest achievement is X."
        
        evaluation = evaluation_module.evaluate_response(question, response, config)
        self.assertEqual(evaluation, feedback_json)
        mock_generate_text.assert_called_once()

    @patch('src.evaluation_module.generate_text')
    def test_evaluate_response_api_failure(self, mock_generate_text):
        mock_generate_text.return_value = None # Simulate API failure
        config = {"job_role": "Manager"}
        question = "Q1"
        response = "R1"
        
        evaluation = evaluation_module.evaluate_response(question, response, config)
        self.assertEqual(evaluation["score"], "N/A (GenAI call failed)")
        self.assertIn("Failed to get feedback", evaluation["strengths"])

    @patch('src.evaluation_module.generate_text')
    def test_evaluate_response_parsing_failure(self, mock_generate_text):
        mock_generate_text.return_value = "Invalid JSON output" # Simulate parsing failure
        config = {"job_role": "Analyst"}
        question = "Q2"
        response = "R2"

        evaluation = evaluation_module.evaluate_response(question, response, config)
        self.assertEqual(evaluation["score"], "N/A (GenAI parsing error)")
        self.assertIn("Could not parse GenAI feedback", evaluation["strengths"])

    @patch('src.evaluation_module.generate_text')
    def test_generate_overall_performance_success(self, mock_generate_text):
        overall_analysis_json = {
            "overall_analysis": "Good performance.",
            "key_strengths": ["Clarity"],
            "improvement_areas": ["Depth"],
            "preparation_tips": ["Practice more."]
        }
        mock_generate_text.return_value = json.dumps(overall_analysis_json)
        
        questions = ["Q1"]
        responses = ["R1"]
        feedback_list = [{"score": 7, "strengths": "S1", "areas_for_improvement": "A1"}]
        config = {"job_role": "Lead", "difficulty": "Medium"}
        
        overall_perf = evaluation_module.generate_overall_performance(questions, responses, feedback_list, config)
        
        self.assertEqual(overall_perf["overall_analysis"], "Good performance.")
        self.assertEqual(overall_perf["average_score"], 7.0)
        mock_generate_text.assert_called_once()

    @patch('src.evaluation_module.generate_text')
    def test_generate_overall_performance_api_failure(self, mock_generate_text):
        mock_generate_text.return_value = None
        overall_perf = evaluation_module.generate_overall_performance([], [], [], {})
        self.assertEqual(overall_perf["overall_analysis"], "Failed to generate overall analysis.")
        self.assertEqual(overall_perf["average_score"], 0)

    @patch('src.evaluation_module.generate_text')
    def test_generate_overall_performance_parsing_failure(self, mock_generate_text):
        mock_generate_text.return_value = "Not a JSON"
        overall_perf = evaluation_module.generate_overall_performance([], [], [], {})
        self.assertEqual(overall_perf["overall_analysis"], "Not a JSON")
        self.assertIn("Error parsing analysis output.", overall_perf["key_strengths"]) # Corrected string
        self.assertEqual(overall_perf["average_score"], 0)
        
    def test_generate_overall_performance_empty_inputs(self):
        with patch('src.evaluation_module.generate_text') as mock_gen_text:
            mock_gen_text.return_value = json.dumps({
                "overall_analysis": "Default", 
                "key_strengths": [], 
                "improvement_areas": [], 
                "preparation_tips": []
            })
            overall_perf = evaluation_module.generate_overall_performance([], [], [], {})
            self.assertEqual(overall_perf["average_score"], 0)
            self.assertEqual(overall_perf["overall_analysis"], "Default")

if __name__ == '__main__':
    unittest.main()
