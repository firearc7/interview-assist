import os
import requests

# Load the API key from environment variable
api_key = os.getenv("MISTRAL_API_KEY")

if not api_key:
    raise ValueError("MISTRAL_API_KEY environment variable not set.")

# Set your model and endpoint
url = "https://api.mistral.ai/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}
payload = {
    "model": "mistral-tiny",  # Or "mistral-small", "mistral-medium", etc.
    "messages": [
        {"role": "user", "content": "Hello, Mistral!"}
    ]
}

# Send the request
try:
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    data = response.json()
    print("Response from Mistral:")
    print(data['choices'][0]['message']['content'])
except requests.exceptions.RequestException as e:
    print("Request failed:")
    print(e)
