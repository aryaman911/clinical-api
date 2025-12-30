# Clinical NLP Datasets for Fine-Tuning

This document provides links to publicly available datasets for training the clinical component identification model.

## 🔗 Quick Download Links

### 1. MTSamples Medical Transcriptions (Recommended - Easy Start)

**Direct Download:**
```bash
# Download directly
curl -o mtsamples.csv https://raw.githubusercontent.com/salgadev/medical-nlp/master/mtsamples.csv
```

**Kaggle Version:**
- URL: https://www.kaggle.com/datasets/tboyle10/medicaltranscriptions
- Size: ~5,000 samples
- Format: CSV
- Contents: Medical specialty, sample name, transcription, keywords

### 2. Clinical Stopwords & Vocabulary

```bash
# Clinical stopwords
curl -o clinical-stopwords.txt https://raw.githubusercontent.com/salgadev/medical-nlp/master/clinical-stopwords.txt

# Medical vocabulary
curl -o vocab.txt https://raw.githubusercontent.com/salgadev/medical-nlp/master/vocab.txt
```

### 3. ClinicalTrials.gov Data

**API Access:**
```bash
# Search clinical trials
curl "https://clinicaltrials.gov/api/v2/studies?query.term=cancer&pageSize=10"
```

**Bulk Download:**
- URL: https://clinicaltrials.gov/AllPublicXML.zip
- Size: ~3 GB
- Format: XML files

### 4. n2c2 NLP Research Data Sets (Requires DUA)

- URL: https://portal.dbmi.hms.harvard.edu/projects/n2c2-nlp/
- Registration: Required (free for research)
- Contains:
  - 2006: De-identification & Smoking status
  - 2008: Obesity recognition
  - 2009: Medication extraction
  - 2010: Relations extraction
  - 2011: Coreference resolution
  - 2012: Temporal relations
  - 2018: Clinical trial cohort selection

### 5. MIMIC-III Clinical Database (Requires Certification)

- URL: https://physionet.org/content/mimiciii/
- Requirements:
  1. Complete CITI training
  2. Sign data use agreement
  3. Get credentialed on PhysioNet
- Contains: ICU patient records, clinical notes, lab results

### 6. PRO-ACT ALS Clinical Trial Data

- URL: https://ncri1.partners.org/ProACT
- Size: 10,700+ patient records
- Contains: Data from 23 Phase II/III clinical trials

---

## 📊 Dataset Format for Fine-Tuning

After downloading, convert your data to this JSONL format:

```json
{"messages": [
  {"role": "system", "content": "You are an expert at identifying reusable components in clinical documents..."},
  {"role": "user", "content": "Identify components in this text:\n\n[CLINICAL TEXT HERE]"},
  {"role": "assistant", "content": "[{\"type\": \"boilerplate\", \"title\": \"...\", \"text\": \"...\", \"confidence\": 0.95, \"reuse_potential\": \"high\", \"rationale\": \"...\"}]"}
]}
```

---

## 🛠️ Processing Scripts

Use the provided `prepare_data.py` script:

```bash
# Process MTSamples CSV
python prepare_data.py --input mtsamples.csv --output data/

# Process a directory of text files
python prepare_data.py --input ./clinical_docs/ --output data/

# Generate only synthetic training data
python prepare_data.py --synthetic-only --output data/
```

---

## ⚠️ Important Notes

1. **Data Use Agreements**: Many clinical datasets require signing a DUA. Never share this data publicly.

2. **De-identification**: Ensure all data is properly de-identified before use.

3. **Quality over Quantity**: 500 high-quality, manually verified examples are better than 5000 auto-labeled ones.

4. **Balanced Training**: Include examples of all component types:
   - Boilerplate (~20%)
   - Definitions (~20%)
   - Study Sections (~20%)
   - Drug Info (~15%)
   - Safety (~15%)
   - Procedures (~10%)

5. **Validation Set**: Always keep 10-20% of data for validation.

---

## 📈 Recommended Training Data Sizes

| Accuracy Target | Training Examples | Est. Cost |
|-----------------|-------------------|-----------|
| 75-80%          | 50-100            | ~$0.10    |
| 85-90%          | 200-500           | ~$0.30    |
| 90-95%          | 500-1000          | ~$0.75    |
| 95%+            | 1000+             | ~$1.50+   |

---

## 🔄 Iterative Improvement

1. Start with synthetic data + 100 real examples
2. Fine-tune and evaluate
3. Identify failure cases
4. Add targeted training examples for failures
5. Re-fine-tune
6. Repeat until target accuracy is reached
