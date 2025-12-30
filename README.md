# Clinical Component Identifier - Fine-Tuning with OpenAI

A full-stack application for identifying reusable components in clinical documents using a fine-tuned OpenAI GPT model.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    GitHub Pages (Frontend)                   │
│                 React + Tailwind CSS Application             │
│            https://yourusername.github.io/clinical-ui        │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ API Calls
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Render (Backend)                          │
│                   Flask + Gunicorn API                       │
│          https://clinical-api.onrender.com                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ Fine-tuned Model
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    OpenAI API                                │
│              Fine-tuned GPT-4o-mini Model                    │
│        ft:gpt-4o-mini:your-org:clinical:xxxxx               │
└─────────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
clinical-component-identifier/
├── backend/                    # Flask API (Deploy to Render)
│   ├── app.py                 # Main Flask application
│   ├── fine_tune.py           # Fine-tuning script
│   ├── prepare_data.py        # Data preparation script
│   ├── requirements.txt       # Python dependencies
│   ├── render.yaml            # Render deployment config
│   └── data/
│       ├── training_data.jsonl
│       └── validation_data.jsonl
│
├── frontend/                   # React App (Deploy to GitHub Pages)
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   └── index.css
│   ├── package.json
│   └── vite.config.js
│
├── datasets/                   # Sample datasets & links
│   └── README.md
│
└── README.md                   # This file
```

---

## 📊 STEP 1: Datasets for Fine-Tuning

### Available Clinical NLP Datasets

Since clinical trial protocols are often proprietary, here are publicly available datasets you can use:

#### 1. **Kaggle - Medical Transcriptions** (Recommended for starting)
- **URL**: https://www.kaggle.com/datasets/tboyle10/medicaltranscriptions
- **Size**: ~5,000 medical transcription samples
- **Contains**: Medical specialty, transcription text, keywords
- **Download**: Create Kaggle account → Download CSV

#### 2. **MTSamples Medical Transcriptions**
- **URL**: https://github.com/salgadev/medical-nlp
- **Direct CSV**: https://raw.githubusercontent.com/salgadev/medical-nlp/master/mtsamples.csv
- **Contains**: 40 medical specialties with sample reports

#### 3. **n2c2 NLP Research Data Sets**
- **URL**: https://portal.dbmi.hms.harvard.edu/projects/n2c2-nlp/
- **Note**: Requires data use agreement (DUA)
- **Contains**: Clinical notes from i2b2 challenges

#### 4. **MIMIC-III Clinical Database**
- **URL**: https://physionet.org/content/mimiciii/
- **Note**: Requires credentialing through PhysioNet
- **Contains**: De-identified clinical notes from ICU patients

#### 5. **PRO-ACT ALS Clinical Trial Data**
- **URL**: https://ncri1.partners.org/ProACT
- **Contains**: 10,700+ patient records from 23 Phase II/III trials

### Quick Start - Download MTSamples:

```bash
# Download the medical transcriptions dataset
curl -o mtsamples.csv https://raw.githubusercontent.com/salgadev/medical-nlp/master/mtsamples.csv
```

---

## 🔧 STEP 2: Prepare Training Data

### Understanding OpenAI Fine-Tuning Format

OpenAI requires JSONL format where each line is a conversation:

```json
{"messages": [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]}
```

### Run the Data Preparation Script

```bash
cd backend
python prepare_data.py --input ../datasets/mtsamples.csv --output data/
```

This will create:
- `data/training_data.jsonl` (80% of data)
- `data/validation_data.jsonl` (20% of data)

---

## 🚀 STEP 3: Fine-Tune the Model

### Prerequisites

1. **OpenAI Account with API Access**
   - Sign up: https://platform.openai.com/signup
   - Create API Key: https://platform.openai.com/api-keys
   - **Note**: Fine-tuning requires payment. GPT-4o-mini fine-tuning costs ~$3.00/1M tokens

2. **Set Environment Variable**
   ```bash
   export OPENAI_API_KEY="sk-your-api-key-here"
   ```

### Run Fine-Tuning

```bash
cd backend
pip install openai

# Upload training data and start fine-tuning
python fine_tune.py
```

### Fine-Tuning Process

1. **Upload Files** (~1-2 minutes)
2. **Create Fine-Tuning Job** (~1-3 hours for 500 examples)
3. **Get Model ID** (e.g., `ft:gpt-4o-mini-2024-07-18:your-org:clinical:abc123`)

### Monitor Progress

```python
from openai import OpenAI
client = OpenAI()

# List fine-tuning jobs
jobs = client.fine_tuning.jobs.list(limit=10)
for job in jobs.data:
    print(f"Job: {job.id}, Status: {job.status}, Model: {job.fine_tuned_model}")
