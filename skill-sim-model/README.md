---
library_name: sentence-transformers
pipeline_tag: sentence-similarity
license: apache-2.0
tags:
- sentence-transformers
- feature-extraction
- sentence-similarity
- job-matching
- skill-similarity
- embeddings
- esco
---

# 🛠️ alvperez/skill-sim-model

**skill-sim-model** is a fine-tuned [Sentence-Transformers](https://www.sbert.net) checkpoint that maps short *skill phrases* (e.g. `Python`, `Forklift operation`, `Electrical wiring`) into a 768‑D vector space where semantically related skills cluster together.  
Training pairs come from the public **ESCO** taxonomy plus curated *hard negatives* for job‑matching research.

| Use‑case | How to leverage the embeddings |
|----------|--------------------------------|
| Candidate ↔ vacancy matching | `score = cosine(skill_vec, job_vec)` |
| Deduplicating skill taxonomies | cluster the vectors |
| Recruiter query‑expansion | nearest‑neighbour search |
| Exploratory dashboards | feed to t‑SNE / PCA |

---

## 🚀 Quick start

```bash
pip install -U sentence-transformers
```

```python
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("alvperez/skill-sim-model")

skills = ["Electrical wiring",
          "Circuit troubleshooting",
          "Machine learning"]

emb = model.encode(skills, convert_to_tensor=True)
print(util.pytorch_cos_sim(emb[0], emb))   # similarity matrix
```

```python
from transformers import pipeline
similarity = pipeline("sentence-similarity",
                      model="alvperez/skill-sim-model")
similarity("forklift operation",
           ["pallet jack", "python"])
```

---

## 📊 Benchmark

| Metric                         | Value |
|--------------------------------|-------|
| Spearman correlation           | **0.845** |
| ROC AUC                        | **0.988** |
| MAP@all (*cold‑start*)         | **0.232** |

> *cold‑start = the system sees only skill strings, no historical interactions.*

---

## ⚙️ Training recipe (brief)

* Base: `sentence-transformers/all-mpnet-base-v2`  
* Loss: `CosineSimilarityLoss`  
* Epochs × batch: `5 × 32`  
* LR / warm‑up: `2 e‑5` / `100` steps  
* Negatives: random + “hard” pairs from ESCO siblings  
* Hardware: 1 × A100 40 GB (≈ 45 min)

Full code in [`/training_scripts`](training_scripts).

---

## 🏹 Intended use

* **Employment tech** – rank CVs vs. vacancies  
* **EdTech / reskilling** – detect skill gaps, suggest learning paths  
* **HR analytics** – normalise noisy skill fields at scale  

---

## ✋ Limitations & bias

* Vocabulary dominated by ESCO (English); niche jargon may project poorly.  
* No explicit fairness constraints; downstream systems should audit (e.g. *Disparate Impact*).  
* In our tests, a threshold of 0.65 marks a “definitely related” cut‑off; tune for your own precision‑recall needs.

---

## 🔍 Citation

```bibtex
@misc{alvperez2025skillsim,
  title  = {Skill-Sim: a Sentence-Transformers model for skill similarity and job matching},
  author = {Pérez Amado, Álvaro},
  howpublished = {\url{https://huggingface.co/alvperez/skill-sim-model}},
  year   = {2025}
}
```

---

### Acknowledgements

Built on top of Sentence-Transformers and the public **ESCO** dataset.  
Feedback & PRs welcome!
