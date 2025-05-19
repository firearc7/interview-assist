import json
import torch
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
from torch.utils.data import Dataset, DataLoader
import os

class TestQADataset(Dataset):
    def __init__(self, samples, tokenizer, label_map, max_length=512):
        self.samples = samples
        self.tokenizer = tokenizer
        self.label_map = label_map
        self.max_length = max_length

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        q = self.samples[idx]["question"]
        a = self.samples[idx]["answer"]
        label = self.label_map[self.samples[idx]["quality"]]
        combined_text = f"Question: {q} Answer: {a}"
        encoding = self.tokenizer(
            combined_text,
            truncation=True,
            padding="max_length",
            max_length=self.max_length,
            return_tensors="pt"
        )
        item = {key: val.squeeze(0) for key, val in encoding.items()}
        item["labels"] = torch.tensor(label)
        return item

def load_label_map(label_map_path):
    label_map = {}
    with open(label_map_path, "r") as f:
        for line in f:
            label, idx = line.strip().split("\t")
            label_map[label] = int(idx)
    return label_map

def evaluate(model, dataloader, device):
    model.eval()
    correct = 0
    total = 0
    all_preds = []
    all_labels = []
    with torch.no_grad():
        for batch in dataloader:
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)
            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            predictions = torch.argmax(outputs.logits, dim=1)
            total += labels.size(0)
            correct += (predictions == labels).sum().item()
            all_preds.extend(predictions.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
    accuracy = correct / total
    return accuracy, all_labels, all_preds

def main():
    test_data_path = "test_data.json"
    finetuned_model_path = "./checkpoint"
    base_model_name = "distilbert-base-uncased"

    # Load test samples
    with open(test_data_path, "r") as f:
        test_samples = json.load(f)

    # Load label map
    label_map_path = os.path.join(finetuned_model_path, "label_map.txt")
    label_map = load_label_map(label_map_path)
    idx_to_label = {idx: label for label, idx in label_map.items()}

    tokenizer = DistilBertTokenizer.from_pretrained(base_model_name)
    test_dataset = TestQADataset(test_samples, tokenizer, label_map)
    test_loader = DataLoader(test_dataset, batch_size=8)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Evaluate base model (no fine-tuning)
    print("Evaluating base (non-finetuned) model...")
    base_model = DistilBertForSequenceClassification.from_pretrained(
        base_model_name, num_labels=len(label_map)
    ).to(device)
    base_acc, base_labels, base_preds = evaluate(base_model, test_loader, device)
    print(f"Base model accuracy: {base_acc:.4f}")

    # Evaluate finetuned model
    print("Evaluating finetuned model...")
    finetuned_model = DistilBertForSequenceClassification.from_pretrained(
        finetuned_model_path
    ).to(device)
    finetuned_acc, finetuned_labels, finetuned_preds = evaluate(finetuned_model, test_loader, device)
    print(f"Finetuned model accuracy: {finetuned_acc:.4f}")

    # Detailed metrics if sklearn is available
    try:
        from sklearn.metrics import classification_report, confusion_matrix
        label_names = [label for label, idx in sorted(label_map.items(), key=lambda x: x[1])]
        print("\nBase model classification report:")
        print(classification_report(base_labels, base_preds, target_names=label_names))
        print("Base model confusion matrix:")
        print(confusion_matrix(base_labels, base_preds))

        print("\nFinetuned model classification report:")
        print(classification_report(finetuned_labels, finetuned_preds, target_names=label_names))
        print("Finetuned model confusion matrix:")
        print(confusion_matrix(finetuned_labels, finetuned_preds))
    except ImportError:
        print("scikit-learn not available. Install it for more detailed metrics.")

if __name__ == "__main__":
    main()
