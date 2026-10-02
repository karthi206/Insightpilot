from scoring import STAGE

NOTE = ("Sample labels are synthetic: a hidden 'intent' variable generates outcomes, separate from the scorer. "
        "Upload real CRM outcomes (won column) for a real result.")


def p_at_k(order, k=10):
    top = order[:k]
    return sum(x["won"] for x in top) / len(top)


def evaluate(leads, k=10):
    lab = [x for x in leads if not x["dup"] and x.get("won") in (0, 1)]
    if len(lab) < 2 * k:
        return None
    base = sum(x["won"] for x in lab) / len(lab)
    methods = [("Sort by deal value", lambda x: x["value"]),
               ("Sort by most recent contact", lambda x: -x["days"]),
               ("Sort by pipeline stage", lambda x: STAGE[x["stage"]]),
               ("InsightPilot rules", lambda x: x["rule_score"])]
    if any(x["ai_score"] is not None for x in lab):
        methods.append(("InsightPilot rules + AI", lambda x: x["score"]))
    rows = []
    for name, key in methods:
        p = p_at_k(sorted(lab, key=key, reverse=True), k)
        rows.append({"name": name, "p": p, "lift": p / base if base else 0})
    return {"rows": rows, "n": len(lab), "base": base, "k": k, "note": NOTE}
