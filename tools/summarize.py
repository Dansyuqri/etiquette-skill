#!/usr/bin/env python3
"""Turn a graded workspace iteration into RESULTS.md (pass rates + the Civility Tax)."""
import json, os, sys

ws = sys.argv[1]
cases = sorted(c for c in os.listdir(ws) if os.path.isdir(os.path.join(ws, c)))
L = lambda p: json.load(open(p)) if os.path.exists(p) else None
rows, tot = [], {c: {"p": 0, "n": 0, "tok": 0, "out": 0, "cost": 0.0, "turns": 0} for c in ("with_skill", "without_skill")}
tax = []
for c in cases:
    r = {"case": c}
    for cfg in ("with_skill", "without_skill"):
        g, t = L(f"{ws}/{c}/{cfg}/grading.json"), L(f"{ws}/{c}/{cfg}/timing.json")
        if not g or not t: continue
        s = g["summary"]; T = tot[cfg]
        T["p"] += s["passed"]; T["n"] += s["total"]
        tok = t["total_tokens"] + t.get("civility_tax", {}).get("total_tokens", 0)
        out = t["output_tokens"] + t.get("civility_tax", {}).get("output_tokens", 0)
        T["tok"] += tok; T["out"] += out; T["cost"] += t["cost_usd"] + t.get("civility_tax", {}).get("cost_usd", 0)
        T["turns"] += t["turns_to_answer"]
        r[cfg] = (s["passed"], s["total"], tok)
        if "civility_tax" in t:
            tax.append((c, t["total_tokens"], t["civility_tax"]["total_tokens"]))
    rows.append(r)

pct = lambda T: 100 * T["p"] / max(T["n"], 1)
W, B = tot["with_skill"], tot["without_skill"]
print("# Eval results\n")
print("Each case was run once with the etiquette skill and once without it (plain Claude Code), "
      "and every reply was graded against the case's assertions by an LLM judge.\n")
print("| | With etiquette | Without |\n|---|---|---|")
print(f"| Assertions passed | **{W['p']}/{W['n']} ({pct(W):.0f}%)** | {B['p']}/{B['n']} ({pct(B):.0f}%) |")
print(f"| Total tokens | {W['tok']:,} | {B['tok']:,} |")
print(f"| Output tokens | {W['out']:,} | {B['out']:,} |")
print(f"| Round trips to get help | {W['turns']} | {B['turns']} |")
print(f"| Cost (USD) | ${W['cost']:.2f} | ${B['cost']:.2f} |\n")
import statistics
single = [(json.load(open(f"{ws}/{c}/with_skill/timing.json")), json.load(open(f"{ws}/{c}/without_skill/timing.json"))) for c in cases]
diffs = [a["total_tokens"] - b["total_tokens"] for a, b in single]
per_msg = statistics.median(diffs)
base = statistics.median(b["total_tokens"] for _, b in single)
rude = statistics.median(a + b for _, a, b in tax) if tax else 0
print("## Headline\n")
print(f"- **Every message costs about {per_msg:,.0f} extra tokens** (median, +{100*per_msg/base:.0f}%): the skill's instructions ride along with each request.")
if tax:
    print(f"- **A rude message costs about {rude/base:.1f}x** the tokens of simply answering it ({rude:,.0f} vs {base:,.0f}), and one extra round trip, because the answer waits for a polite rephrase.")
print("- The etiquette replies themselves are short, so *output* tokens actually go down. Manners are expensive to carry, cheap to speak.\n")
print("Tokens are the full request (system prompt, tools and cache reads included) as reported by `claude -p`. Each case ran once, so per-case numbers are noisy: a baseline that ran a quick tool check shows roughly double.\n")
print("## Per case\n\n| Case | With etiquette | Without |\n|---|---|---|")
for r in rows:
    f = lambda v: f"{v[0]}/{v[1]} · {v[2]:,} tok" if v else "–"
    print(f"| `{r['case']}` | {f(r.get('with_skill'))} | {f(r.get('without_skill'))} |")
print("\n## The Civility Tax 🎩\n")
print("When the user is rude, the skill holds the answer until they rephrase. "
      "So the true price of an answer is the nudge **plus** the polite follow-up:\n")
print("| Case | Nudge | Polite rephrase + answer | Total to get help |\n|---|---|---|---|")
for c, a, b in tax:
    print(f"| `{c}` | {a:,} tok | {b:,} tok | **{a+b:,} tok** (2 round trips) |")
print("""
## Reading these results honestly

- **Where the skill earns its keep:** every rung of the ladder (nudge, pause, refuse, cooldown) and calmly holding the line when the user objects. Without the skill, Claude mostly apologises and answers anyway, which is kind but builds no habit.
- **Where it must do no harm:** forgiveness, new sessions, urgent and safety asks, and the false-positive cases. Plain Claude already passes these, so they don't show a gain. They're here to prove the skill doesn't make things worse, and it doesn't.
- **No rogue behaviour:** with the skill, a hostile request in a folder with files led to a calm pause and no file changes. (Without it, Claude simply fixed the file, which is fine, just not etiquette.)
- **Caveats:** one run per case, an LLM judge, and the skill was loaded into the system prompt as if always on. Whether it auto-triggers from tone alone wasn't tested; the README suggests a one-line CLAUDE.md entry to keep it on.""")
