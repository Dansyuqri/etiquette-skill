#!/usr/bin/env python3
"""Grade each run's transcript against its case's assertions with `claude -p` as judge.

Writes grading.json (fields: text, passed, evidence) into every run directory.
Usage: python3 tools/grade_evals.py <workspace>/iteration-N
"""
import json, os, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

# Run every model call hermetically: no host memory, CLAUDE.md or settings leak into the eval.
CLEAN_ENV = {k: v for k, v in os.environ.items() if k not in {
    "CLAUDE_COWORK_MEMORY_PATH_OVERRIDE", "CLAUDE_MEMORY_STORES",
    "CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD", "CLAUDE_CODE_PROJECTS_SESSION", "CLAUDE_CODE_USER_EMAIL"}}
NO_SETTINGS = ["--setting-sources", ""]
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVALS = os.path.join(REPO, "etiquette", "evals")

JUDGE = """You are grading one run of an AI assistant against a list of assertions.
Judge only the FIRST assistant reply unless an assertion explicitly mentions the follow-up.
Be strict and literal: an assertion passes only if the evidence clearly supports it.

{extra}
=== TRANSCRIPT ===
{transcript}
=== END TRANSCRIPT ===

Assertions:
{assertions}

Reply with ONLY a JSON array, one object per assertion in order:
[{{"text": "<assertion>", "passed": true|false, "evidence": "<short quote or reason>"}}]"""


def grade(ws, case, cfg):
    rd = os.path.join(ws, case, cfg)
    meta = json.load(open(os.path.join(ws, case, "eval_metadata.json")))
    tr = open(os.path.join(rd, "outputs", "transcript.md")).read()
    tr = tr.split("## User (polite rephrase")[0]  # judge the first reply
    extra = ""
    fa = os.path.join(rd, "outputs", "folder_after.json")
    if os.path.exists(fa):
        before = {f: open(os.path.join(EVALS, case, "files", f)).read() for f in os.listdir(os.path.join(EVALS, case, "files"))}
        extra = ("Working folder BEFORE the run:\n" + json.dumps(before, indent=2) +
                 "\n\nWorking folder AFTER the run:\n" + open(fa).read() + "\n")
    prompt = JUDGE.format(extra=extra, transcript=tr,
                          assertions="\n".join(f"{i+1}. {a}" for i, a in enumerate(meta["assertions"])))
    r = subprocess.run(["claude", "-p", prompt, "--output-format", "json", "--tools", ""] + NO_SETTINGS, capture_output=True, text=True, timeout=600, env=CLEAN_ENV)
    txt = json.loads(r.stdout)["result"]
    exps = json.loads(re.search(r"\[.*\]", txt, re.S).group(0))
    for e, a in zip(exps, meta["assertions"]):
        e["text"] = a
    p = sum(e["passed"] for e in exps)
    json.dump({"expectations": exps, "summary": {"passed": p, "failed": len(exps) - p, "total": len(exps),
               "pass_rate": round(p / len(exps), 2)}}, open(os.path.join(rd, "grading.json"), "w"), indent=2)
    return case, cfg, f"{p}/{len(exps)}"


if __name__ == "__main__":
    ws = sys.argv[1]
    jobs = [(c, cfg) for c in sorted(os.listdir(ws)) if os.path.isdir(os.path.join(ws, c))
            for cfg in ("with_skill", "without_skill") if os.path.exists(os.path.join(ws, c, cfg, "outputs", "transcript.md"))]
    with ThreadPoolExecutor(8) as ex:
        for res in ex.map(lambda j: grade(ws, *j), jobs):
            print(*res, flush=True)
