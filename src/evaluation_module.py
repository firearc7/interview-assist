"""
Evaluates user responses and provides feedback using GenAI.
"""
import json

# Placeholder for GenAI integration
from genai_client import generate_text

def parse_feedback_from_text(text_feedback):
    """
    Parses the structured feedback text (expected JSON) from GenAI.
    """
    if not text_feedback:
        return None
    try:
        # Assuming GenAI returns a JSON string that matches our feedback structure
        return json.loads(text_feedback)
    except json.JSONDecodeError as e:
        print(f"Error parsing feedback JSON from GenAI: {e}")
        print(f"Received text: {text_feedback}")
        return None

def evaluate_response(question, response, config):
    """
    Evaluates a user's response to an interview question using GenAI.

    Args:
        question (str): The interview question asked.
        response (str): The user's response.
        config (dict): Interview configuration.

    Returns:
        dict: A dictionary containing evaluation feedback, 
              e.g., {"score": 8, "strengths": "...", "areas_for_improvement": "...", "sample_answer": "..."}
    """
    print("\n--- Evaluating Response (GenAI) ---")
    print(f"Question: {question}")
    print(f"Your Response: {response[:100]}...") # Print a snippet

    # --- GenAI Integration ---
    prompt_system = "You are an expert interviewer providing feedback on a candidate's answer. " \
                    "Evaluate the response based on clarity, relevance, completeness, and conciseness. " \
                    "Provide specific strengths and areas for improvement. " \
                    "Suggest a concise sample answer that would be considered strong for the given role. " \
                    "Return your feedback strictly in JSON format with keys: " \
                    "'score' (integer 1-10), 'strengths' (string), 'areas_for_improvement' (string), 'sample_answer' (string)."

    prompt_user = f"Interview Question: '{question}'\n" \
                  f"Candidate's Role: {config.get('job_role', 'Not specified')}\n" \
                  f"Candidate's Response: '{response}'\n\n" \
                  f"Please provide your evaluation in the specified JSON format."

    prompt_messages = [
        {"role": "system", "content": prompt_system},
        {"role": "user", "content": prompt_user}
    ]
    
    generated_feedback_text = generate_text(prompt_messages)
    
    if generated_feedback_text:
        parsed_feedback = parse_feedback_from_text(generated_feedback_text)
        if parsed_feedback:
            feedback = parsed_feedback
            # Ensure all expected keys are present, even if GenAI missed some
            feedback.setdefault("score", "N/A (GenAI error)")
            feedback.setdefault("strengths", "N/A (GenAI error)")
            feedback.setdefault("areas_for_improvement", "N/A (GenAI error)")
            feedback.setdefault("sample_answer", "N/A (GenAI error)")
        else:
            # Parsing failed, use placeholder
            feedback = {
                "score": "N/A (GenAI parsing error)",
                "strengths": "Could not parse GenAI feedback.",
                "areas_for_improvement": "Could not parse GenAI feedback.",
                "sample_answer": "Could not parse GenAI feedback."
            }
    else:
        # GenAI call failed, use placeholder
        feedback = {
            "score": "N/A (GenAI call failed)",
            "strengths": "Failed to get feedback from GenAI.",
            "areas_for_improvement": "Failed to get feedback from GenAI.",
            "sample_answer": "Failed to get feedback from GenAI."
        }

    print("Evaluation complete.")
    return feedback

if __name__ == '__main__':
    # Example usage (for testing this module directly)
    sample_config = {
        "job_role": "Software Engineer", 
        "job_description": "Develop and maintain web applications.", 
        "difficulty": "medium"
    }
    sample_question = "Tell me about a challenging project you worked on."
    sample_response = "I worked on a project that was very challenging because of the tight deadlines and complex requirements. We managed to deliver it on time."
    
    evaluation_result = evaluate_response(sample_question, sample_response, sample_config)
    print("\nEvaluation Result:")
    for key, value in evaluation_result.items():
        print(f"- {key.replace('_', ' ').title()}: {value}")
