# Multimodal Construction Intelligence Platform

A production‑ready **Streamlit** application that demonstrates AI‑powered multimodal analysis for construction sites.

## Features
- **Secure Gemini API key** entry (fallback demo mode).
- **Tab 1:** PPE compliance audit from site photos (JSON report, metric cards).
- **Tab 2:** Crack diagnostics on concrete/wall images (defect classification, repair suggestions).
- **Tab 3:** Project budgeting, valuation, material estimation, and placeholder 3D rendering.
- **Tab 4:** Weather‑aware safety alerts and a multi‑turn construction assistant chatbot.
- No external database dependencies – one‑click deployable on Streamlit Community Cloud.

## Quick Start (Local)
1. **Clone / copy the project** into a folder, e.g. `d:\NOTES\skill wallet project`.
2. **Create a virtual environment** (optional but recommended):
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
3. **Install dependencies**:
   ```powershell
   pip install streamlit pillow google-generativeai
   ```
   - `google-generativeai` is the official client library for Gemini.
4. **Run the app**:
   ```powershell
   streamlit run app.py
   ```
   The app will open in your default browser at `http://localhost:8501`.

## Deploy to Streamlit Community Cloud
1. Push the repository to a Git hosting service (GitHub, GitLab, etc.).
2. In Streamlit Cloud, click **New app**, select the repo and the `app.py` file.
3. Add a secret named `GEMINI_API_KEY` under **Settings → Secrets** if you have a Google Gemini key.
4. Deploy – the app will run in demo mode if the key is missing.

## Gemini API Key (Optional)
- Obtain a key from **Google AI Studio**.
- Provide it via the sidebar input or set the environment variable `GEMINI_API_KEY` before launching.

## Notes
- The application is fully self‑contained; all data is processed in‑memory.
- For production, consider enabling caching, stronger error handling, and logging.
- The 3‑D rendering tab currently shows a placeholder image – integrate with Pollinations AI via their API for real renders.

---
© 2026 Multimodal Construction Intelligence Platform – Built with Streamlit and Google Gemini
