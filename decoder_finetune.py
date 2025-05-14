import json
import random
from datasets import load_dataset, Dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer, DataCollatorForLanguageModeling
import torch

# Load synthetic Q&A data
data = []
with open("decoder_dataset.jsonl", "r") as f:
    for line in f:
        data.append(json.loads(line))

# Prepare prompt/response pairs
examples = []
for item in data:
    prompt = f"Role: {item['job_role']}\nDescription: {item['job_description']}\nDifficulty: {item['hardness']}\nNumber of Questions: {item['num_questions']}\nGenerate interview questions:"
    response = "\n".join(item['questions'])
    examples.append({"prompt": prompt, "response": response})

dataset = Dataset.from_list(examples)
dataset = dataset.train_test_split(test_size=0.3, seed=42)

# Tokenizer and model
model_name = "meta-llama/Llama-2-7b-hf"
tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=True)
model = AutoModelForCausalLM.from_pretrained(model_name)

def preprocess(example):
    input_text = example['prompt'] + "\n" + example['response']
    return tokenizer(input_text, truncation=True, padding='max_length', max_length=256)

tokenized_train = dataset['train'].map(preprocess, batched=False)
tokenized_test = dataset['test'].map(preprocess, batched=False)

data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

# Training
training_args = TrainingArguments(
    output_dir="./llama_results",
    num_train_epochs=5,
    per_device_train_batch_size=1,
    per_device_eval_batch_size=1,
    evaluation_strategy="epoch",
    logging_dir="./llama_logs",
    save_strategy="no"
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_train,
    eval_dataset=tokenized_test,
    data_collator=data_collator,
)

trainer.train()

# Evaluation: generate sample outputs
sample = dataset['test'][0]
input_ids = tokenizer(sample['prompt'], return_tensors="pt").input_ids
output = model.generate(input_ids, max_new_tokens=100)
generated = tokenizer.decode(output[0], skip_special_tokens=True)

with open("decoder_eval_results.txt", "w") as f:
    f.write("Prompt:\n" + sample['prompt'] + "\n\nGenerated:\n" + generated)
print("Decoder finetuning and evaluation complete.")
