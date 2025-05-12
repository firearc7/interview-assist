"""
Module for evaluating interview responses.
"""
import json
import os
import sys

# Fix imports to work whether the file is imported as a module or run directly
try:
    # Try relative import (when imported as part of package)
    from .genai_client import generate_text
except ImportError:
    # Fallback to direct import (when run as script)
    import genai_client
    generate_text = genai_client.generate_text
    # If that fails, try to import from the same directory
    if 'genai_client' not in sys.modules:
        # Add the parent directory to sys.path if needed
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        # Try again with direct import
        import genai_client
        generate_text = genai_client.generate_text

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

def generate_overall_performance(questions, responses, feedback, interview_config):
    """
    Generate overall performance analysis and suggestions based on all responses.
    
    Args:
        questions (list): List of all interview questions.
        responses (list): List of user responses to the questions.
        feedback (list): List of feedback for each question.
        interview_config (dict): Interview configuration.
        
    Returns:
        dict: A dictionary containing overall analysis, score and suggestions.
    """
    print("\n--- Generating Overall Performance Analysis ---")
    
    # Extract scores from feedback
    scores = []
    strengths_list = []
    areas_for_improvement_list = []
    
    for fb in feedback:
        if fb:
            try:
                score = float(fb.get('score', 0))
                scores.append(score)
            except (ValueError, TypeError):
                pass
                
            strengths = fb.get('strengths', '')
            if strengths and strengths != 'N/A' and not strengths.startswith('Failed'):
                strengths_list.append(strengths)
                
            areas = fb.get('areas_for_improvement', '')
            if areas and areas != 'N/A' and not areas.startswith('Failed'):
                areas_for_improvement_list.append(areas)
    
    # Create a summary of the interview for context
    avg_score = sum(scores) / len(scores) if scores else 0
    
    # Prepare for GenAI call
    prompt_system = (
        "You are an expert interview coach providing an overall assessment of a candidate's "
        "interview performance. Review all their responses and previous feedback to provide "
        "a comprehensive analysis of their strengths and weaknesses. Focus on patterns across "
        "answers, communication style, and expertise demonstrated. Provide specific, actionable "
        "advice for improvement. Format your response as JSON with these keys: "
        "'overall_analysis' (general performance assessment), 'key_strengths' (list of main strengths), "
        "'improvement_areas' (list of areas to work on), and 'preparation_tips' (specific tips for their next interview)."
    )
    
    prompt_user = (
        f"Job Role: {interview_config.get('job_role')}\n"
        f"Interview Difficulty: {interview_config.get('difficulty')}\n"
        f"Average Score: {avg_score:.1f}/10\n\n"
        "Interview Questions and Responses:\n"
    )
    
    # Add questions, responses, and feedback summaries to the prompt
    for i, (q, r) in enumerate(zip(questions, responses)):
        if r:  # Only include questions that were answered
            fb_summary = ""
            if i < len(feedback) and feedback[i]:
                fb = feedback[i]
                fb_summary = f"[Score: {fb.get('score', 'N/A')}/10, Strengths: {fb.get('strengths', 'N/A')}, Areas for improvement: {fb.get('areas_for_improvement', 'N/A')}]"
            
            prompt_user += f"Q{i+1}: {q}\nResponse: {r}\nFeedback: {fb_summary}\n\n"
    
    prompt_user += "Please provide an overall performance analysis in the specified JSON format."
    
    prompt_messages = [
        {"role": "system", "content": prompt_system},
        {"role": "user", "content": prompt_user}
    ]
    
    generated_text = generate_text(prompt_messages)
    
    try:
        # Try to parse as JSON
        if generated_text:
            overall_analysis = json.loads(generated_text)
            # Ensure all expected keys are present
            overall_analysis.setdefault("overall_analysis", "Analysis could not be generated.")
            overall_analysis.setdefault("key_strengths", ["Could not identify strengths."])
            overall_analysis.setdefault("improvement_areas", ["Could not identify improvement areas."])
            overall_analysis.setdefault("preparation_tips", ["Could not generate preparation tips."])
        else:
            overall_analysis = {
                "overall_analysis": "Failed to generate overall analysis.",
                "key_strengths": ["Failed to generate key strengths."],
                "improvement_areas": ["Failed to generate improvement areas."],
                "preparation_tips": ["Failed to generate preparation tips."]
            }
    except json.JSONDecodeError:
        # If it's not valid JSON, create a dict with the raw text and placeholders
        overall_analysis = {
            "overall_analysis": generated_text if generated_text else "Failed to generate analysis.",
            "key_strengths": ["Error parsing analysis output."],
            "improvement_areas": ["Error parsing analysis output."],
            "preparation_tips": ["Error parsing analysis output."]
        }
    
    # Add numerical average score
    overall_analysis["average_score"] = avg_score
    
    return overall_analysis

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
