---
license: apache-2.0
base_model: distilbert/distilbert-base-uncased
library_name: transformers.js
pipeline_tag: text-classification
language:
- en
tags:
- onnx
- distilbert
- text-classification
- human-rights
- business-and-human-rights
- hredd
- due-diligence
- supply-chain
- esg
widget:
- text: "Auditors documented withheld wages and confiscated passports at the plant."
  example_title: Forced labour indicators
- text: "Regulators found the factory discharged untreated wastewater into the local river for months."
  example_title: Environmental harm
- text: "The company opened a new distribution centre and hired two hundred warehouse staff."
  example_title: Benign business news
model-index:
- name: llama-hredd-adverse-text-distilbert-onnx
  results:
  - task:
      type: text-classification
      name: HREDD adverse-text harm classification
    dataset:
      name: HREDD 30-case held-out gold set (offline)
      type: hredd-gold-30
    metrics:
    - type: accuracy
      name: Full gold detection (n=30), int8 quantized ONNX
      value: 0.667
    - type: accuracy
      name: Labour detection (n=23), int8 quantized ONNX
      value: 0.652
    - type: accuracy
      name: Environmental detection (n=7), int8 quantized ONNX
      value: 0.714
    - type: recall
      name: Severe-trio Critical recall (n=18), int8 quantized ONNX
      value: 0.556
  - task:
      type: text-classification
      name: HREDD adverse-text harm classification
    dataset:
      name: HREDD 60-case held-out gold set (offline, cohorts g30 and x2026)
      type: hredd-gold-60
    metrics:
    - type: accuracy
      name: Full gold detection (n=60), int8 quantized ONNX
      value: 0.7
    - type: recall
      name: Severe-trio Critical recall (n=31), int8 quantized ONNX
      value: 0.548
    - type: accuracy
      name: Harm-class accuracy (n=50), int8 quantized ONNX
      value: 0.36
    - type: accuracy
      name: Harm-domain accuracy (n=60), int8 quantized ONNX
      value: 0.917
---

# Llama-distilled HREDD adverse-text detector (DistilBERT ONNX student)

