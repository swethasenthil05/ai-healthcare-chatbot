# AI Healthcare Chatbot for Symptom Analysis and Healthcare Guidance

A learning/demo web application with automatic online/offline fallback.

## Architecture

- **Frontend:** Streamlit (`app.py`)
- **Backend API:** FastAPI (`server.py`)
- **Online/server reference database:** SQLite demo DB (`data/server_healthcare.db`)
- **Offline/local reference database:** SQLite (`data/healthcare.db`)
- **Online/offline switching:** the frontend checks `GET /health`; if the API is unavailable or a request fails, it uses the local engine.
- **Offline matching:** transparent keyword/rule matching.
- **Online AI/NLP:** this starter uses API-backed retrieval, not a generative model by default. An approved NLP/LLM provider can be integrated later using clinician-reviewed content, privacy controls, and validated safeguards.

## Requirements

- Python 3.10 or later
- Internet connection only for installing packages and using the online backend
- A terminal/command prompt

## Setup (Windows PowerShell)

1. Extract the ZIP and open a terminal in the project folder.
2. Create and activate a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Install packages:

   ```powershell
   pip install -r requirements.txt
   ```

4. Copy environment settings:

   ```powershell
   Copy-Item .env.example .env
   ```

5. Start the backend in terminal 1:

   ```powershell
   uvicorn server:app --reload --host 127.0.0.1 --port 8000
   ```

6. Start the web app in terminal 2:

   ```powershell
   streamlit run app.py
   ```

7. Open the local URL Streamlit prints, usually `http://localhost:8501`.

## Setup (macOS/Linux)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn server:app --reload --host 127.0.0.1 --port 8000
```

In a second terminal with the same environment activated:

```bash
streamlit run app.py
```

## Test offline fallback

1. Start Streamlit.
2. Stop the FastAPI server with `Ctrl+C` in terminal 1.
3. Submit a symptom such as `fever, headache`.
4. The app should display **Offline mode** and use the local SQLite DB.
5. Restart the API server. The app checks availability again when the page is rerun.

The frontend and backend are separate local processes. For a real hosted deployment, configure `API_BASE_URL` to the deployed API URL and protect it with HTTPS, authentication, rate limiting, monitoring, and privacy controls.

## Current demo dataset

The included examples cover common cold-like symptoms, fever, headache, cough, stomach discomfort, and sore throat. This is a small educational dataset, not a complete medical knowledge base.

## Important safety and production limitations

- This software is **not a medical device and does not diagnose conditions**.
- The data is illustrative and must be reviewed by qualified healthcare professionals before clinical use.
- Symptom keyword matching can miss context, negation, rare symptoms, and dangerous conditions.
- Emergency phrase detection is a limited additional safeguard, not a reliable triage system. Never delay emergency care to use this app.
- Do not add identifiable patient information unless privacy, security, consent, retention, and applicable legal requirements have been addressed.
- Before production, add clinician-reviewed content, tests, audit/security review, accessibility, multilingual support as appropriate, and a validated triage pathway.
- The default server database is SQLite for easy local demonstration. PostgreSQL is a better option for a multi-user hosted deployment.

## Project structure

```text
ai_healthcare_chatbot/
├── app.py
├── server.py
├── local_engine.py
├── safety.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── data/
└── tests/
```
