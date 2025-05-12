"""
Command-line interface for the interview simulator.
"""
import sys
import os

# Fix imports to work whether the file is imported as a module or run directly
try:
    # When imported as part of the src package
    from . import config_module
    from . import question_module
    from . import evaluation_module
except ImportError:
    # When run as a script or imported directly
    # Add current directory to sys.path if not already there
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    # Direct imports
    import config_module
    import question_module
    import evaluation_module

def start_interview():
    """
    Manages the overall flow of the interview session.
    """
    print("Welcome to the AI Interview Simulator (Terminal Edition)!")

    # 1. Get Interview Configuration
    interview_config = config_module.get_interview_configuration()

    # 2. Generate Questions
    # You might want to ask the user how many questions they want
    num_questions_to_ask = int(input("How many questions would you like to answer? (default is 5): ") or 5)
    questions = question_module.generate_questions(interview_config, num_questions=num_questions_to_ask)

    if not questions:
        print("No questions were generated. Exiting.")
        return

    print(f"\n--- Starting Interview ({len(questions)} questions) ---")

    # 3. Conduct Interview Loop
    for i, question_text in enumerate(questions):
        print(f"\nQuestion {i+1}/{len(questions)}: {question_text}")
        user_response = input("Your answer: ")

        # 4. Evaluate Response
        feedback = evaluation_module.evaluate_response(question_text, user_response, interview_config)
        
        print("\n--- Feedback ---")
        print(f"Score: {feedback.get('score', 'N/A')}")
        print(f"Strengths: {feedback.get('strengths', 'N/A')}")
        print(f"Areas for Improvement: {feedback.get('areas_for_improvement', 'N/A')}")
        print(f"Sample Answer Hint: {feedback.get('sample_answer', 'N/A')}")
        
        if i < len(questions) - 1:
            input("\nPress Enter to continue to the next question...")

    print("\n--- Interview Finished ---")
    print("Thank you for using the AI Interview Simulator!")

if __name__ == '__main__':
    start_interview()
