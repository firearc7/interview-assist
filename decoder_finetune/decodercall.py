import google.generativeai as genai
import os
from pathlib import Path
import json

# Explicitly get API key from environment variable
api_key = os.environ.get("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY environment variable not set")
    
# Configure the API key
genai.configure(api_key=api_key)

# List available models
for model in genai.list_models():
    print(model.name)

# Create training data as a list of prompt/response pairs
training_examples = [
    {"input_text": "1", "output_text": "2"},
    {"input_text": "3", "output_text": "4"},
    {"input_text": "-3", "output_text": "-2"},
    {"input_text": "twenty two", "output_text": "twenty three"},
    {"input_text": "two hundred", "output_text": "two hundred one"},
    {"input_text": "ninety nine", "output_text": "one hundred"},
    {"input_text": "8", "output_text": "9"},
    {"input_text": "-98", "output_text": "-97"},
    {"input_text": "1,000", "output_text": "1,001"},
    {"input_text": "10,100,000", "output_text": "10,100,001"},
    {"input_text": "thirteen", "output_text": "fourteen"},
    {"input_text": "eighty", "output_text": "eighty one"},
    {"input_text": "one", "output_text": "two"},
    {"input_text": "three", "output_text": "four"},
    {"input_text": "seven", "output_text": "eight"},
]

# Create a JSONL file with the examples
training_file = Path('/home/prasoon/Documents/code/interview-assist/decoder_finetune/training_data.jsonl')
with open(training_file, 'w') as f:
    for example in training_examples:
        f.write(json.dumps(example) + '\n')

print(f"Training data saved to {training_file}")

# Select an appropriate model that supports this type of task
model_name = "models/gemini-1.5-flash-001"  # Use an appropriate model from the list

# Test the model with a few examples using few-shot learning approach
def generate_next_number(input_text, examples=5):
    # Create a prompt with a few examples to guide the model
    few_shot_examples = training_examples[:examples]
    prompt = "You are a simple calculator that returns the next number in sequence. Only output the next number, nothing else. No explanations, no code, just the result.\n\n"
    
    for example in few_shot_examples:
        prompt += f"Input: {example['input_text']}\nOutput: {example['output_text']}\n\n"
    
    prompt += f"Input: {input_text}\nOutput:"
    
    # Create a model object and generate the response
    model = genai.GenerativeModel(model_name=model_name)
    
    try:
        # Generate the response
        response = model.generate_content(
            contents=prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.1,  # Slight increase in temperature for better variety
                top_p=0.95,
                top_k=5,
                max_output_tokens=10,
                stop_sequences=["\n"]  # Stop generating at a newline
            )
        )
        
        # Clean the response to ensure we just get the number
        result = response.text.strip()
        # Remove any code formatting that might appear
        if "```" in result:
            result = result.replace("```python", "").replace("```", "").strip()
        # Get just the first line if there's multiple lines
        result = result.split("\n")[0].strip()
        
        return result
    except Exception as e:
        return f"Error: {str(e)}"

# Test with a few examples
test_inputs = ["5", "sixteen", "42", "ninety-nine"]
print("\nTesting model with few-shot learning:")
for test in test_inputs:
    next_number = generate_next_number(test)
    print(f"Input: {test} → Output: {next_number}")