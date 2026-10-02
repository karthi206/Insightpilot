import sys, io
sys.path.insert(0, "backend")
from fastapi.testclient import TestClient
from main import app
c = TestClient(app)


def test_state_ranks_and_flags_dups():
    s = c.get("/api/state").json()
    assert len(s["leads"]) == 80 and len(s["queue"]) == 15
    assert sum(l["dup"] for l in s["leads"]) >= 8
    ranks = sorted(l["rank"] for l in s["leads"] if l["rank"])
    assert ranks == list(range(1, len(ranks) + 1))


def test_approval_and_explain():
    q = c.get("/api/state").json()["queue"][0]
    assert c.post(f"/api/queue/{q['id']}", json={"status": "approve"}).status_code == 200
    assert c.get("/api/state").json()["queue"][0]["status"] == "approve"
    assert c.post(f"/api/explain/{q['id']}").json()["text"].startswith("Score")


def test_upload():
    data = "name,company,email,stage,last_contact_days,deal_value,engagement,notes,won\nAsha Rao,Orbit,a@o.com,Proposal,3,48000,8,budget approved,1\n"
    r = c.post("/api/upload", files={"file": ("x.csv", io.BytesIO(data.encode()), "text/csv")})
    assert r.json()["count"] == 1


def test_eval_has_baselines():
    c.post("/api/sample")
    e = c.get("/api/state").json()["eval"]
    names = [r["name"] for r in e["rows"]]
    assert "Sort by pipeline stage" in names and "InsightPilot rules" in names


def test_ai_rank_without_key_is_safe(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    assert c.post("/api/ai-rank").json()["ai"] is False


def test_ai_blend_and_draft(monkeypatch):
    import main
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    c.post("/api/sample")
    top = c.get("/api/state").json()["leads"]
    x = next(l for l in top if l["rank"] == 1)
    main.STORE["ai"] = {x["id"]: {"score": 0, "reason": "test"}}
    y = next(l for l in c.get("/api/state").json()["leads"] if l["id"] == x["id"])
    assert y["ai_score"] == 0 and y["score"] == round(y["rule_score"] / 2)
    main.STORE["ai"] = {}
    q = c.get("/api/state").json()["queue"][0]
    c.post(f"/api/queue/{q['id']}", json={"status": "approve"})
    assert c.get("/api/state").json()["queue"][0]["draft"]
