import random

STAGE = {"New": 10, "Contacted": 25, "Qualified": 45, "Demo": 65, "Proposal": 80, "Negotiation": 92}
POS = [("budget approved", 12), ("pricing", 8), ("demo", 6), ("urgent", 8), ("renewal", 5), ("referral", 7)]
NEG = [("not interested", -25), ("no budget", -18), ("competitor", -10), ("later", -6)]


def score(x):
    factors, s = [], 0

    def add(label, pts):
        nonlocal s
        if pts:
            s += pts
            factors.append({"label": label, "pts": pts})

    add(f"stage = {x['stage']}", round(STAGE[x["stage"]] * 0.45))
    d = x["days"]
    add(f"last_contact_days = {d}", 18 if d <= 7 else 8 if d <= 30 else 0 if d <= 60 else -12)
    add(f"engagement = {x['engagement']}/10", round(x["engagement"] * 2.2))
    v = x["value"]
    add(f"deal_value = ${v // 1000}k", 10 if v >= 50000 else 5 if v >= 20000 else 0)
    n = (x.get("notes") or "").lower()
    for k, p in POS + NEG:
        if k in n:
            add(f'notes mention "{k}"', p)
    factors.sort(key=lambda f: -abs(f["pts"]))
    return max(0, min(100, round(s))), factors


def dup_key(x):
    parts = "".join(c for c in x["name"].lower() if c.isalpha() or c == " ").split()
    return f'{x["company"].lower()}|{parts[0][0] if parts else ""}|{parts[-1] if parts else ""}'


def suggest(x):
    if x["score"] >= 60 and x["days"] <= 30:
        return "Send follow-up email", f"High score ({x['score']}) and contacted {x['days']} days ago, keep momentum."
    if x["stale"]:
        return "Send re-engagement email", f"No contact for {x['days']} days; stage is {x['stage']}."
    if x["score"] < 30:
        return "Change status to Nurture", f"Low score ({x['score']}) and weak signals."
    return "Create call task", f"Mid score ({x['score']}); a call is the best next step."


def analyse(leads, decisions, ai=None):
    ai = ai or {}
    seen = {}
    for x in leads:
        x["dup"], x["dupOf"] = False, None
        for k in (dup_key(x), "e:" + x["email"].lower() if x["email"] else None):
            if not k:
                continue
            if k in seen and seen[k] is not x:
                x["dup"], x["dupOf"] = True, seen[k]["name"]
            else:
                seen[k] = x
        x["rule_score"], x["factors"] = score(x)
        a = ai.get(x["id"])
        x["ai_score"] = a["score"] if a else None
        x["ai_reason"] = a["reason"] if a else None
        x["score"] = round((x["rule_score"] + a["score"]) / 2) if a else x["rule_score"]
        x["stale"] = x["days"] > 60
        x["rank"] = None
    active = sorted([x for x in leads if not x["dup"]], key=lambda x: -x["score"])
    for i, x in enumerate(active, 1):
        x["rank"] = i
    queue = []
    for x in active[:15]:
        t, why = suggest(x)
        queue.append({"id": x["id"], "type": t, "why": why, "status": decisions.get(x["id"], "pending")})
    return active, queue


def digest(active):
    from datetime import date
    top = active[:5]
    body = "\n\n".join(
        f"{i}. {x['name']} ({x['company']}) - score {x['score']}\n   Why: "
        + "; ".join(f"{f['label']} ({'+' if f['pts'] > 0 else ''}{f['pts']})" for f in x["factors"][:3])
        for i, x in enumerate(top, 1))
    return f"InsightPilot daily digest - {date.today():%a %d %b %Y}\nCall these {len(top)} first:\n\n{body}"


STRONG = ["CFO joined the call and asked for contract terms", "legal review of our MSA has started",
          "asked for a pilot start date", "budget approved by CFO", "urgent: contract ends soon",
          "referral from existing client"]
NEUTRAL = ["asked about pricing", "wants a demo next week", "intro email sent", "renewal discussion",
           "requested case studies"]
WEAK = ["went silent after the proposal", "not interested right now", "no budget this quarter",
        "evaluating a competitor", "call me later", "signed with another vendor last week"]


def sample():
    """Synthetic CRM. A hidden 'intent' variable drives notes, engagement and the won/lost label,
    so labels are NOT computed from the scorer's formula. Several notes carry signal the keyword rules cannot read."""
    r = random.Random(26)
    F = "Aarav Priya Rohan Meera Karan Divya Arjun Sneha Vikram Anita Rahul Nisha Suresh Kavya Imran Lakshmi".split()
    L = "Sharma Iyer Nair Reddy Kumar Menon Singh Patel Rao Das Gupta Bose".split()
    C = ["Zenith Labs", "Orbit Retail", "Nimbus Cloud", "Pixel Foods", "Vertex Steel", "Lumen Health",
         "Kite Logistics", "Atlas Edu", "Brightpay", "Cobalt Auto"]
    st = list(STAGE)
    out = []
    for i in range(72):
        f, l, c = r.choice(F), r.choice(L), r.choice(C)
        intent = r.random()
        stage = st[min(5, int(intent * 2.5 + r.random() * 3.5))]
        pool = STRONG if intent > .7 else WEAK if intent < .3 else NEUTRAL
        notes = r.choice(STRONG + NEUTRAL + WEAK) if r.random() < .2 else r.choice(pool)
        d = int(r.random() * r.random() * 120 * (1.4 - intent))
        eng = max(0, min(10, round(intent * 6 + r.random() * 5)))
        val = round(3 + r.random() * 90) * 1000
        z = .55 * intent + .1 * STAGE[stage] / 100 + .08 * eng / 10 + (.04 if d < 14 else 0) + (r.random() - .5) * .45
        out.append(dict(id=i + 1, name=f"{f} {l}", company=c, email=f"{f}.{l}".lower() + "@" + c.split()[0].lower() + ".com",
                        stage=stage, days=d, value=val, engagement=eng, notes=notes, won=1 if z > .56 else 0))
    for i in range(8):
        o = out[i * 7]
        out.append({**o, "id": 73 + i, "name": o["name"][0] + ". " + o["name"].split()[-1], "days": o["days"] + 30 + i,
                    "engagement": max(0, o["engagement"] - 4), "notes": "intro email sent", "email": ""})
    return out
