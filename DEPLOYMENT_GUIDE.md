# 🚀 Complete Deployment Guide

This guide walks you through deploying the Clinical Component Identifier from start to finish.

## Prerequisites

- [ ] GitHub account
- [ ] OpenAI account with API key (https://platform.openai.com/api-keys)
- [ ] Render account (https://render.com)
- [ ] Node.js 18+ installed
- [ ] Python 3.9+ installed
- [ ] Git installed

---

## Part 1: Fine-Tune the OpenAI Model

### Step 1.1: Set Up Your Environment

```bash
# Clone or copy the project
cd clinical-component-identifier/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set your OpenAI API key
export OPENAI_API_KEY="sk-your-api-key-here"
```

### Step 1.2: Prepare Training Data

**Option A: Use synthetic data (quick start)**
```bash
python prepare_data.py --synthetic-only --output data/
```

**Option B: Use real clinical data**
```bash
# Download MTSamples
curl -o mtsamples.csv https://raw.githubusercontent.com/salgadev/medical-nlp/master/mtsamples.csv

# Process it
python prepare_data.py --input mtsamples.csv --output data/
```

### Step 1.3: Start Fine-Tuning

```bash
python fine_tune.py
```

This will:
1. Validate your training data
2. Upload files to OpenAI
3. Create a fine-tuning job
4. Wait for completion (1-3 hours)
5. Output your model ID

**Expected output:**
```
🎉 Fine-Tuning Complete!
Your fine-tuned model ID: ft:gpt-4o-mini-2024-07-18:your-org:clinical-components:abc123
```

### Step 1.4: Save Your Model ID

```bash
# The model ID is also saved to fine_tuned_model.txt
cat fine_tuned_model.txt
```

**⚠️ Keep this ID safe - you'll need it for deployment!**

---

## Part 2: Deploy Backend to Render

### Step 2.1: Create GitHub Repository

```bash
cd backend

# Initialize git
git init
git add .
git commit -m "Initial commit - Clinical API backend"

# Create repo on GitHub (https://github.com/new)
# Name it: clinical-api

# Push to GitHub
git remote add origin https://github.com/YOUR_USERNAME/clinical-api.git
git branch -M main
git push -u origin main
```

### Step 2.2: Deploy on Render

1. **Go to Render Dashboard**: https://dashboard.render.com

2. **Create New Web Service**:
   - Click "New +" → "Web Service"
   - Select "Build and deploy from a Git repository"
   - Connect your GitHub account if not already connected
   - Select the `clinical-api` repository

3. **Configure the Service**:
   ```
   Name: clinical-api
   Region: Oregon (US West) or closest to you
   Branch: main
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: gunicorn app:app
   Instance Type: Free
   ```

4. **Add Environment Variables**:
   Click "Advanced" → "Add Environment Variable"
   
   | Key | Value |
   |-----|-------|
   | `OPENAI_API_KEY` | `sk-your-actual-api-key` |
   | `FINE_TUNED_MODEL` | `ft:gpt-4o-mini-2024-07-18:org:clinical:xxx` |
   | `PYTHON_VERSION` | `3.11.0` |

5. **Create Web Service**: Click "Create Web Service"

6. **Wait for Deployment** (~3-5 minutes)

7. **Get Your API URL**: 
   - It will be something like: `https://clinical-api.onrender.com`
   - Test it: `curl https://clinical-api.onrender.com`

### Step 2.3: Test the API

```bash
curl -X POST https://clinical-api.onrender.com/api/identify \
  -H "Content-Type: application/json" \
  -d '{"text": "This study follows GCP guidelines."}'
```

---

## Part 3: Deploy Frontend to GitHub Pages

### Step 3.1: Update API URL

Edit `frontend/src/App.jsx`:

```javascript
// Line ~15 - Update this URL
const API_URL = 'https://clinical-api.onrender.com';  // Your Render URL
```

### Step 3.2: Update Package.json

Edit `frontend/package.json`:

```json
{
  "homepage": "https://YOUR_USERNAME.github.io/clinical-ui",
  ...
}
```

### Step 3.3: Update Vite Config

Edit `frontend/vite.config.js`:

```javascript
export default defineConfig({
  plugins: [react()],
  base: '/clinical-ui/',  // Must match your repo name
  ...
})
```

### Step 3.4: Create GitHub Repository

```bash
cd frontend

# Initialize git
git init
git add .
git commit -m "Initial commit - Clinical UI frontend"

# Create repo on GitHub (https://github.com/new)
# Name it: clinical-ui

# Push to GitHub
git remote add origin https://github.com/YOUR_USERNAME/clinical-ui.git
git branch -M main
git push -u origin main
```

### Step 3.5: Install Dependencies & Deploy

```bash
# Install dependencies
npm install

# Build and deploy to GitHub Pages
npm run deploy
```

### Step 3.6: Enable GitHub Pages

1. Go to your repository: `https://github.com/YOUR_USERNAME/clinical-ui`
2. Click "Settings" tab
3. Scroll to "Pages" in the sidebar
4. Under "Source", select:
   - Branch: `gh-pages`
   - Folder: `/ (root)`
5. Click "Save"

### Step 3.7: Access Your Site

After 1-2 minutes, your site will be live at:
```
https://YOUR_USERNAME.github.io/clinical-ui
```

---

## Part 4: Troubleshooting

### CORS Errors

If you see CORS errors in the browser console:

1. **Update Flask CORS in `backend/app.py`**:
```python
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "https://YOUR_USERNAME.github.io",
            "http://localhost:3000"
        ]
    }
})
```

2. **Commit and push to trigger Render redeploy**

### Render Service Sleeping

Free Render services sleep after 15 minutes of inactivity:
- First request after sleep takes ~30 seconds
- Upgrade to paid tier for always-on

### 404 on GitHub Pages Refresh

Add a `404.html` file that redirects to `index.html`:

```bash
# In frontend/public/
cp index.html 404.html
```

### API Key Issues

- Never commit API keys to GitHub
- Always use environment variables
- Regenerate keys if exposed

---

## Part 5: Updating Your Deployment

### Update Backend

```bash
cd backend
git add .
git commit -m "Update backend"
git push origin main
# Render auto-deploys on push
```

### Update Frontend

```bash
cd frontend
git add .
git commit -m "Update frontend"
git push origin main
npm run deploy  # Deploys to gh-pages branch
```

### Update Fine-Tuned Model

1. Create new training data
2. Run `python fine_tune.py`
3. Get new model ID
4. Update `FINE_TUNED_MODEL` in Render dashboard
5. Render will redeploy automatically

---

## Summary Checklist

- [ ] OpenAI API key created
- [ ] Training data prepared
- [ ] Model fine-tuned
- [ ] Model ID saved
- [ ] Backend pushed to GitHub
- [ ] Backend deployed on Render
- [ ] Environment variables set on Render
- [ ] Backend API tested
- [ ] Frontend API_URL updated
- [ ] Frontend pushed to GitHub
- [ ] Frontend deployed to GitHub Pages
- [ ] GitHub Pages enabled
- [ ] Full application tested

🎉 **Congratulations! Your Clinical Component Identifier is now live!**
