#!/usr/bin/env python3
# filepath: /home/firearc7/Documents/iREL/interview-assist/dataset_generator.py

import os
import csv
import time
import random
import requests
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

# Get API key from environment variable
MISTRAL_API_KEY = os.environ.get("MISTRAL_API_KEY")
if not MISTRAL_API_KEY:
    raise ValueError("MISTRAL_API_KEY environment variable not set")

# Define constants
TOTAL_SAMPLES = 600
SAMPLES_PER_CLASS = 200
OUTPUT_FILE = "interview_qa_dataset.csv"

# Define topics to cover in the interview questions
TOPICS = [
    "Data Structures", "Algorithms", "Object-Oriented Programming", 
    "System Design", "Databases", "Operating Systems", "Networking",
    "Web Development", "Front-end Frameworks", "Back-end Development",
    "Cloud Computing", "DevOps", "Microservices", "Security",
    "Testing", "CI/CD", "Version Control", "Agile Methodologies",
    "API Design", "Concurrency", "Parallel Programming", "Memory Management",
    "Design Patterns", "Problem Solving", "Debugging", "Performance Optimization",
    "Mobile Development", "Machine Learning Basics", "Ethics in Software Engineering"
]

# Mistral API configuration
MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"
MODEL = "mistral-large-latest"

def generate_prompt_for_question(topic):
    return f"""Generate a challenging interview question for a Software Development Engineer about {topic}. 
    The question should be technical and specific, testing deep knowledge. 
    Return only the question text without any explanations or introductions."""

def generate_prompt_for_answers(question, quality):
    quality_descriptions = {
        "excellent": "comprehensive, accurate, well-structured, detailed, demonstrating deep understanding with relevant examples and best practices",
        "adequate": "mostly correct but lacking depth, missing some important details or examples, somewhat disorganized, shows basic understanding but not mastery",
        "insufficient": "incomplete, contains some inaccuracies or misconceptions, poorly structured, superficial understanding, missing critical components"
    }
    
    human_speech_patterns = {
        "excellent": "Include some natural speech patterns, occasional pauses (like 'um' or brief thinking), realistic examples from work experience, and confident tone. The candidate might start with phrases like 'That's a great question' or 'In my experience'. Include 1-2 specific examples from hypothetical past work.",
        "adequate": "Include some hesitation, self-corrections, and a mix of detailed and vague explanations. The candidate might use phrases like 'I think', 'If I recall correctly', or 'Generally speaking'. They might also make minor verbal detours before returning to the main point.",
        "insufficient": "Include circular explanations and occasional contradictions. The candidate might try to talk around concepts they don't fully understand, use vague terms, and might say 'to be honest, I'm not entirely certain' or similar phrases indicating knowledge gaps."
    }
    
    return f"""For the following software engineering interview question: 
    
    "{question}"
    
    Generate a {quality} answer as if given by a real human candidate in a live interview. The answer should be {quality_descriptions[quality]}.
    
    {human_speech_patterns[quality]}
    
    Make the response sound conversational and spontaneous as if spoken rather than written. Don't make it TOO polished.
    
    Return only the answer without any introductions or explanations about its quality."""

def generate_prompt_for_gold_answer(question, answer, quality):
    """Generate prompt for gold standard answer based on the question, original answer, and quality"""
    
    if quality == "excellent":
        return f"""For the following software engineering interview question:
        
        "{question}"
        
        Given this excellent answer from a candidate:
        
        "{answer}"
        
        Provide a slightly refined gold standard version of this answer that maintains the same structure and content, 
        but with minimal improvements to clarity and precision. Keep the answer similarly excellent but 
        with subtle enhancements. Maintain a professional tone but make it slightly more polished than the original.
        
        Return only the gold standard answer without any explanations."""
    
    elif quality == "adequate":
        return f"""For the following software engineering interview question:
        
        "{question}"
        
        Given this adequate answer from a candidate:
        
        "{answer}"
        
        Transform this into a gold standard excellent answer. Enhance it by:
        1. Adding more technical depth and detailed explanations
        2. Incorporating relevant examples and best practices
        3. Improving the structure and flow
        4. Filling in missing information
        5. Maintaining the core ideas from the original answer
        
        Make it comprehensive and technically precise while still being clear and concise.
        Return only the gold standard answer without any explanations."""
    
    else:  # insufficient
        return f"""For the following software engineering interview question:
        
        "{question}"
        
        Given this insufficient answer from a candidate:
        
        "{answer}"
        
        Create a gold standard answer that:
        1. Corrects any misconceptions or inaccuracies in the original
        2. Develops the same core topic areas but with proper technical depth
        3. Provides clarity where the original was vague
        4. Adds necessary details, examples, and best practices
        5. Maintains the same general approach but with substantially improved quality
        
        Transform the answer into a comprehensive, well-structured response that would be considered excellent.
        Return only the gold standard answer without any explanations."""

