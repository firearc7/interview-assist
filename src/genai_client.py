"""
Client for interacting with the Mistral AI API.
"""
import os
import requests
import json

# Load the API key from environment variable
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
API_URL = "https://api.mistral.ai/v1/chat/completions"

def generate_text(prompt_messages, model="mistral-tiny"):
    """
    Generates text using the Mistral API.

    Args:
        prompt_messages (list): A list of message objects (e.g., [{"role": "user", "content": "Hello"}]).
        model (str): The Mistral model to use (e.g., "mistral-tiny", "mistral-small").

    Returns:
        str: The generated text content from the API response, or None if an error occurs.
    """
    if not MISTRAL_API_KEY:
        print("Error: MISTRAL_API_KEY environment variable not set.")
        return None

    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    payload = {
        "model": model,
        "messages": prompt_messages
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4XX or 5XX)
        data = response.json()
        if data.get('choices') and len(data['choices']) > 0:
            return data['choices'][0]['message']['content']
        else:
            print("Error: No choices found in Mistral API response.")
            print("Response data:", data)
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error calling Mistral API: {e}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                print(f"Response content: {e.response.json()}")
            except json.JSONDecodeError:
                print(f"Response content: {e.response.text}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

if __name__ == '__main__':
    # Example usage:
    if MISTRAL_API_KEY:
        print("Testing GenAI Client...")
        test_prompt = [{"role": "user", "content": "What is the capital of France?"}]
        generated_content = generate_text(test_prompt)
        if generated_content:
            print("Mistral's Response:")
            print(generated_content)
        else:
            print("Failed to get a response from Mistral.")
    else:
        print("MISTRAL_API_KEY not set. Cannot run example.")