```

Or check the dashboard: https://platform.openai.com/finetune

---

## 🖥️ STEP 4: Set Up the Backend (Render)

### 4.1 Create GitHub Repository for Backend

```bash
cd backend
git init
git add .
git commit -m "Initial backend commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/clinical-api.git
git push -u origin main
```

### 4.2 Deploy to Render

1. **Create Render Account**: https://render.com/

2. **Create New Web Service**:
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Configure:
     - **Name**: `clinical-api`
     - **Region**: Choose closest to you
     - **Branch**: `main`
     - **Runtime**: `Python 3`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn app:app`

3. **Add Environment Variables**:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `FINE_TUNED_MODEL`: Your fine-tuned model ID (e.g., `ft:gpt-4o-mini-2024-07-18:org:clinical:xxx`)
   - `PYTHON_VERSION`: `3.11.0`

4. **Deploy**: Click "Create Web Service"

5. **Get Your API URL**: `https://clinical-api.onrender.com`

---

## 🌐 STEP 5: Set Up the Frontend (GitHub Pages)

### 5.1 Create React App

```bash
cd frontend
npm install
```

### 5.2 Update API URL

Edit `src/App.jsx` and update the API_URL:

```javascript
const API_URL = 'https://clinical-api.onrender.com';
```

### 5.3 Create GitHub Repository

```bash
git init
git add .
git commit -m "Initial frontend commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/clinical-ui.git
git push -u origin main
```

### 5.4 Deploy to GitHub Pages

```bash
# Install gh-pages
npm install --save-dev gh-pages

# Deploy
npm run deploy
```

### 5.5 Enable GitHub Pages

1. Go to your repository on GitHub
2. Settings → Pages
3. Source: Select `gh-pages` branch
4. Your site will be live at: `https://YOUR_USERNAME.github.io/clinical-ui`

---

## 🧪 STEP 6: Test the Application

### Test Backend API

```bash
curl -X POST https://clinical-api.onrender.com/api/identify \
  -H "Content-Type: application/json" \
  -d '{"text": "This study will be conducted in accordance with Good Clinical Practice (GCP) as defined by ICH guidelines."}'
```

### Expected Response

```json
{
  "components": [
    {
      "type": "boilerplate",
      "title": "GCP Compliance Statement",
      "text": "This study will be conducted in accordance with Good Clinical Practice (GCP) as defined by ICH guidelines.",
      "confidence": 0.95,
      "reuse_potential": "high"
    }
  ],
  "model_used": "ft:gpt-4o-mini-2024-07-18:org:clinical:xxx"
}
```

---

## 💰 Cost Estimation

### Fine-Tuning Costs (One-time)

| Item | Cost |
|------|------|
| Training (500 examples, ~100K tokens) | ~$0.30 |
| Validation | ~$0.05 |
| **Total Fine-Tuning** | **~$0.35** |

### Usage Costs (Per Request)

| Model | Input | Output |
|-------|-------|--------|
| Fine-tuned GPT-4o-mini | $0.30/1M tokens | $1.20/1M tokens |

### Hosting Costs

| Service | Cost |
|---------|------|
| Render (Free Tier) | $0/month |
| GitHub Pages | $0/month |
| **Total Hosting** | **$0/month** |

---

## 🔒 Security Best Practices

1. **Never commit API keys** - Use environment variables
2. **Add `.env` to `.gitignore`**
3. **Use Render's secret management** for production keys
4. **Enable CORS** only for your frontend domain

---

## 📈 Improving Model Accuracy

### Tips for Better Fine-Tuning Results

1. **More Training Data**: Aim for 500-1000 high-quality examples
2. **Diverse Examples**: Include all component types
3. **Consistent Formatting**: Keep JSON structure identical
4. **Quality over Quantity**: Manually verify 10% of training data
5. **Iterative Improvement**: Fine-tune again with corrected examples

### Monitoring Model Performance

```python
# Evaluate on test set
def evaluate_model(test_file, model_id):
    correct = 0
    total = 0
    
    with open(test_file) as f:
        for line in f:
            data = json.loads(line)
            # Compare model output to expected
            ...
    
    return correct / total
```

---

## 🐛 Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| CORS errors | Add frontend domain to Flask CORS config |
| 404 on GitHub Pages refresh | Use HashRouter in React |
| Render timeout | Upgrade to paid tier or optimize API |
| Fine-tuning failed | Check JSONL format, ensure valid JSON |
| Model not found | Wait for fine-tuning to complete |

### Logs

**Render Logs**: Dashboard → Your Service → Logs
**OpenAI Logs**: https://platform.openai.com/usage

---

## 📚 Resources

- [OpenAI Fine-Tuning Guide](https://platform.openai.com/docs/guides/fine-tuning)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference/fine-tuning)
- [Render Flask Deployment](https://render.com/docs/deploy-flask)
- [GitHub Pages React Deployment](https://github.com/gitname/react-gh-pages)
- [Clinical NLP Resources](https://github.com/EpistasisLab/ClinicalDataSources)

---

## 📄 License

MIT License - Feel free to use and modify for your projects.
