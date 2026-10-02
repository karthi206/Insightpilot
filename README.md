# InsightPilot

**AI decision engine that ranks CRM leads, explains every rank, and never acts without human approval.**
Team Quantum Force | Build Fast with AI: AI Build Challenge 2026 | PS-04: AI Decision Engine for Business Data

## 💡 Project Overview
Sales reps waste time deciding who to call first, and most CRM scores come with no reason. InsightPilot reads CRM lead data and tells a rep **who to contact today and why**.

- **Smart lead ranking:** a 0-100 score from deal stage, contact recency, engagement, deal value and notes keywords
- **Explainable reasoning:** every score lists the CRM fields and points behind it; Claude can rewrite them in plain language
- **Claude re-rank:** Claude reads the free-text notes of the top 20 leads, scores them, and gives a one-line reason; blended 50/50 with the rule score
- **Cleanup:** detects duplicate leads (same company + initial + surname, or same email) and stale leads (60+ days without contact)
- **Human-in-the-loop approval queue:** suggested actions wait for Approve/Reject; approving drafts the email (nothing is sent)
- **Daily digest:** the top 5 leads to act on today
- **Evaluation:** precision@10 compared with simple baselines (deal value, recency, stage)

## 🛠️ Technologies Used
- **Backend:** Python 3.12, FastAPI, Uvicorn
- **AI:** Anthropic Claude API (`anthropic` SDK), optional; the app works without a key using rule-based scoring
- **Frontend:** HTML, CSS, vanilla JavaScript (no build step)
- **Data:** synthetic CRM sample generated in code, plus CSV upload
- **Testing:** pytest, httpx
- **Deployment:** Docker, Render (`render.yaml`)

## 📁 Project Structure
```
insightpilot/
├── backend/
│   ├── main.py           # FastAPI app and API routes, Claude calls
│   ├── scoring.py        # scoring, dedup, stale detection, sample data
│   ├── metrics.py        # precision@10 evaluation vs baselines
│   ├── data_io.py        # CSV parsing
│   ├── evaluate.py       # CLI evaluation script
│   └── requirements.txt
├── frontend/index.html   # web UI served by the backend
├── tests/test_api.py
├── Dockerfile
├── render.yaml
└── .env.example
```

## ⚙️ Setup & Installation
Requirements: Python 3.10+ (3.12 recommended), pip, and optionally an Anthropic API key.

```bash
git clone https://github.com/karthi206/Insightpilot-.git
cd Insightpilot-
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r backend/requirements.txt
cp .env.example .env               # optional: put your ANTHROPIC_API_KEY in .env
```

## 🚀 How to Run
```bash
cd backend
# optional, enables Claude features:
export ANTHROPIC_API_KEY=your_key_here     # Windows PowerShell: $env:ANTHROPIC_API_KEY="your_key_here"
uvicorn main:app --reload
```
Open **http://localhost:8000**.

**Try it:**
1. Click **Load sample CRM (80 leads)** and open the **Ranked** tab to see scores and reasons.
2. Click **Re-rank with Claude** (needs the API key) to blend Claude's note-based scores in.
3. Open **Approvals**, approve an action to see the drafted email.
4. Check **Cleanup**, **Digest** and **Evaluation**.
5. To use your own data, click **Upload CSV** (use **Download CSV template** for the columns).

**Docker:** `docker build -t insightpilot . && docker run -p 8000:8000 -e ANTHROPIC_API_KEY=your_key insightpilot`

**Tests:** `pip install pytest httpx && pytest -q tests`

**Evaluation script:** `python backend/evaluate.py [labelled.csv]`

## 🔌 API
`GET /api/state` · `POST /api/sample` · `POST /api/upload` (CSV) · `POST /api/queue/{id}` `{"status":"approve|reject"}` · `POST /api/explain/{id}` · `POST /api/ai-rank`

CSV columns: `name, company, email, stage, last_contact_days, deal_value, engagement, notes, won` (won is optional, 1/0)

## 📊 Evaluation Note
The sample outcomes are synthetic, generated from a hidden variable rather than the scorer's formula. On the sample, the rules perform about like "sort by stage", and the set is small, so differences are noise. The Claude blend has not been measured. Use real CRM outcomes for a real result.

## 🚧 Not Implemented Yet
Embedding-based semantic dedup, vector DB / RAG, MCP CRM connectors, persistent storage (state is in memory and resets on restart), real email sending.

## 👥 Team Quantum Force
Karthikeyan A, Jitenra Rajan V, Kumaran S, Easwari Engineering College
