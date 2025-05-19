import pandas as pd
import torch
from torch.utils.data import Dataset
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification, Trainer, TrainingArguments
from sklearn.model_selection import train_test_split
import numpy as np
import random
import os
import time
import json

class InterviewQADataset(Dataset):
    def __init__(self, csv_path, tokenizer, max_length=256):
        df = pd.read_csv(csv_path)
        self.questions = df["question"].astype(str).tolist()
        self.answers = df["answer"].astype(str).tolist()
        self.labels = df["quality"].tolist()  # Store original quality values
        
        # Create label mapping dynamically from unique values
        unique_labels = sorted(set(self.labels))
        self.label_map = {label: idx for idx, label in enumerate(unique_labels)}
        self.num_labels = len(unique_labels)
        
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.answers)

    def __getitem__(self, idx):
        # Combine question and answer for better context
        combined_text = f"Question: {self.questions[idx]} Answer: {self.answers[idx]}"
        
        encoding = self.tokenizer(
            combined_text,
            truncation=True,
            padding="max_length",
            max_length=self.max_length,
            return_tensors="pt"
        )
        item = {key: val.squeeze(0) for key, val in encoding.items()}
        item["labels"] = torch.tensor(self.label_map[self.labels[idx]])
        return item

def main():
    csv_path = "../../dataset/interview_qa_dataset.csv"
    model_path = "./checkpoint"
    tokenizer = DistilBertTokenizer.from_pretrained("distilbert-base-uncased")
    
    # Option to use random seed or fixed seed
    use_random_seed = True  # Set to False for reproducible results
    
    if use_random_seed:
        # Generate truly random seeds based on current time
        random_seed = int(time.time()) % 10000
        torch_seed = (random_seed + 1) % 10000
        np_seed = (random_seed + 2) % 10000
        
        # Set all random seeds to different values
        random.seed(random_seed)
        np.random.seed(np_seed)
        torch.manual_seed(torch_seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(torch_seed)
        
        print(f"Using random seeds - random: {random_seed}, numpy: {np_seed}, torch: {torch_seed}")
    else:
        # Fixed seed for reproducibility
        fixed_seed = 42
        random.seed(fixed_seed)
        np.random.seed(fixed_seed)
        torch.manual_seed(fixed_seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(fixed_seed)
        print(f"Using fixed seed: {fixed_seed}")
    
    # Load the data
    df = pd.read_csv(csv_path)
    
    # Shuffle the dataframe before splitting
    df = df.sample(frac=1.0, random_state=random.randint(0, 10000) if use_random_seed else 42)
    
    # Calculate the maximum sequence length in the dataset
    df['combined_text'] = "Question: " + df['question'] + " Answer: " + df['answer']
    
    max_possible_length = 512  # DistilBERT's maximum context length
    
    # Use different random state for train-test split
    split_random_state = None if use_random_seed else 42
    train_df, test_df = train_test_split(df, test_size=0.1, random_state=split_random_state)
    
    print(f"Split random state: {'Random' if split_random_state is None else split_random_state}")
    
    # Save test samples to test_data.json
    test_samples = test_df[["question", "answer", "quality"]].to_dict(orient="records")
    with open("test_data.json", "w") as f:
        json.dump(test_samples, f, indent=2)
    
    # Create datasets directly from the dataframes
    class DataFrameDataset(InterviewQADataset):
        def __init__(self, dataframe, tokenizer, max_length=512):
            self.questions = dataframe["question"].astype(str).tolist()
            self.answers = dataframe["answer"].astype(str).tolist()
            self.labels = dataframe["quality"].tolist()
            
            # Create label mapping dynamically from unique values
            unique_labels = sorted(set(self.labels))
            self.label_map = {label: idx for idx, label in enumerate(unique_labels)}
            self.num_labels = len(unique_labels)
            
            self.tokenizer = tokenizer
            self.max_length = max_length
    
    # Create train dataset directly from the dataframe
    train_dataset = DataFrameDataset(train_df, tokenizer, max_length=max_possible_length)
    
    model = DistilBertForSequenceClassification.from_pretrained(
        "distilbert-base-uncased", 
        num_labels=train_dataset.num_labels
    )

    train_args = TrainingArguments(
        output_dir=model_path,
        num_train_epochs=3,
        per_device_train_batch_size=8,
        save_steps=50,
        save_total_limit=1,
        logging_steps=10,
        learning_rate=2e-5,
        seed=random.randint(0, 10000) if use_random_seed else 2023111014,  # Random or fixed seed
        dataloader_drop_last=True,
    )
    
    print(f"Training with seed: {train_args.seed}")
    
    trainer = Trainer(
        model=model,
        args=train_args,
        train_dataset=train_dataset,
        tokenizer=tokenizer
    )
    trainer.train()
    model.save_pretrained(model_path)
    tokenizer.save_pretrained(model_path)
    
    # Save label mapping for future inference
    with open(f"{model_path}/label_map.txt", "w") as f:
        for label, idx in train_dataset.label_map.items():
            f.write(f"{label}\t{idx}\n")
    
    print(f"Model trained and saved to {model_path}")
    print(f"Train set size: {len(train_dataset)}")
    print(f"Test set size: {len(test_samples)}")
    print("Test samples saved to test_data.json")

if __name__ == "__main__":
    main()
