"""
Generates interview questions based on configuration using GenAI.
"""
import genai_client # Import the new client

def parse_questions_from_text(text_response):
    """
    Parses a block of text from LLM into a list of questions.
    Assumes questions are separated by newlines.
    """
    if not text_response:
        return []
    # Simple split by newline, removing empty lines and stripping whitespace
    questions = [q.strip() for q in text_response.split('\n') if q.strip()]
    # Further refinement might be needed based on LLM output format
    # e.g., removing numbering like "1. Question text"
    cleaned_questions = []
    for q in questions:
        if q.startswith(tuple(f"{i}." for i in range(1, 10))): # "1.", "2." etc.
            cleaned_questions.append(q.split('.', 1)[1].strip())
        elif q.startswith(tuple(f"{i})" for i in range(1, 10))): # "1)", "2)" etc.
            cleaned_questions.append(q.split(')', 1)[1].strip())
        else:
            cleaned_questions.append(q)
    return cleaned_questions


def generate_questions(config, num_questions=5):
    """
    Generates interview questions using a GenAI model.

    Args:
        config (dict): Interview configuration from config_module.
        num_questions (int): Number of questions to generate.

    Returns:
        list: A list of generated interview questions (strings).
    """
    print(f"\n--- Generating {num_questions} Questions (Mistral AI) ---")
    print(f"Configuration: Role - {config.get('job_role')}, Difficulty - {config.get('difficulty')}")
    
    questions = []
    
    # --- GenAI Integration using Mistral ---
    prompt_content = (
        f"You are an expert interviewer. Generate {num_questions} interview questions "
        f"for a candidate applying for the role of '{config.get('job_role')}'. "
        f"The desired difficulty level is '{config.get('difficulty')}'. "
        f"The job description is: '{config.get('job_description', 'Not provided')}'. "
        f"Focus on questions relevant to this role and difficulty. "
        f"Ensure each question is distinct and on a new line, without any introductory or concluding text, just the questions."
    )
    
    messages = [{"role": "user", "content": prompt_content}]
    
    generated_text = genai_client.generate_text(messages)
    
    if generated_text:
        questions = parse_questions_from_text(generated_text)
        if len(questions) > num_questions:
            questions = questions[:num_questions]
        elif not questions:
            print("Warning: Mistral API returned text, but no questions could be parsed.")
    else:
        print("Error: Failed to generate questions from Mistral API.")
    # --- End GenAI Integration ---

    if not questions: # Fallback if API fails or parsing yields nothing
        print("Using fallback placeholder questions.")
        if config.get("job_role", "").lower() == "software engineer":
            questions = [
                "Tell me about a challenging project you worked on.",
                "How do you handle disagreements within your team?",
                "Explain a complex technical concept to a non-technical person.",
                "Describe your experience with [specific technology from job description, if any].",
                f"What are your strengths and weaknesses as a {config.get('job_role')}?"
            ]
        else:
             questions = [
                f"What interests you about the {config.get('job_role')} role?",
                "Describe a time you had to learn something new quickly.",
                "How do you prioritize your tasks when working on multiple projects?",
                "Where do you see yourself in 5 years?",
                "Why should we hire you for this position?"
            ]
        questions = questions[:num_questions]

    print(f"{len(questions)} questions generated.")
    return questions

if __name__ == '__main__':
    # Example usage (for testing this module directly)
    sample_config = {
        "job_role": "Software Engineer", 
        "job_description": "Develop and maintain web applications.", 
        "difficulty": "medium"
    }
    generated_questions = generate_questions(sample_config)
    print("\nGenerated Questions:")
    for i, q in enumerate(generated_questions):
        print(f"{i+1}. {q}")

    sample_config_manager = {
        "job_role": "Product Manager", 
        "job_description": "Define product strategy and roadmap.", 
        "difficulty": "hard"
    }
    generated_questions_manager = generate_questions(sample_config_manager, 3)
    print("\nGenerated Questions (Manager):")
    for i, q in enumerate(generated_questions_manager):
        print(f"{i+1}. {q}")
