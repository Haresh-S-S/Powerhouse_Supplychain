---
language: en
license: apache-2.0
tags:
  - distilbert
  - text-classification
  - supply-chain
  - risk-classification
datasets:
  - custom
---

# Supply Chain DistilBERT Risk Classifier

Fine-tuned `distilbert-base-uncased` for 4-class electronics supply chain risk:
**LOW | MEDIUM | HIGH | CRITICAL**

Trained on `lite_master` rows from the supply-chain-disrupter project.

## Usage

```python
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch

model_id = "mathurvarun84/supply-chain-distilbert-risk"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForSequenceClassification.from_pretrained(model_id)

text = "Region: Eastern Asia. Product: DRAM. Delivery: Late delivery. ..."
inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=256)
with torch.no_grad():
    pred = model(**inputs).logits.argmax(-1).item()
labels = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
print(labels[pred])
```

## Local project

Set in `.env`:
```
DISTILBERT_MODEL_ID=mathurvarun84/supply-chain-distilbert-risk
```