def call_mistral_api(prompt, max_tokens=500):
    """Call Mistral API with the given prompt"""
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": 0.7
    }
    
    retries = 5  # Increased retries
    base_delay = 2  # Base delay in seconds
    max_delay = 60  # Maximum delay in seconds
    
    for attempt in range(retries):
        try:
            response = requests.post(MISTRAL_API_URL, headers=headers, json=data, timeout=30)
            
            # Handle rate limiting (429) or server errors (5xx)
            if response.status_code == 429 or (response.status_code >= 500 and response.status_code < 600):
                wait_time = min(base_delay * (2 ** attempt) + random.uniform(0, 1), max_delay)
                print(f"Rate limited or server error (status {response.status_code}). Waiting {wait_time:.2f}s...")
                time.sleep(wait_time)
                continue
                
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"].strip()
            return content
            
        except requests.exceptions.Timeout:
            wait_time = min(base_delay * (2 ** attempt) + random.uniform(0, 1), max_delay)
            print(f"Request timed out. Waiting {wait_time:.2f}s before retry...")
            time.sleep(wait_time)
            
        except requests.exceptions.RequestException as e:
            wait_time = min(base_delay * (2 ** attempt) + random.uniform(0, 1), max_delay)
            print(f"API request error: {str(e)}. Waiting {wait_time:.2f}s...")
            time.sleep(wait_time)
            
        except (KeyError, IndexError, ValueError) as e:
            print(f"Error parsing API response: {str(e)}")
            if attempt < retries - 1:
                wait_time = min(base_delay * (2 ** attempt) + random.uniform(0, 1), max_delay)
                print(f"Retrying in {wait_time:.2f}s...")
                time.sleep(wait_time)
            else:
                raise
                
        except Exception as e:
            if attempt < retries - 1:
                wait_time = min(base_delay * (2 ** attempt) + random.uniform(0, 1), max_delay)
                print(f"Unexpected error: {str(e)}. Retrying in {wait_time:.2f}s...")
                time.sleep(wait_time)
            else:
                print(f"API call failed after {retries} attempts: {str(e)}")
                raise
    
    return None

def generate_sample(topic, quality, asked_questions=None):
    """Generate a complete sample (question, answer, quality, and gold answer)"""
    try:
        # Generate question based on topic
        max_attempts = 3  # Maximum attempts to generate a unique question
        question = None
        
        for _ in range(max_attempts):
            question_prompt = generate_prompt_for_question(topic)
            new_question = call_mistral_api(question_prompt, max_tokens=200)
            
            # Check if this question (or similar) has already been asked
            if asked_questions and new_question.strip().lower() in asked_questions:
                print(f"Duplicate question detected, regenerating...")
                continue
            else:
                question = new_question
                break
        
        if not question:
            print(f"Failed to generate unique question after {max_attempts} attempts")
            return None
        
        # Generate answer based on question and desired quality
        answer_prompt = generate_prompt_for_answers(question, quality)
        answer = call_mistral_api(answer_prompt, max_tokens=800)
        
        # Generate gold standard answer based on the question, answer, and quality
        gold_prompt = generate_prompt_for_gold_answer(question, answer, quality)
        gold_answer = call_mistral_api(gold_prompt, max_tokens=1000)
        
        return {
            "question": question,
            "answer": answer,
            "quality": quality,
            "gold_answer": gold_answer
        }
    except Exception as e:
        print(f"Error generating sample for {topic}, {quality}: {str(e)}")
        return None

def main():
    print(f"Generating {TOTAL_SAMPLES} interview Q&A samples...")
    
    # Prepare distribution of samples
    qualities = ["excellent", "adequate", "insufficient"]
    samples_needed = {quality: SAMPLES_PER_CLASS for quality in qualities}
    
    # Prepare data collection
    dataset = []
    failed_attempts = []
    asked_questions = set()  # Track already asked questions to avoid duplicates
    
    # Try to load existing dataset to avoid duplicates
    if os.path.exists(OUTPUT_FILE):
        try:
            print(f"Found existing dataset file. Loading to prevent duplicate questions...")
            with open(OUTPUT_FILE, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    asked_questions.add(row["question"].strip())
            print(f"Loaded {len(asked_questions)} existing questions that will be avoided.")
        except Exception as e:
            print(f"Error loading existing dataset: {str(e)}")
    
    # Save partial results after every N samples
    checkpoint_interval = 25
    checkpoint_file = "dataset_checkpoint.csv"
    
    # Use ThreadPoolExecutor to parallelize API calls with reduced concurrency
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = []
        
        # Submit jobs to the executor
        for quality in qualities:
            for _ in range(SAMPLES_PER_CLASS):
                topic = random.choice(TOPICS)
                futures.append(executor.submit(generate_sample, topic, quality, asked_questions))
        
        # Process results as they complete
        completed = 0
        for future in tqdm(as_completed(futures), total=len(futures), desc="Generating samples"):
            try:
                sample = future.result()
                if sample:
                    dataset.append(sample)
                    completed += 1
                    # Save checkpoint periodically
                    if completed % checkpoint_interval == 0:
                        print(f"\nSaving checkpoint ({completed}/{TOTAL_SAMPLES})...")
                        with open(checkpoint_file, 'w', newline='', encoding='utf-8') as file:
                            writer = csv.DictWriter(file, fieldnames=["question", "answer", "quality", "gold_answer"])
                            writer.writeheader()
                            writer.writerows(dataset)
                else:
                    failed_attempts.append((topic, quality))
            except Exception as e:
                print(f"Error processing result: {str(e)}")
                failed_attempts.append((topic, quality))
                
            # Add a small delay between processing results to reduce API pressure
            time.sleep(0.2)
    
    # Write to CSV
    print(f"Writing {len(dataset)} samples to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["question", "answer", "quality", "gold_answer"])
        writer.writeheader()
        writer.writerows(dataset)
    
    print("Dataset generation complete!")
    
    # Basic stats
    quality_counts = {}
    for sample in dataset:
        quality = sample["quality"]
        quality_counts[quality] = quality_counts.get(quality, 0) + 1
    
    print("\nDataset Statistics:")
    for quality, count in quality_counts.items():
        print(f"- {quality.capitalize()}: {count} samples")

if __name__ == "__main__":
    main()
