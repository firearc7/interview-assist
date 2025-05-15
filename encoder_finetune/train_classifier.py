import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification, Trainer, TrainingArguments

class AnswerDataset(Dataset):
    def __init__(self, csv_path, tokenizer, max_length=256):
        df = pd.read_csv(csv_path)
        self.answers = df["answer"].astype(str).tolist()
        self.labels = df["class"].map({"Needs Improvement": 0, "Adequate": 1, "Excellent": 2}).tolist()
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.answers)

    def __getitem__(self, idx):
        encoding = self.tokenizer(
            self.answers[idx],
            truncation=True,
            padding="max_length",
            max_length=self.max_length,
            return_tensors="pt"
        )
        item = {key: val.squeeze(0) for key, val in encoding.items()}
        item["labels"] = torch.tensor(self.labels[idx])
        return item

def main():
    csv_path = "./answer_quality_dataset.csv"
    model_path = "./checkpoint"
    tokenizer = DistilBertTokenizer.from_pretrained("distilbert-base-uncased")
    model = DistilBertForSequenceClassification.from_pretrained("distilbert-base-uncased", num_labels=3)

    dataset = AnswerDataset(csv_path, tokenizer)
    train_args = TrainingArguments(
        output_dir=model_path,
        num_train_epochs=3,
        per_device_train_batch_size=8,
        save_steps=50,
        save_total_limit=1,
        logging_steps=10,
        learning_rate=2e-5
    )
    trainer = Trainer(
        model=model,
        args=train_args,
        train_dataset=dataset,
        tokenizer=tokenizer
    )
    trainer.train()
    model.save_pretrained(model_path)
    tokenizer.save_pretrained(model_path)

if __name__ == "__main__":
    main()
