import csv, io
import scoring


def parse_csv(text):
    rows = list(csv.DictReader(io.StringIO(text)))
    if not rows:
        raise ValueError("CSV has no rows")
    leads = []
    for i, r in enumerate(rows, 1):
        r = {(k or "").strip().lower(): (v or "").strip() for k, v in r.items()}
        stage = next((s for s in scoring.STAGE if s.lower() == r.get("stage", "").lower()), "New")
        won = r.get("won", "")
        leads.append(dict(id=i, name=r.get("name") or "Unknown", company=r.get("company", ""), email=r.get("email", ""),
                          stage=stage, days=int(float(r.get("last_contact_days") or 0)),
                          value=int(float(r.get("deal_value") or 0)),
                          engagement=min(10, int(float(r.get("engagement") or 0))),
                          notes=r.get("notes", ""), won=int(float(won)) if won != "" else None))
    return leads