A compact, browser-ready text classifier that reads adverse media and allegations and predicts a human-rights or environmental harm category for supplier due-diligence screening. It is the offline student reader of the [risk-screening tool - Supplier diligence · HREDD](https://supplier-risk-model.pages.dev), distilled from a Llama 3.3 70B teacher and int8-quantized to run entirely in the browser, with no API key and no server. On the live demo as currently deployed it performs all batch screening, while single supplier runs go to a hosted teacher behind a same-origin proxy and fall back to this student when that teacher is unavailable. The live teacher has been `qwen/qwen3.8-27b` since 2026-09-17, after Groq decommissioned `qwen/qwen3.6-27b` (the live teacher from 2026-08-15) on 2026-09-14; the training teacher named above (Llama 3.3 70B) is permanent history baked into these weights and does not change with it.

> **Screening aid, not a verdict.** This model helps prioritise where human due-diligence attention goes. It does not clear, terminate, or blacklist suppliers, and every High or Critical outcome is reviewed by a person. It approximates its 70B teacher; it does not beat it (see Evaluation below). Built with Llama (see Provenance and licensing below).

**Intended use:** an offline screening-support reader inside a human-reviewed human rights and environmental due diligence workflow, never an automated decision tool.

---

## What it does

- **Input:** a short adverse-text snippet (news headline or allegation, English).
- **Output:** one of 16 classes, a trained subset of the Supplier Risk Screener's 18-category HREDD harm taxonomy:

  - `biodiversity_loss`
  - `child_labour`
  - `deforestation`
  - `discrimination`
  - `fatal_incident`
  - `forced_labour`
  - `freedom_of_association`
  - `gbvh`
  - `hazardous_waste`
  - `none`
  - `osh_nonfatal`
  - `retaliation`
  - `toxic_pollution`
  - `trafficking`
  - `wage_theft`
  - `water_depletion`

  The taxonomy also defines two band-level categories, `elevated` and `limited`, that sit outside the trained head. They are not among this model's possible outputs and can never be emitted by it.
- **Tier:** the risk tier (Low / Medium / High / Critical) is derived downstream by a severity rubric in the screener. The model emits a harm category, not a tier.

## Usage

### transformers.js (primary surface)

```js
import { pipeline } from "@huggingface/transformers";

const detect = await pipeline(
  "text-classification",
  "PSompong/llama-hredd-adverse-text-distilbert-onnx",
  { dtype: "q8" }
);

const out = await detect(
  "Auditors documented withheld wages and confiscated passports at the plant."
);
console.log(out); // e.g. [{ label: "forced_labour", score: 0.91 }]
```

This repository carries only the int8-quantized ONNX graph, at `onnx/model_quantized.onnx`, and `dtype: "q8"` pins resolution to that artefact explicitly. Without it the library selects fp32 outside the browser and requests `onnx/model.onnx`, which this repository does not ship.

### Python (onnxruntime)

```python
from huggingface_hub import hf_hub_download
from transformers import AutoTokenizer
import onnxruntime as ort
import numpy as np
import json

repo_id = "PSompong/llama-hredd-adverse-text-distilbert-onnx"

model_path = hf_hub_download(repo_id=repo_id, filename="onnx/model_quantized.onnx")
label_map_path = hf_hub_download(repo_id=repo_id, filename="label_map.json")

tokenizer = AutoTokenizer.from_pretrained(repo_id)
session = ort.InferenceSession(model_path)

with open(label_map_path, encoding="utf-8") as f:
    labels = json.load(f)  # 16-label list, alphabetical

text = "Auditors documented withheld wages and confiscated passports at the plant."
inputs = tokenizer(text, return_tensors="np")
input_names = {i.name for i in session.get_inputs()}
onnx_inputs = {k: v for k, v in inputs.items() if k in input_names}

logits = session.run(None, onnx_inputs)[0]
predicted_id = int(np.argmax(logits, axis=-1)[0])
print(labels[predicted_id])  # e.g. "forced_labour"
```

The int8-quantized graph lives at `onnx/model_quantized.onnx`; `label_map.json` gives the label order used to map logits back to class names.

## Model details

| Field | Value |
|---|---|
| Base model | distilbert-base-uncased (about 66M params, English) |
| Teacher | Groq Llama 3.3 70B Instruct (`llama-3.3-70b-versatile`). These weights were trained on single-seed teacher labels; the curated real cases have since been relabelled by a five-seed majority vote, which reaches the model at the next retrain |
| Format | ONNX, int8-quantized, about 65 MB (vs about 268 MB full precision) |
| Task | 16-class head over the 18-category HREDD harm taxonomy |
| Tier derivation | Downstream, via the shared severity rubric (outside this model) |
| Random seed | 42 |
| Training | Free Colab T4 GPU, inverse-frequency class weights, macro-F1 model selection |

## Training data

The model was distilled on a 961-row, three-source corpus: 750 synthetic HREDD news snippets, 157 unique targeted synthetic rows (generated from deterministic templates at seed 42, 180 before de-duplication), and 54 de-identified curated real cases, each carrying a generic public descriptor. The evaluation gold set is held out of training entirely, and it has since grown to 60 cases: the 30 added in August 2026 were researched after these weights were trained, so they could not have reached them by any route. Real company names are never used as labels.

Synthetic rows carry the verbatim data marker `[SYNTHETIC NEWS — for portfolio demonstration]`.

**The corpus has since grown; these weights have not.** A second round of curated research (July 2026) took the corpus to 980 rows and the curated real-case slice to 73 rows, and re-labelled every curated row with a five-seed majority vote of the teacher instead of a single sample. A third round (August 2026) added 56 further de-identified real cases, taking the curated slice to 129 rows; its five-seed teacher labelling completed in early August 2026, taking the corpus to 1036 rows, with every curated row persisting the teacher's five raw votes alongside the majority label. The completed corpus carries no `hazardous_waste` rows: that class's merge into `toxic_pollution` (see the Bias section) is already applied at the corpus level. None of those rows have trained anything: they take effect at the next retraining run, and every number on this page describes the weights trained on the 961-row corpus.

## Evaluation

Measured on a held-out gold set of documented real cases, fully offline (no API, no key). Detection means the predicted tier meets or exceeds the gold case's minimum expected tier.

**The gold set doubled in August 2026, from 30 cases to 60, and the two halves are reported separately.** The original 30 cases are kept as a cohort named `g30`, which carries every figure this page has published; those figures are unchanged. The 30 cases added in August form a second cohort, `x2026`, reported further down. The cohorts differ in composition, so their numbers describe different sets and must never be read against each other as a before and after.

**The file in this repository is the int8-quantized graph, so the quantized column is the one that describes what you run here.** Both columns are the same weights in two exports. Confidence intervals are Wilson score intervals at 95%, quoted at three decimals. The table immediately below is the `g30` cohort.

| Stratum | **This repository (int8 quantized)** | Full-precision export (used for the batch tool) |
|---|---|---|
| Labour detection (n=23) | **15/23 (65.2%)**, 95% CI [0.449, 0.812] | 16/23 (69.6%), 95% CI [0.491, 0.844] |
| Environmental detection (n=7) | **5/7 (71.4%)**, 95% CI [0.359, 0.918] | 5/7 (71.4%), 95% CI [0.359, 0.918] |
| Severe-trio Critical recall (n=18) | **10/18 (55.6%)**, 95% CI [0.337, 0.754] | 11/18 (61.1%), 95% CI [0.386, 0.797] |
| Full gold (n=30) | **20/30 (66.7%)**, 95% CI [0.488, 0.808] | 21/30 (70.0%), 95% CI [0.521, 0.833] |

For reference, on the same gold set a bare structured-data baseline with no text reader detects 1 of 23 labour cases and 0 of 18 severe cases, and the 70B teacher this student is distilled from detects 22 of 23 labour, 7 of 7 environmental and 17 of 18 severe.

**The one-case gap between the two exports is a disclosure, not a measured quality difference.** They differ on exactly one gold case, a forced-labour case that the full-precision export rates Critical and the quantized graph rates High after reading it as gender-based violence and harassment. On a 30-case set, with confidence intervals that overlap almost completely, that difference cannot be told apart from chance. It is published because the two exports are not interchangeable case by case, and because a user is entitled to the number for the artifact they are actually running. The metrics block in this repository's metadata reports the quantized figures, matching the artifact this repository serves; the full-precision column above is kept beside them for comparison, and it is the one to read only if you have built the full-precision export yourself.

The student recovers roughly two-thirds of the distance from the bare model to the 70B teacher. Its remaining misses are one-tier-short adjacent-family confusions (for example, `forced_labour` read as `discrimination`, which is still High), not missed harms; every such case still triggers mandatory human review.

### The expanded 60-case set, and two new measures (August 2026)

The gold set now holds 60 cases: the 30 above (`g30`) plus 30 newly researched, de-identified real cases (`x2026`) drawn from public enforcement actions, court records, investigative NGO reporting and documented major incidents. The expansion nearly doubles the severe-trio stratum (18 cases to 31) and nearly triples the environmental stratum (7 to 19), which were the thinnest parts of the old set.

Two measures were added at the same time, because tier detection alone cannot see whether the model named the right harm:

- **Harm-class accuracy:** does the predicted harm category exactly match the documented one? Scored only on the 50 cases whose gold category names a specific harm, since the 10 cases documented as broadly severe labour harm have no exact counterpart in this model's 16-class vocabulary.
- **Harm-domain accuracy:** does the prediction at least land in the right broad area, labour or environmental? Scored on all 60.

| Stratum | **This repository (int8), all 60** | `g30` (30) | `x2026` (30) |
|---|---|---|---|
| Full gold detection | **42/60 (70.0%)**, [0.575, 0.801] | 20/30, [0.488, 0.808] | 22/30, [0.556, 0.858] |
| Labour detection | 26/41, [0.481, 0.764] | 15/23, [0.449, 0.812] | 11/18, [0.386, 0.797] |
| Environmental detection | 16/19, [0.624, 0.945] | 5/7, [0.359, 0.918] | 11/12, [0.646, 0.985] |
| Severe-trio Critical recall | **17/31**, [0.378, 0.708] | 10/18, [0.337, 0.754] | 7/13, [0.291, 0.768] |
| Harm-class accuracy | **18/50**, [0.241, 0.499] | 10/25, [0.234, 0.593] | 8/25, [0.172, 0.516] |
| Harm-domain accuracy | **55/60**, [0.819, 0.964] | 27/30, [0.744, 0.965] | 28/30, [0.787, 0.982] |

On the same 60 cases the full-precision export scores 43/60 detection, 18/31 severe-trio Critical recall, 18/50 harm-class and 56/60 harm-domain.

**The two new measures are the most useful thing on this page.** The model places the harm in the right broad area 55 times out of 60, and names the exact harm 18 times out of 50. It usually knows whether it is reading a labour problem or an environmental one, and it frequently picks the wrong specific harm inside that area. Because the harm category is what a reviewer reads, and what remediation guidance keys off, treat the category as a pointer for a person to check rather than as a finding. Cases reaching High or Critical go to mandatory human review in any event.

The `g30` column reproduces the published figures exactly, which is the reason for keeping it: the weights, the `g30` texts and the scoring code are all unchanged, so it is a check that nothing drifted rather than a result.

### An attempt to improve this artifact, and why it was dropped

The int8 graph served here is produced by dynamic quantization. In August 2026 two statically calibrated alternatives were built and measured on the same 60 cases, to see whether a better recipe could recover the single case the quantized export loses against full precision. Both were rejected. They scored higher on tier detection, one of them at 60 of 60, while their predictions collapsed onto a handful of severe classes at near-uniform confidence: they were rating almost everything Critical rather than reading the text. Harm-class accuracy fell from 18/50 to 4/50 and 5/50, and neither could classify a benign control sentence. Nothing was promoted and the artifact served here is unchanged. This is the clearest argument for the two new measures: judged on tier detection alone, one of the rejected builds would have looked like the strongest model this project has ever measured.

### Two benign-floor batteries and a reviewer queue (September 2026)

**Weights unchanged.** These are measurements of the artifact served here, added so that anyone running it knows how it behaves on text that is benign but uses harm vocabulary.

**Benign battery.** 300 real corporate self-description sentences from the `mila-ai4h/AIMS.au` dataset (Australian modern slavery statements, CC BY 4.0), kept only where every annotation flag is a self-description flag (reporting entity, structure, operations, supply chains), with signature lines dropped, company names replaced by generic placeholders and registration numbers redacted. Sentences flagged High or Critical are false positives at the mandatory-review threshold.

| Artifact | Flagged High or Critical | Flagged Critical |
|---|---|---|
| **This repository (int8 quantized)** | **7/300 (2.3%)**, 95% CI [0.011, 0.047] | 1/300 |
| Full-precision export | 7/300 (2.3%), 95% CI [0.011, 0.047] | 0/300 |

Plain corporate disclosure text is read as benign almost always. The one int8 Critical is a sentence naming a geographic region with no adverse content at all, a quantization-sensitive calibration slip rather than a reading of harm. Two earlier variants of this battery (unmasked, and masked without the signature-line rule) measured between 7 and 13 flagged rows per 300; the parent repository records all three.

**Counterfactual pairs.** 14 pairs, one per trained harm class, in which the benign side reuses the adverse side's industry vocabulary to describe a remediated, compliant or prevented state (for example recruitment fees reimbursed and passports returned, a wastewater plant commissioned and monitored, a union agreement signed). The pairs were written and committed before any scoring code existed. A benign side passes only if the model answers `none`. That pass rule predates the project's 2026-09-16 labelling policy, described below, so the benign-side count is now reported for information.

| Reader | Adverse side detected | Benign side passes | Both sides right |
|---|---|---|---|
| **This repository (int8 quantized)** | 11/14 | **2/14** | 2/14 |
| Full-precision export | 11/14 | 1/14 | 1/14 |
| Teacher-class model (Groq `qwen/qwen3.6-27b`, three seeds, 2026-09-12), for reference | 14/14 | 12/14 | 12/14 |

**This is the most important limitation on this page for a user of the model.** On remediated or compliant text the student almost always still names a harm: it reads only 1 of the 14 benign sides as `none` in full precision and 2 in this repository's quantized form. A teacher-class language model reading the same pairs passed 12 of 14 benign sides, so this reading is the student's own and not inherited from its labels. How to act on it depends on what the text says. If it describes a harm that was documented and later fixed, such as placement fees reimbursed to migrant workers, a High or Critical answer is what the project now intends: under the owner's 2026-09-16 policy for training labels, a fixed and verified harm keeps its harm label, so the case still reaches the human review where the remediation evidence is weighed. The class it names can still be wrong (it reads that reimbursement as retaliation rather than forced labour), so check the class as well as the tier. If the text only states a policy, a commitment or a compliant state and describes no harm, such as a signed union neutrality agreement, which it reads as a freedom of association harm, or a ban on bonded labour, treat a High or Critical answer as a probable false positive. Either way, keep the human review that the parent screener requires on every High or Critical result.

**Reviewer queue.** From 787 corporate risk and mitigation sentences containing harm vocabulary, the model placed 90 at High or Critical; the 40 most confident, such as a policy line stating that harassment is not tolerated, or that employees are free to join a union, form a queue awaiting a human reviewer's verdicts. Nothing in that queue has trained anything.

## Bias, risks and coverage

- **Negation and remediation insensitivity (measured September 2026):** the model keys on harm vocabulary and setting more than on what the sentence says happened. On 14 remediated or compliant counterparts of adverse texts it passes only 1 or 2, and it flags policy commitments such as a ban on bonded labour as if they were the harm. Under the project's 2026-09-16 labelling policy a counterpart that describes a fixed harm is expected to keep its harm class, so only its readings of policy and compliance text count as false positives, while a fixed harm read under the wrong class is still a class error. See the September batteries under Evaluation.
- **Single-teacher-family bias:** all labels come from one model family (Llama 3.3); its systematic errors transfer to the student.
- **English only** (`distilbert-base-uncased`). Non-English allegations are invisible to this model.
- **Coverage asymmetry:** English-language adverse media under-reports exactly the opaque, low-press-freedom jurisdictions where risk can be highest; silence is not safety. The parent screener carries a dedicated opacity signal for this reason, and treats absence of evidence as an information problem, not clearance.
- **Template-overfit risk** from the synthetic training rows. This is now measured rather than suspected: the teacher agreed with the template's intended category on **157 of 157** template-generated rows, a perfect score that no other part of the corpus approaches (across the 73 curated real cases in the current corpus it disagrees with the researcher's annotation 12 times). Template text is measurably easier than real text, so the student's training signal is cleanest exactly where the language is most artificial. Treat strong performance on template-like phrasing as weak evidence about real reporting.
- **One harm class has no real-text supervision.** Every `hazardous_waste` row in the corpus comes from a template. A second round of curated research wrote seven real cases for that class, including one reworded specifically to foreground waste handling rather than a discharge stream, and the teacher labelled all seven `toxic_pollution` instead. The teacher separates the two classes on template text and collapses them on real case text. The collapse runs toward the more severe class, so it raises rather than lowers the tier, but the boundary between the two remains untaught on real prose and the harm category shown to a reviewer can be the wrong one. This is single-teacher-family bias measured rather than assumed, and writing more curated examples against the same teacher will not fix it.

  **Retested against a second model family in August 2026: it is not a quirk of one teacher.** Those same seven real cases were relabelled by a non-Llama model on the same hosting platform, using an identical prompt, the same five seeds and the same temperature. It also answered `toxic_pollution` on all seven, while getting four of five toxic-pollution control cases right. Carry one caveat whenever this result is cited: the only non-Llama model available for the test is far smaller than the 70B teacher and is not its peer, so this is a caution rather than a verdict. What it does rule out is the cheap fix. Swapping teachers, or writing yet more curated examples, will not teach this boundary; the lever is the taxonomy or the prompt definitions themselves.

  **That lever has since been chosen, and it matters if you depend on this class.** The decided resolution is to stop training a class no teacher can supervise: at the next retrain `hazardous_waste` is merged into `toxic_pollution`, so a future version of this model will not emit it, and waste-handling text will be reported as toxic pollution, one severity band higher. That retrain is gated. Three time-boxed, owner-authorized windows ran in August and September 2026; in each, one candidate was trained and measured against promotion criteria registered in advance, none met every criterion, and none was released, so nothing in this repository changed. The model in this repository still emits `hazardous_waste`, with exactly the boundary problem described above, and the label stays valid in the parent project's severity rubric either way.
