#!/usr/bin/env python3
"""
Evaluation script for testing the tuned interview assistant model.
This script compares the performance of the tuned model with the base model.
"""

from google import genai
import json
import os
import time
from tqdm import tqdm
import pandas as pd
import numpy as np

# For metrics
try:
    from rouge import Rouge
    from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
except ImportError:
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "rouge", "nltk", "tqdm"])
    from rouge import Rouge
    from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
    import nltk
    nltk.download('punkt', quiet=True)

# Initialize the Google API client
client = genai.Client()  # Uses GOOGLE_API_KEY env variable

# Configuration parameters
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODEL_INFO_PATH = os.path.join(BASE_DIR, "model_info.json")
TEST_DATA_PATH = os.path.join(BASE_DIR, "test_data.json")
RESULTS_PATH = os.path.join(BASE_DIR, "evaluation_results.json")
BASE_MODEL = "models/gemini-1.5-flash-001"  # Base model without tuning

def load_model_info():
    """Load model information from the saved file."""
    try:
        with open(MODEL_INFO_PATH, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Model info file not found at {MODEL_INFO_PATH}")
        return None

def load_test_data():
    """Load test data from the saved file."""
    try:
        with open(TEST_DATA_PATH, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Test data file not found at {TEST_DATA_PATH}")
        return None

def calculate_metrics(generated_text, reference_text):
    """Calculate ROUGE and BLEU metrics between generated and reference text."""
    metrics = {}
    
    # Calculate ROUGE scores
    rouge = Rouge()
    try:
        rouge_scores = rouge.get_scores(generated_text, reference_text)[0]
        metrics['rouge-1'] = rouge_scores['rouge-1']['f']
        metrics['rouge-l'] = rouge_scores['rouge-l']['f']
    except Exception as e:
        print(f"Error calculating ROUGE: {e}")
        metrics['rouge-1'] = 0
        metrics['rouge-l'] = 0
    
    # Calculate BLEU score
    try:
        reference = [reference_text.split()]
        candidate = generated_text.split()
        smooth = SmoothingFunction().method1
        metrics['bleu'] = sentence_bleu(reference, candidate, smoothing_function=smooth)
    except Exception as e:
        print(f"Error calculating BLEU: {e}")
        metrics['bleu'] = 0
        
    return metrics

def evaluate_model(model_name, test_data, model_type="tuned"):
    """Evaluate a model on the test data and return metrics."""
    print(f"\nEvaluating {model_type} model: {model_name}")
    
    results = {
        'model_name': model_name,
        'model_type': model_type,
        'overall': {'rouge-1': [], 'rouge-l': [], 'bleu': []},
        'by_quality': {
            'excellent': {'rouge-1': [], 'rouge-l': [], 'bleu': []},
            'adequate': {'rouge-1': [], 'rouge-l': [], 'bleu': []},
            'insufficient': {'rouge-1': [], 'rouge-l': [], 'bleu': []}
        }
    }
    
    for test_item in tqdm(test_data, desc=f"Testing {model_type} model"):
        input_text = test_item['input']
        gold_answer = test_item['gold_answer']
        quality = test_item['quality']
        
        # Generate response with model
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=input_text,
            )
            generated_answer = response.text
            
            # Calculate metrics
            metrics = calculate_metrics(generated_answer, gold_answer)
            
            # Add to overall results
            for metric, value in metrics.items():
                results['overall'][metric].append(value)
                results['by_quality'][quality][metric].append(value)
                
        except Exception as e:
            print(f"Error generating response: {e}")
    
    # Calculate averages
    for category in ['overall'] + list(results['by_quality'].keys()):
        if category == 'overall':
            metrics_dict = results['overall']
        else:
            metrics_dict = results['by_quality'][category]
            
        for metric in metrics_dict:
            if metrics_dict[metric]:
                metrics_dict[metric] = sum(metrics_dict[metric]) / len(metrics_dict[metric])
            else:
                metrics_dict[metric] = 0
    
    return results

def print_comparison(tuned_results, base_results):
    """Print a comparison of results between tuned and base models."""
    print("\n" + "="*50)
    print(f"COMPARISON: TUNED MODEL VS BASE MODEL")
    print("="*50)
    
    # Overall performance
    print("\nOVERALL PERFORMANCE:")
    print(f"Metric      | Tuned Model | Base Model | Improvement")
    print(f"-----------|------------|-----------|------------")
    for metric in ['rouge-1', 'rouge-l', 'bleu']:
        tuned = tuned_results['overall'][metric]
        base = base_results['overall'][metric]
        improvement = tuned - base
        improvement_pct = (improvement / base) * 100 if base > 0 else 0
        print(f"{metric:10} | {tuned:.4f}      | {base:.4f}     | {improvement_pct:+.2f}%")
    
    # Performance by quality
    print("\nPERFORMANCE BY ANSWER QUALITY:")
    for quality in ['excellent', 'adequate', 'insufficient']:
        print(f"\n{quality.upper()}:")
        print(f"Metric      | Tuned Model | Base Model | Improvement")
        print(f"-----------|------------|-----------|------------")
        for metric in ['rouge-1', 'rouge-l', 'bleu']:
            tuned = tuned_results['by_quality'][quality][metric]
            base = base_results['by_quality'][quality][metric]
            improvement = tuned - base
            improvement_pct = (improvement / base) * 100 if base > 0 else 0
            print(f"{metric:10} | {tuned:.4f}      | {base:.4f}     | {improvement_pct:+.2f}%")

def main():
    """Main evaluation function."""
    # Load model info and test data
    model_info = load_model_info()
    test_data = load_test_data()
    
    if not model_info or not test_data:
        print("Required files not found. Make sure to run training first.")
        return
    
    print(f"Loaded test data with {len(test_data)} examples.")
    print(f"Tuned model: {model_info['tuned_model']}")
    print(f"Base model: {BASE_MODEL}")
    
    # Evaluate the tuned model
    tuned_results = evaluate_model(
        model_info['tuned_model'], 
        test_data,
        "tuned"
    )
    
    # Evaluate the base model
    base_results = evaluate_model(
        BASE_MODEL, 
        test_data,
        "base"
    )
    
    # Print comparison
    print_comparison(tuned_results, base_results)
    
    # Save results
    all_results = {
        "tuned_model": tuned_results,
        "base_model": base_results
    }
    
    with open(RESULTS_PATH, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\nResults saved to {RESULTS_PATH}")

if __name__ == "__main__":
    main()
