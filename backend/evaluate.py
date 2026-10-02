"""Usage: python evaluate.py [labelled.csv]  - precision@10 for InsightPilot vs simple baselines."""
import sys
import scoring, metrics
from data_io import parse_csv

leads = parse_csv(open(sys.argv[1], encoding="utf-8-sig").read()) if len(sys.argv) > 1 else scoring.sample()
scoring.analyse(leads, {}, {})
e = metrics.evaluate(leads)
if not e:
    sys.exit("Need at least 20 labelled leads (won = 1/0).")
print(f"{e['n']} labelled leads, base win rate {e['base']:.0%}\n")
for r in e["rows"]:
    print(f"{r['name']:<32} precision@{e['k']} = {r['p']:.0%}   lift {r['lift']:.1f}x")
print("\n" + e["note"])
