#!/usr/bin/env python3
"""
Main script for training and saving an interview assistant model.
This script handles data loading, preprocessing, and model fine-tuning.
"""

from google import genai
from google.genai import types
import pandas as pd
import os
import json
import time
from sklearn.model_selection import train_test_split

# Initialize the Google API client
client = genai.Client()  # Uses GOOGLE_API_KEY env variable

# Configuration parameters
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATASET_PATH = os.path.join(BASE_DIR, "dataset", "interview_qa_dataset.csv")
MODEL_INFO_PATH = os.path.join(BASE_DIR, "model_info.json")
TEST_DATA_PATH = os.path.join(BASE_DIR, "test_data.json")
BASE_MODEL = "models/gemini-1.5-flash-001-tuning"

def main():
    # Read the interview_qa_dataset.csv
    print(f"Loading dataset from {DATASET_PATH}")
    df = pd.read_csv(DATASET_PATH)

    print(f"Dataset loaded with {len(df)} entries")
    print("Columns:", df.columns.tolist())

    # Split the dataset into training (80%) and test (20%) sets
    train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)
    print(f"Split dataset into {len(train_df)} training samples and {len(test_df)} test samples")

    # Create input-output pairs for tuning
    # Format: Input will be "Question: {question}\nAnswer: {answer}\nQuality: {quality}"
    # Output will be the gold_answer
    training_data = []
    for _, row in train_df.iterrows():
        input_text = f"Question: {row['question']}\nAnswer: {row['answer']}\nQuality: {row['quality']}"
        output_text = row['gold_answer']
        training_data.append((input_text, output_text))

    # Create test data pairs for evaluation and save for later testing
    test_data = []
    for _, row in test_df.iterrows():
        test_item = {
            "input": f"Question: {row['question']}\nAnswer: {row['answer']}\nQuality: {row['quality']}",
            "gold_answer": row['gold_answer'],
            "quality": row['quality']
        }
        test_data.append(test_item)

    # Save test data to file for later evaluation
    print(f"Saving test data to {TEST_DATA_PATH}")
    with open(TEST_DATA_PATH, 'w') as f:
        json.dump(test_data, f, indent=2)
        
    # Convert to TuningDataset format
    training_dataset = types.TuningDataset(
        examples=[
            types.TuningExample(
                text_input=i,
                output=o,
            )
            for i, o in training_data
        ],
    )

    # Start the tuning job
    print(f"Starting tuning job using base model: {BASE_MODEL}")
    tuning_job = client.tunings.tune(
        base_model=BASE_MODEL,
        training_dataset=training_dataset,
        config=types.CreateTuningJobConfig(
            epoch_count=5,
            batch_size=4,
            learning_rate=0.001,
            tuned_model_display_name="interview_qa_tuned_model"
        )
    )

    # Wait for the tuning job to complete
    print("Tuning job started. Job name:", tuning_job.name)

    # Instead of using wait(), we'll use a polling approach to check job status
    while True:
        # Get the latest status of the tuning job
        job_status = client.tunings.get(name=tuning_job.name)
        print(f"Current state: {job_status.state}")
        
        # If job is in a terminal state, break the loop
        if "SUCCEEDED" in str(job_status.state) or "FAILED" in str(job_status.state) or "CANCELLED" in str(job_status.state):
            tuning_job = job_status
            break
        
        # Wait for some time before checking again
        print("Job still running, waiting...")
        time.sleep(60)  # Check every minute

    print("Tuning job completed with state:", tuning_job.state)

    # Save the model information for later use
    if "SUCCEEDED" in str(tuning_job.state) and tuning_job.tuned_model:
        model_info = {
            "tuned_model": tuning_job.tuned_model.model,
            "base_model": BASE_MODEL,
            "training_samples": len(training_data),
            "test_samples": len(test_data),
            "tuning_job_name": tuning_job.name,
            "completion_time": str(tuning_job.end_time) if tuning_job.end_time else None
        }
        
        print(f"Saving model information to {MODEL_INFO_PATH}")
        with open(MODEL_INFO_PATH, 'w') as f:
            json.dump(model_info, f, indent=2)
            
        print("Model training complete. You can now use the model for inference.")
        print(f"Tuned model ID: {tuning_job.tuned_model.model}")
    else:
        print("Tuning job did not complete successfully or tuned model is not available.")
        print("Tuning job details:", tuning_job)

if __name__ == "__main__":
    main()
