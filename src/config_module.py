"""
Handles interview configuration input from the user.
"""

def get_interview_configuration():
    """
    Prompts the user for interview configuration details.

    Returns:
        dict: A dictionary containing interview configuration, 
              e.g., {"job_role": "Software Engineer", "job_description": "...", "difficulty": "medium"}
    """
    print("\n--- Interview Configuration ---")
    
    job_role = input("Enter the job role you are preparing for (e.g., Software Engineer): ")
    job_description = input("Paste the job description (or a summary): ")
    difficulty = input("Enter desired difficulty (e.g., easy, medium, hard): ")
    # Add more configuration options as needed (e.g., interview type, specific skills to focus on)

    config = {
        "job_role": job_role,
        "job_description": job_description,
        "difficulty": difficulty,
    }
    
    print("Configuration received.")
    return config

if __name__ == '__main__':
    # Example usage (for testing this module directly)
    config = get_interview_configuration()
    print("\nCollected Configuration:")
    for key, value in config.items():
        print(f"- {key.replace('_', ' ').title()}: {value}")
