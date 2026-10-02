# InsightPilot

AI decision engine that ranks and explains sales leads from CRM data.
Team Quantum Force, BFWAI/HACK 26, PS-04.

## Run locally
```bash
cd backend
pip install -r requirements.txt
cp ../.env.example ../.env        # optional: add ANTHROPIC_API_KEY
uvicorn main:app --reload
# open http://localhost:8000
```
Tests: `pip install pytest httpx && pytest -q tests` (from project root).

## Run with Docker
```bash
docker build -t insightpilot . && docker run -p 8000:8000 --env-file .env insightpilot
```

## Deploy (Render / Railway)
Push to GitHub, then Render > New > Blueprint (uses `render.yaml`) or a Web Service using the Dockerfile. Set `ANTHROPIC_API_KEY` as an env var (optional).

## Features
- Rule-based lead score (stage, recency, engagement, deal value, notes keywords) with the contributing fields and points shown per lead
- **Claude re-rank** (`POST /api/ai-rank`): Claude scores the top 20 using free-text notes; blended 50/50 with the rule score; reason shown per lead. Needs `ANTHROPIC_API_KEY`
- Duplicate (company + initial + surname, or same email) and stale (60+ days) detection
- Human-in-the-loop approval queue: approving a lead drafts the email (Claude when keyed, template otherwise). Nothing is sent
- Daily digest, CSV upload
- Evaluation tab / `python backend/evaluate.py [labelled.csv]`: precision@10 versus baselines (deal value, recency, stage)

## Evaluation honesty
Sample outcomes are synthetic, generated from a hidden variable rather than the scorer's formula. On the 69 labelled sample leads the rules perform about like "sort by stage"; the sample is small, so differences are noise. Use real CRM outcomes for a real result. The Claude blend has not been measured here.

## API
`GET /api/state` · `POST /api/sample` · `POST /api/upload` (CSV) · `POST /api/queue/{id}` `{status}` · `POST /api/explain/{id}` · `POST /api/ai-rank`

CSV columns: name, company, email, stage, last_contact_days, deal_value, engagement, notes, won (optional 1/0)

## Not implemented yet (from the idea deck)
Embedding-based semantic dedup, vector DB / RAG, MCP CRM connectors, persistent storage (state is in memory), real email sending.
