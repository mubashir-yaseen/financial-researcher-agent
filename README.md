# Free Financial Researcher Agent

A production-ready Financial Researcher Agent built entirely on **FREE** tools and APIs.

## 🌟 Features
- **Zero API Costs**: Uses OpenRouter's free tier (Gemini 2.0 Flash / Llama 3.2), DuckDuckGo Search, and HuggingFace models.
- **Local Credibility Scoring**: Robust local domain rules and recency evaluation.
- **Semantic Caching**: Local vector store using FAISS & `sentence-transformers` for instant cached responses.
- **Streamlit UI**: Clean, responsive frontend designed for Streamlit Cloud.

## 🚀 Quick Setup

### 1. Local Installation
1. Clone this repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Setup environment variables:
   ```bash
   cp .env.example .env
   # Open .env and add your OPENROUTER_API_KEY
   ```
4. Run locally:
   ```bash
   streamlit run app.py
   ```

---

### 2. 🌍 One-Click Deployment (FREE Streamlit Cloud)

Deploy this app to the public web in 3 minutes for free:

1. **Push to GitHub**: Push this folder to a new GitHub Repository.
2. **Streamlit Cloud**: Go to [share.streamlit.io](https://share.streamlit.io/) and log in.
3. **New App**: Click **New app** -> From existing repository.
4. **Configure**: Select your repo/branch and set **Main file path** to `app.py`.
5. **Secrets**: Click **Advanced Settings** and paste:
   ```toml
   OPENROUTER_API_KEY = "your_key_here"
   LLM_MODEL = "google/gemini-2.0-flash-lite-preview-02-05:free"
   ```
6. **Deploy!**

> [!TIP]
> If you experience "429 Rate Limit" errors, it's due to OpenRouter's free tier limits. Try switching models in your `.env` or Streamlit Secrets (e.g., to Gemini 2.0 Flash Lite).

---

### 3. 🐳 Docker Deployment
```bash
docker build -t researcher-agent .
docker run -p 8501:8501 --env-file .env researcher-agent
```

## Example Query
> *"PSX crash analysis March 2026"*

Output is structurally clean JSON containing key facts, a confidence score, and fully attributed real-time sources!
