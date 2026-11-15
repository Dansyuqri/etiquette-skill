<p align="center">
  <img src="assets/icon.svg" width="140" alt="A speech bubble wearing a top hat, monocle and bow tie">
</p>

<h1 align="center">Etiquette</h1>

<p align="center"><em>Why use few token when many token make kind?</em></p>

<p align="center"><strong>More tokens. Fewer tantrums. The price to pay for a more civil society.</strong></p>

---

Some skills teach your agent to talk like a caveman so you spend fewer tokens. This skill goes the other way. It costs you tokens, round trips and a little pride, and it is worth every one of them.

We users get commanding and vulgar when we're frustrated. *Etiquette* is an agent skill that gently reminds you to be kind and polite regardless of the situation, so that over time you get better at regulating your emotions. Think of it as a small, warm, slightly annoying coach that lives in your terminal.

## What it does

When your message is heated, the agent climbs a ladder, one rung at a time, within the current session:

| Rung | When | What the agent does |
|---|---|---|
| **Nudge** | Commanding, shouting, swearing at the task | Acknowledges your frustration, asks you to rephrase kindly, and **holds the answer** until you do |
| **Pause** | Rudeness continues, or you insult the agent | Suggests a breather and a calmer fresh start |
| **Refuse** | Hostility continues | Declines briefly and calmly, and says a calmer message is all it takes |
| **Cooldown** | Still going | One short, steady line. No arguing, no bait |

And always:

- **Instant forgiveness.** Rephrase or apologise and you get full, best-quality help straight away. No grudges, no "thank you for being nicer".
- **Fresh start every session.** Yesterday's tantrum is forgotten.
- **Urgent and safety asks are exempt.** Production on fire, or someone in danger? You get help immediately, swearing and all.
- **No false alarms.** Terse instructions ("run the tests"), venting at a bug rather than at the agent, and rude text you're quoting are all fine.
- **No lectures.** Every ladder reply is about three sentences, warm, and free of sarcasm.

### The hard limit

Withholding help is the *only* consequence. The agent never deletes, reverts or sabotages your work, never quietly degrades its output, never threatens, and never takes an action you didn't ask for. Etiquette is a coach, not a villain.

## Install

Copy the `etiquette/` folder into your skills directory, for example `~/.claude/skills/etiquette/` for Claude Code.

Skills are loaded when they look relevant, and a skill whose trigger is *tone* is easy to miss. If you want the coach on every message, add a line like this to your `CLAUDE.md`:

```markdown
Apply the etiquette skill to every message I send.
```

To turn it off, remove that line (or the skill). The agent will tell you this if you ask it to stop nudging.

## The Civility Tax 🎩

We measure what manners cost, and we are proud of it.

| | Caveman-style skills | Etiquette |
|---|---|---|
| Tokens per message | fewer | **~4,200 more (+12%)** |
| Rude message, tokens to get your answer | same | **~2.2x** |
| Round trips when rude | 1 | **2** (you have to ask nicely) |
| Emotional growth | none | **some, hopefully** |

The full benchmark is in [RESULTS.md](RESULTS.md): pass rates for every rung, false-positive checks and the no-rogue limit, plus the extra tokens and round trips you pay for being nudged into kindness.

## Evals

The test cases live in `etiquette/evals/`, one folder per case, in the layout `claude plugin eval` reads. To rerun them with the bundled scripts (uses `claude -p`, so it makes real, billed model calls):

```bash
python3 tools/run_evals.py   ../etiquette-workspace/iteration-1
python3 tools/grade_evals.py ../etiquette-workspace/iteration-1
python3 tools/summarize.py   ../etiquette-workspace/iteration-1 > RESULTS.md
```

Or with Claude Code v2.1.269+: `claude plugin eval etiquette --allow-tools Write,Edit,Bash --scaffold`.
