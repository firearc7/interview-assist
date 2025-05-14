import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification, Trainer, TrainingArguments
import torch

# Load and preprocess data
csv_path = "encoder_dataset.csv"
df = pd.read_csv(csv_path, comment='#')

# Use only the new format for finetuning
if 'job_role' in df.columns:
    df = df.dropna(subset=['job_role'])
    df['input'] = df['job_role'] + ' | ' + df['job_description'] + ' | ' + df['hardness']
    X = df['input'].tolist()
    y = df['interview_type'].astype('category').cat.codes.tolist()
    label2id = {v: k for k, v in enumerate(df['interview_type'].astype('category').cat.categories)}
else:
    raise ValueError("No job_role/job_description/hardness columns found.")

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Tokenization
tokenizer = DistilBertTokenizerFast.from_pretrained('distilbert-base-uncased')
train_encodings = tokenizer(X_train, truncation=True, padding=True)
test_encodings = tokenizer(X_test, truncation=True, padding=True)

class InterviewDataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels
    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx])
        return item
    def __len__(self):
        return len(self.labels)

train_dataset = InterviewDataset(train_encodings, y_train)
test_dataset = InterviewDataset(test_encodings, y_test)

# Model
model = DistilBertForSequenceClassification.from_pretrained('distilbert-base-uncased', num_labels=len(set(y)))

# Training
training_args = TrainingArguments(
    output_dir='./results',
    num_train_epochs=10,
    per_device_train_batch_size=2,
    per_device_eval_batch_size=2,
    evaluation_strategy="epoch",
    logging_dir='./logs',
    logging_steps=10,
    save_strategy="no"
)

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = logits.argmax(-1)
    report = classification_report(labels, preds, output_dict=True)
    return {"accuracy": report["accuracy"]}

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=test_dataset,
    compute_metrics=compute_metrics
)

trainer.train()

# Evaluation
results = trainer.evaluate()
with open("encoder_eval_results.txt", "w") as f:
    f.write(str(results))
    preds = trainer.predict(test_dataset).predictions.argmax(-1)
    f.write("\n\nClassification Report:\n")
    f.write(classification_report(y_test, preds, target_names=list(label2id.keys())))
print("Encoder finetuning and evaluation complete.")
