# 🩺 Healthcare Symptom Checker

An AI-powered web app that analyzes user-reported symptoms and provides **educational insights** on possible conditions and next steps.
Built using **Python, Streamlit, FastAPI, SQLite**, and **Google Gemini LLM**.

Author: komal 

---

## 🚀 Features

* 🤖 **LLM-powered diagnosis suggestions** using Google Gemini
* 🧾 **Educational disclaimer** for safe, non-clinical use
* 💾 **SQLite database** to store query history
* 🌐 **Streamlit frontend** + **FastAPI backend**
* 📜 **View saved queries** directly in the app

---

## 🛠️ Tech Stack

| Layer          | Technology                            |
| -------------- | ------------------------------------- |
| Frontend       | Streamlit                             |
| Backend        | FastAPI                               |
| LLM            | Google Gemini (`google-generativeai`) |
| Database       | SQLite                                |
| Env Management | Python-dotenv                         |

---

## ⚙️ Setup

### 1️⃣ Clone the repo

```bash
git clone https://github.com/KomalSaiVulchi/Healthcare_Symptom_Checker.git
cd Healthcare_Symptom_Checker
```

### 2️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Set your API key

Create a `.env` file in the root:

```
GEMINI_API_KEY=your_google_api_key_here
```

### 4️⃣ Run the backend

```bash
cd Backend
uvicorn main:app --reload
```

### 5️⃣ Run the frontend

```bash
streamlit run Frontend/app.py
```

---

## 🎨 Frontend updates

The Streamlit UI in `Frontend/app.py` was recently improved to be more compact and user-friendly:

- a clean form layout with example prompts and quick tips
- a styled result card for clearer output
- logs are shown in a tidy table on the "Database Logs" tab

If you want a different color theme or additional features (file upload, multi-turn follow-up), tell me and I can implement them.

---

## 🧠 API Endpoints

| Endpoint        | Method | Description                           |
| --------------- | ------ | ------------------------------------- |
| `/api/diagnose` | POST   | Generate diagnosis suggestions        |
| `/api/logs`     | GET    | Retrieve stored symptom-response logs |

---

## 🧾 Example Output

**Input:**

> “I have a sore throat and mild fever for 2 days.”

**Output:**

* Possible conditions: Common cold, mild viral infection
* Recommendations: Rest, hydrate, consult doctor if worsens
* Disclaimer: *Educational purpose only — not medical advice.*


---

## 📦 Deployment

Quick Render deployment (backend)

- This repository includes a `Procfile` and `render.yaml` to help deploy the backend to Render.
- Required environment variables (configure these in your Render dashboard):
	- `GEMINI_API_KEY` — your Google/Gemini API key (do NOT commit this to the repo).

Steps:

1. Create an account at https://render.com and link your GitHub repository.
2. Render will detect `render.yaml` and create a web service named `healthcare-backend`.
3. In the Render dashboard, add the environment variable `GEMINI_API_KEY` with your key.
4. Deploy — Render will run `pip install -r requirements.txt` and start uvicorn per the `render.yaml`.

Notes:

- SQLite is file-based. For persistent storage across restarts or multiple instances, migrate to a managed DB (e.g., Postgres) and update `Backend/db.py`.
- Keep API keys and secrets in the platform environment variables — never commit them.