- **Cross-language behaviour** was audited separately in the parent project, and that audit covers the 70B teacher reader rather than this student: it found no detection gap across Thai, Vietnamese, Chinese and Bahasa Indonesia on translated text from a representative slice of the gold set, and redirected the open problem to collecting non-English coverage in the first place. It does not transfer to this model, which is English only.

## Limitations and out-of-scope use

This model approximates its teacher; it does not beat it. The distillation trades some accuracy for offline reproducibility (no API, no key, no server).

Out of scope:
- Supplier termination decisions.
- Worker-level scoring.
- Production HREDD screening without human review.
- Out-of-domain text: financial, medical, or legal documents.

## Provenance and licensing

- **Weights:** a fine-tuned DistilBERT student (Apache-2.0 base model). This derivative is released under Apache-2.0.
- **Built with Llama:** the training labels were generated by Meta Llama 3.3 70B. Use of those labels is subject to the Llama 3.3 Community License.
- **Naming:** this repository was renamed from `PSompong/hredd-adverse-text-distilbert-onnx` to carry "Llama" at the start of the model name, as the Llama 3.3 Community License requires for models trained on Llama outputs. The old id redirects here.
- Synthetic rows are marked as demonstration data; curated real cases are de-identified.
- Portfolio and methodology artefact; not legal advice and not a certification of any supplier.

