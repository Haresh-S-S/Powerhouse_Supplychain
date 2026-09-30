---
license: mit
base_model: numind/NuExtract-tiny-v1.5
tags:
  - nlp
  - json
  - information-extraction
  - resume-parsing
  - structured-extraction
  - qwen2
  - unsloth
  - lora
  - gguf
  - ollama
  - langchain
language:
  - en
pipeline_tag: text-generation
library_name: transformers
---

# NuExtract-tiny-Resume-Data-Extractor

A fine-tuned version of [numind/NuExtract-tiny-v1.5](https://huggingface.co/numind/NuExtract-tiny-v1.5)
(Qwen2.5-0.5B backbone) specialised for **resume / CV structured extraction**.

Given raw resume text in any format, the model returns a clean JSON object with name,
contact details, skills, work experience, education, and other details — ready to plug
into a hiring pipeline, ATS, or LangChain workflow.

![Gemini_Generated_Image_t8vmzet8vmzet8vm.png](https://cdn-uploads.huggingface.co/production/uploads/69e38d3a85cbb38401962a34/CSpI68gEFsI_-ENhHQi6z.jpeg)

## Model Details

| Property | Value |
|---|---|
| Base model | `numind/NuExtract-tiny-v1.5` |
| Backbone | Qwen2.5-0.5B |
| Total parameters | 511,388,160 |
| Trainable (LoRA) | 17,596,416 (3.44%) |
| LoRA rank / alpha | r=32 / alpha=64 |
| Quantisation | Q4_K_M GGUF (Ollama-ready) |
| Vocabulary size | 151,665 (unchanged from base) |
| License | MIT |

---

## Training

| Property | Value |
|---|---|
| Method | QLoRA via Unsloth |
| Dataset | 3,000 synthetic resumes (generated) |
| Train / eval split | 95% / 5% (2,850 / 150) |
| Packed sequences | 1,125 |
| Epochs | 4 |
| Total steps | 284 |
| Batch size | 16 (2 per device × 8 grad accum) |
| Learning rate | 2e-4 (cosine schedule, 14 warmup steps) |
| Hardware | 1× NVIDIA Tesla T4 (Google Colab) |
| Training time | ~24 minutes |

### Loss Curve

| Step | Epoch | Train Loss | Val Loss |
|---|---|---|---|
| 100 | 1.0 | 0.2355 | 0.2354 |
| 200 | 2.8 | 0.2298 | 0.2313 |
| 284 | 4.0 | 0.2276 | 0.2296 |

Near-zero train/val gap throughout — no overfitting observed.
Best checkpoint (step 284, val loss 0.2296) loaded automatically.

---

## Output Schema

```json
{
  "name":         "string or null",
  "email":        "string or null",
  "phone":        "string or null",
  "website":      "string or null",
  "skills":       ["string"],
  "experience":   [{"title": "string", "company": "string", "duration": "string"}],
  "education":    [{"degree": "string", "institution": "string", "year": "string"}],
  "other_details": ["string"]
}
```

- Missing scalar fields → `null`
- Missing list fields → `[]`
- `skills` contains technical skills only — soft skills excluded
- `other_details` captures certifications, languages, awards, publications

---

## Inference Speed (Ollama, Tesla T4)

| Metric | Value |
|---|---|
| Prompt eval | 161 tokens in ~28ms |
| Generation | 154 tokens in ~2,986ms |
| Total (typical resume) | ~7.5 seconds |
| Throughput | ~52 tokens/sec |

---

## Usage

### Ollama (recommended)

**Step 1 — Create Modelfile:**

```dockerfile
FROM hf.co/nimendraai/NuExtract-tiny-Resume-Data-Extractor:Q4_K_M

PARAMETER temperature 0
PARAMETER top_k 10
PARAMETER top_p 0.9
PARAMETER repeat_penalty 1.1
PARAMETER seed 42
PARAMETER num_ctx 2048
PARAMETER num_predict 600
PARAMETER stop "<|end-output|>"
PARAMETER stop "<|endoftext|>"

TEMPLATE """<|input|>
### Template:
{
    "name": "",
    "email": "",
    "phone": "",
    "website": "",
    "skills": [""],
    "experience": [{"title": "", "company": "", "duration": ""}],
    "education": [{"degree": "", "institution": "", "year": ""}],
    "other_details": [""]
}
### Text:
{{ .Prompt }}

<|output|>
"""

LICENSE """Apache License, Version 2.0 - http://www.apache.org/licenses/LICENSE-2.0"""
```

**Step 2 — Create model:**

```bash
ollama create agenthire-extractor -f Modelfile
```

**Step 3 — Query:**

```bash
curl http://localhost:11434/api/generate \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "model": "agenthire-extractor",
    "format": "json",
    "stream": false,
    "prompt": "<resume text here>"
  }'
```

> Always apply brace-counting extraction on the response value — see Python helper below.

---

### Python (transformers)

```python
import json
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

model_name = "nimendraai/NuExtract-tiny-Resume-Data-Extractor"
model = AutoModelForCausalLM.from_pretrained(
    model_name, torch_dtype=torch.bfloat16, trust_remote_code=True
).eval().cuda()
tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)

TEMPLATE = json.dumps({
    "name": "", "email": "", "phone": "", "website": "",
    "skills": [""],
    "experience": [{"title": "", "company": "", "duration": ""}],
    "education":  [{"degree": "", "institution": "", "year": ""}],
    "other_details": [""],
}, indent=4)

def extract_first_json(text):
    depth, start = 0, None
    for i, ch in enumerate(text):
        if ch == "{":
            if start is None: start = i
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start is not None:
                return text[start:i+1]
    return text

def extract(resume_text: str) -> dict:
    prompt = (
        "<|input|>\n"
        f"### Template:\n{TEMPLATE}\n"
        f"### Text:\n{resume_text}\n\n"
        "<|output|>"
    )
    inputs = tokenizer(
        prompt, return_tensors="pt", truncation=True, max_length=2048
    ).to(model.device)
    with torch.no_grad():
        out = model.generate(
            **inputs, max_new_tokens=512, do_sample=False
        )
    decoded = tokenizer.decode(out[0], skip_special_tokens=True)
    raw = decoded.split("<|output|>")[-1].strip()
    return json.loads(extract_first_json(raw))
```

---

### LangChain

```python
from langchain_ollama import OllamaLLM
from pydantic import BaseModel, Field
from typing import Optional
import json

class Experience(BaseModel):
    title: str = Field(default="")
    company: str = Field(default="")
    duration: str = Field(default="")

class Education(BaseModel):
    degree: str = Field(default="")
    institution: str = Field(default="")
    year: str = Field(default="")

class ResumeExtraction(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    skills: list[str] = Field(default_factory=list)
    experience: list[Experience] = Field(default_factory=list)
    education: list[Education] = Field(default_factory=list)
    other_details: list[str] = Field(default_factory=list)

def extract_first_json(text):
    depth, start = 0, None
    for i, ch in enumerate(text):
        if ch == "{":
            if start is None: start = i
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start is not None:
                return text[start:i+1]
    return text

llm = OllamaLLM(model="agenthire-extractor", format="json", temperature=0)

def extract_resume(text: str) -> ResumeExtraction:
    raw = llm.invoke(text)
    return ResumeExtraction(**json.loads(extract_first_json(raw)))

# Batch processing
resumes = [resume_1, resume_2, resume_3]
results = [
    ResumeExtraction(**json.loads(extract_first_json(r)))
    for r in llm.batch(resumes)
]

# Pipeline with scoring
from langchain_core.prompts import PromptTemplate
from langchain_ollama import OllamaLLM as ScoreLLM

scoring_prompt = PromptTemplate.from_template(
    "Job: {job_description}\n\nCandidate: {candidate}\n\n"
    "Score 1-10 and explain."
)
scorer = ScoreLLM(model="llama3", temperature=0.3)

def process_application(resume_text, job_description):
    candidate = extract_resume(resume_text).model_dump()
    evaluation = (scoring_prompt | scorer).invoke({
        "job_description": job_description,
        "candidate": json.dumps(candidate, indent=2),
    })
    return {"candidate": candidate, "evaluation": evaluation}
```

---

## Important Notes

**Always use brace-counting extraction** on raw model output before `json.loads()`.
The model occasionally appends a small amount of text after the closing `}`. Parsing
the raw string directly will raise `JSONDecodeError: Extra data`.

```python
def extract_first_json(text):
    depth, start = 0, None
    for i, ch in enumerate(text):
        if ch == "{":
            if start is None: start = i
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start is not None:
                return text[start:i+1]
    return text

result = json.loads(extract_first_json(raw_output))
```

**Do not call the raw HuggingFace model directly via Ollama** (`hf.co/nimendraai/...`)
without a Modelfile. The NuExtract `<|input|> / ### Template: / ### Text:` prompt
format must be applied — the Modelfile `TEMPLATE` block handles this automatically.

**Skill capitalisation** is normalised via `.title()` during training, so `FastAPI`
may appear as `Fastapi` in output. Apply a canonical map in post-processing if needed.

---

## Limitations

- Trained on **synthetic** English resumes — real-world resumes with unusual layouts
  may produce lower accuracy. Fine-tuning on 30+ real examples will improve results.
- Skills are extracted with light normalisation — canonical casing (FastAPI vs Fastapi)
  requires a post-processing map.
- Phone numbers are extracted as-is without E.164 normalisation.
- Best suited for English resumes. Some multilingual capability exists from the
  Qwen2.5 backbone but was not tested.

---

## Citation

If you use this model, please also cite the original NuExtract work:

```bibtex
@misc{nuextract2024,
  author = {NuMind},
  title  = {NuExtract: A Foundation Model for Structured Extraction},
  year   = {2024},
  url    = {https://numind.ai/blog/nuextract-a-foundation-model-for-structured-extraction}
}
```

---

## License

MIT — same as the base model [`numind/NuExtract-tiny-v1.5`](https://huggingface.co/numind/NuExtract-1.5-tiny).

---
This was trained 2x faster with [Unsloth](https://github.com/unslothai/unsloth)
[<img src="https://raw.githubusercontent.com/unslothai/unsloth/main/images/unsloth%20made%20with%20love.png" width="200"/>](https://github.com/unslothai/unsloth)
