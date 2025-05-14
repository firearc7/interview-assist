# Finetuning Challenge: Encoder & Decoder Models (Mock Interview Platform)

## Application Overview
Our platform generates mock interviews tailored to a user's selected job role, job description, desired difficulty, and number of questions.

- **Encoder (DistilBERT):** Classifies user input (job role, description, hardness) into an interview type or difficulty band. This ensures users receive interviews that match their preferences and needs.
- **Decoder (LLaMA-2-7B):** Generates realistic, context-aware interview questions based on the classified intent, job role, and description. This makes the mock interview experience relevant and challenging.

## Why These Choices?
- **Encoder:** Efficiently routes user requests to the right interview template or difficulty, improving user experience and system scalability.
- **Decoder:** Produces high-quality, domain-specific interview questions, enhancing the realism and value of the mock interview.

## Datasets
- **Encoder:** Synthetic dataset mapping (job role, description, hardness) to interview type/difficulty (`encoder_dataset.csv`).
- **Decoder:** Synthetic dataset of (job role, description, hardness, number of questions) mapped to generated interview questions (`decoder_dataset.jsonl`).

## Finetuning Steps
1. **Encoder:**
   - Model: DistilBERT (Hugging Face Transformers)
   - Task: Multi-class classification
   - Dataset: Labeled job role/description/hardness samples
   - Metrics: Accuracy, F1-score
2. **Decoder:**
   - Model: LLaMA-2-7B (Hugging Face Transformers)
   - Task: Text generation
   - Dataset: Q&A pairs for various roles and difficulties
   - Metrics: BLEU/ROUGE, sample generations

## Evaluation
- **Encoder:** Reported accuracy and F1-score on a held-out set.
- **Decoder:** Show sample generations and BLEU/ROUGE scores.

## Conclusion
This approach demonstrates how encoder and decoder models can work together in a mock interview platform: encoders for routing/classification, decoders for content generation. Finetuning on domain data ensures both accuracy and relevance.