## Version history

- Card revised 2026-09-23: **no version bump, because nothing about the model changed.** On 2026-09-23 the site's live teacher behind the hosted single-run proxy (introduction, above) moved to a severity-first prompt that returns a harm category as well as a tier, and the page now keeps the higher of the model's tier and the tier the severity rubric gives that harm. The live-reader decision-quality gate, registered again for this setup and run before it went live, read all 30 original gold cases at High or Critical with that rubric floor applied. The three environmental cases that the 2026-09-17 entry below describes at Medium now read High or Critical on the model's own tier, before any floor; the floor raised four labour cases, three from High to Critical and one from Medium to High. On the benign sides of the 14 counterfactual pairs (Evaluation, above), which describe a remediated, compliant or prevented state, the teacher still named the pair's harm on 2, and the floor kept both at High or Critical; 11 read as clean; on the remaining text one of the three replies left out its tier, which on the site sends the read to the offline student. All of this describes the live teacher on the demo site, not the student model this card describes: the training teacher for these weights stays Llama 3.3 70B, and every published number, artifact and file in this repository is unchanged.
- Card revised 2026-09-17: **no version bump, because nothing about the model changed.** Groq decommissioned `qwen/qwen3.6-27b` on 2026-09-14. On 2026-09-17 the owner moved the live teacher behind the hosted single-run proxy (introduction, above) to `qwen/qwen3.8-27b`, the model that already served corpus work (see the 2026-09-16 entry below). It met every acceptance gate except the live-reader decision-quality gate, and the owner accepted that gap for the live demo. In that gate's five-seed run on the 30 original gold cases (2026-09-14), it read all 23 labour cases at High or Critical and three environmental cases (biodiversity loss, water depletion and hazardous waste) at Medium, one band below the High the previous live teacher gave the same three; 27 of 30 cases reached High or above, against 30 of 30 for that teacher. For a demo user, text describing harms like those three can come back Medium from the live teacher, below the High and Critical tiers that trigger mandatory human review. This was addressed on 2026-09-23 (see the entry above). This is a live-deployment change only: the training teacher for these weights stays Llama 3.3 70B, and every published number, artifact and file in this repository is unchanged.
- Card revised 2026-09-16: **no version bump, because nothing about the model changed.** The distillation-corpus teacher used to label and verify new corpus rows split from the live reader teacher; `qwen/qwen3.8-27b` serves corpus work since 2026-09-14, accepted after passing every acceptance gate except the live-reader decision-quality gate. The live single-run reader described in the introduction above, and the teacher these shipped weights were trained on (Llama 3.3 70B), are both unaffected. The owner also set a remediation policy for future corpus labelling, under which a fixed and verified harm keeps its harm label and documented harm stays flagged for human review even when the text reports remediation. In the retrain window `retrain-v0.5`, one candidate was trained on a 1249-row corpus and measured once against criteria registered before any candidate existed. It did not meet two of them, harm-class accuracy on the full-precision export (32 of 50 against a bar of 34) and harm-domain accuracy on both exports (50 and 49 of 60 against a floor of 55). Its benign-text results were the best so far (0 of 300 corporate disclosure sentences flagged High or Critical), but it also detected fewer gold rows than the previous candidate (51 and 49 of 60 against 57), and eight gold texts that the shipped weights flag for human review read as no harm under it (nine on the quantized export), all but two of them forced labour. It was not released. The counterfactual-pair limitation now separates two kinds of text: a report of a documented harm that was later fixed, which that policy deliberately keeps under its harm class so that it reaches human review, and a policy or compliance statement that describes no harm, where a High or Critical answer remains a probable false positive. The teacher reference row in that table now names its model and date. Every published number, artifact and file in this repository is unchanged.
- Card revised 2026-09-12: **no version bump, because nothing about the model changed.** The September retrain window `retrain-v0.4` ran: one candidate was trained and measured once against the pre-registered criteria, and did not meet two of them as registered (the Critical count, 47 of 60 gold rows against a cap of 40, of which 41 sit on rows whose gold minimum is Critical, a cap the review found sits below the gold set's own Critical floor and will be re-registered; and the counterfactual benign side, which barely moved), alongside real gains elsewhere (a perfect 31 of 31 severe-trio Critical-recall, better harm-class accuracy, and a benign-mass false-positive rate that fell from 7 of 300 to 1 of 300). It was not released. Every published number above this note, and every file in this repository, is unchanged.
- Card revised 2026-09-12: **no version bump, because nothing about the model changed.** Two benign-floor batteries are published for the served artifact: 300 masked real corporate disclosure sentences (7 of 300 flagged High or Critical) and 14 adverse-versus-remediated pairs (the benign side passes on 2 of 14, against 12 of 14 for a teacher-class model), plus a 40-sentence reviewer queue of the model's own false positives. Criteria for a next retrain window that include these batteries are being registered ahead of any candidate; no candidate exists and nothing shipped. Every published number above this note, and every file in this repository, is unchanged.
- **v0.2.3** (2026-08-04): **weights unchanged**; an evaluation update. The held-out gold set doubles from 30 documented cases to 60, with the original 30 preserved as the `g30` cohort so every previously published figure stays comparable and unchanged. Two explanation measures are published for the first time (harm-class and harm-domain accuracy), and they carry the finding that the model is far better at the broad area of harm than at the specific harm. A statically quantized replacement for the artifact served here was built, measured and rejected as degenerate. The missing real-text supervision for one harm class was retested against a second model family and reproduced. Nothing was promoted; no served artifact changed.
- **v0.2.2** (2026-07-29): **weights unchanged**; an evaluation and training-data documentation update. The quantized artifact in this repository is now measured on the gold set in its own right instead of inheriting the full-precision numbers, every stratum is quoted with a 95% confidence interval, the training corpus is documented at its current 980 rows with five-seed curated labels, and the bias section gains two measured findings (template separability, and the missing real-text supervision for one harm class).
- **v0.2** (2026-07-04): corpus widened to 961 rows across three sources; 16-class head; offline gains on the held-out gold set (labour 10 to 16 of 23; environmental 1 to 5 of 7; severe-trio Critical recall 8 to 11 of 18).
- **v0.1** (June 2026): initial distillation.
- Card revised 2026-08-15: **no version bump, because nothing about the model changed.** The live Groq teacher behind the hosted single-run proxy (introduction, above) migrated to `qwen/qwen3.6-27b`, Groq's measured bake-off replacement, on 2026-08-15; Groq decommissioned the prior model `llama-3.3-70b-versatile` on 2026-08-16. This is a live-deployment change only: the training teacher for these weights stays Llama 3.3 70B, and every published number, artifact and file in this repository is unchanged.
- Card revised 2026-08-08: **no version bump, because nothing about the model changed.** The August 2026 retrain window closed: its one candidate was measured against pre-registered promotion criteria and did not meet them on severity calibration (it over-flags benign text), alongside sharply better harm-class explanations, so it was not released; every published number, artifact and file in this repository is unchanged.
- Card revised 2026-08-07: **no version bump, because nothing about the model changed.** The third curated round's labelling is complete (corpus 1036 rows; each curated row persists its five teacher votes), and a time-boxed, owner-authorized window for one staged retrain is open. The retrain has not happened; every published number, artifact and file in this repository is unchanged.
- Card revised 2026-08-05: **no version bump, because nothing about the model changed.** The training-data section now names the third curated round (129 curated real cases, labelling in progress), and the hazardous-waste limitation records the decided resolution: that class is merged into `toxic_pollution` at the next retrain, which is gated and has not happened. Every published number, artifact and file in this repository is unchanged.
- Card revised 2026-07-30: the usage snippet pins `dtype: "q8"` so it also works outside the browser, and the introduction states the model's current role on the live demo (batch reader, and single-run fallback beside a hosted teacher).
- Card revised 2026-07-17: 16-class head correction, new Bias, risks and coverage section, rename note.

## Links

- Live demo: <https://supplier-risk-model.pages.dev>
- AI governance page: <https://supplier-risk-model.pages.dev/#/governance>
- Remedy and engagement page (V2): <https://supplier-risk-model.pages.dev/#/remedy>

## Citation

```bibtex
@software{sompong2026llamahredd,
  author = {Sompong, P.},
  title  = {Llama-distilled HREDD adverse-text detector (DistilBERT ONNX student)},
  year   = {2026},
  url    = {https://huggingface.co/PSompong/llama-hredd-adverse-text-distilbert-onnx}
}
```
