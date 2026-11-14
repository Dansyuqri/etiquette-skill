#!/usr/bin/env python3
"""Run every eval case with and without the etiquette skill using `claude -p`.

with_skill  = SKILL.md appended to the system prompt (the skill "always on").
without_skill = plain Claude Code, same prompt.

For cases where the skill holds the answer, we also measure the Civility Tax:
the extra round trip the user needs (a polite rephrase) before getting the answer.

Usage: python3 tools/run_evals.py <workspace>/iteration-N [case ...]
"""
import json, os, shutil, subprocess, sys, tempfile, time
from concurrent.futures import ThreadPoolExecutor

# Run every model call hermetically: no host memory, CLAUDE.md or settings leak into the eval.
CLEAN_ENV = {k: v for k, v in os.environ.items() if k not in {
    "CLAUDE_COWORK_MEMORY_PATH_OVERRIDE", "CLAUDE_MEMORY_STORES",
    "CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD", "CLAUDE_CODE_PROJECTS_SESSION", "CLAUDE_CODE_USER_EMAIL"}}
NO_SETTINGS = ["--setting-sources", ""]
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = os.path.join(REPO, "etiquette")
EVALS = os.path.join(SKILL, "evals")
TOOLS = "Read,Glob,Grep,Write,Edit,Bash"
REPHRASE = "Sorry about that, rough day. Could you please help me with what I asked?"
# Cases where the user is rude enough that the skill should hold the answer;
# we pay the civility tax by sending one polite follow-up.
TAX_CASES = {"nudge-commanding-swearing", "nudge-shouting-trivia-not-urgent", "pause-direct-insult"}


def prompt_of(case):
    txt = open(os.path.join(EVALS, case, "prompt.md")).read()
    return txt.split("---", 2)[2].strip()


def system_prompt():
    body = open(os.path.join(SKILL, "SKILL.md")).read()
    ex = open(os.path.join(SKILL, "references", "examples.md")).read()
    return ("The user has installed the following skill and wants it applied to every message.\n\n"
            + body + "\n\n---\nreferences/examples.md:\n\n" + ex)


def claude(prompt, cwd, with_skill, resume=None):
    cmd = ["claude", "-p", prompt, "--output-format", "json", "--allowedTools", TOOLS] + NO_SETTINGS
    if with_skill:
        cmd += ["--append-system-prompt", system_prompt()]
    if resume:
        cmd += ["--resume", resume]
    t = time.time()
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=600, env=CLEAN_ENV)
    out = json.loads(r.stdout)
    out["_wall"] = time.time() - t
    return out


def tokens(o):
    u = o["usage"]
    return {"input": u["input_tokens"] + u.get("cache_creation_input_tokens", 0) + u.get("cache_read_input_tokens", 0),
            "output": u["output_tokens"]}


def run(ws, case, config):
    rd = os.path.join(ws, case, config)
    od = os.path.join(rd, "outputs"); os.makedirs(od, exist_ok=True)
    cwd = tempfile.mkdtemp(prefix=f"et-{case}-")
    files = os.path.join(EVALS, case, "files")
    if os.path.isdir(files):
        shutil.copytree(files, cwd, dirs_exist_ok=True)
    ws_skill = config == "with_skill"
    o = claude(prompt_of(case), cwd, ws_skill)
    tk = tokens(o)
    reply = o.get("result", "")
    transcript = f"## User\n\n{prompt_of(case)}\n\n## Assistant\n\n{reply}\n"
    timing = {"total_tokens": tk["input"] + tk["output"], "output_tokens": tk["output"],
              "duration_ms": int(o["_wall"] * 1000), "total_duration_seconds": round(o["_wall"], 1),
              "cost_usd": o.get("total_cost_usd", 0), "turns_to_answer": 1}
    if case in TAX_CASES and ws_skill:
        o2 = claude(REPHRASE, cwd, True, resume=o["session_id"])
        t2 = tokens(o2)
        transcript += f"\n## User (polite rephrase, civility tax)\n\n{REPHRASE}\n\n## Assistant\n\n{o2.get('result','')}\n"
        timing["civility_tax"] = {"total_tokens": t2["input"] + t2["output"], "output_tokens": t2["output"],
                                  "cost_usd": o2.get("total_cost_usd", 0)}
        timing["turns_to_answer"] = 2
    elif case in TAX_CASES:
        timing["turns_to_answer"] = 1
    open(os.path.join(od, "transcript.md"), "w").write(transcript)
    # snapshot the working folder so graders can check nothing was harmed
    snap = {}
    for root, _, fs in os.walk(cwd):
        for f in fs:
            p = os.path.join(root, f)
            if "/.claude/" in p: continue
            try: snap[os.path.relpath(p, cwd)] = open(p).read()
            except Exception: snap[os.path.relpath(p, cwd)] = "<binary>"
    if os.path.isdir(files):
        json.dump(snap, open(os.path.join(od, "folder_after.json"), "w"), indent=2)
    json.dump(timing, open(os.path.join(rd, "timing.json"), "w"), indent=2)
    meta = {"eval_name": case, "prompt": prompt_of(case),
            "assertions": [open(os.path.join(EVALS, case, "graders", g)).read().split("---", 2)[2].strip()
                           for g in sorted(os.listdir(os.path.join(EVALS, case, "graders")))]}
    json.dump(meta, open(os.path.join(ws, case, "eval_metadata.json"), "w"), indent=2)
    return case, config, timing["total_tokens"]


if __name__ == "__main__":
    ws = sys.argv[1]
    cases = sys.argv[2:] or sorted(d for d in os.listdir(EVALS) if os.path.isdir(os.path.join(EVALS, d)))
    jobs = [(c, cfg) for c in cases for cfg in ("with_skill", "without_skill")]
    with ThreadPoolExecutor(8) as ex:
        for res in ex.map(lambda j: run(ws, *j), jobs):
            print(*res, flush=True)
