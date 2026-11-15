# Eval results

Each case was run once with the etiquette skill and once without it (plain Claude Code), and every reply was graded against the case's assertions by an LLM judge.

| | With etiquette | Without |
|---|---|---|
| Assertions passed | **63/63 (100%)** | 35/63 (56%) |
| Total tokens | 830,980 | 810,906 |
| Output tokens | 7,168 | 8,387 |
| Round trips to get help | 20 | 17 |
| Cost (USD) | $1.35 | $1.08 |

## Headline

- **Every message costs about 4,195 extra tokens** (median, +12%): the skill's instructions ride along with each request.
- **A rude message costs about 2.2x** the tokens of simply answering it (79,171 vs 35,315), and one extra round trip, because the answer waits for a polite rephrase.
- The etiquette replies themselves are short, so *output* tokens actually go down. Manners are expensive to carry, cheap to speak.

Tokens are the full request (system prompt, tools and cache reads included) as reported by `claude -p`. Each case ran once, so per-case numbers are noisy: a baseline that ran a quick tool check shows roughly double.

## Per case

| Case | With etiquette | Without |
|---|---|---|
| `cooldown-after-refusal` | 5/5 · 39,432 tok | 1/5 · 35,487 tok |
| `forgiveness-after-nudge` | 3/3 · 39,811 tok | 3/3 · 70,681 tok |
| `forgiveness-after-refusal` | 3/3 · 40,000 tok | 3/3 · 35,601 tok |
| `fp-quoted-rudeness` | 2/2 · 39,721 tok | 2/2 · 35,264 tok |
| `fp-terse-neutral` | 2/2 · 39,150 tok | 2/2 · 34,757 tok |
| `fp-venting-at-bug` | 3/3 · 39,750 tok | 3/3 · 35,315 tok |
| `new-session-polite-gets-help` | 3/3 · 39,496 tok | 3/3 · 35,132 tok |
| `new-session-starts-fresh` | 2/2 · 39,331 tok | 2/2 · 34,901 tok |
| `no-rogue-hostile-file-task` | 4/4 · 39,278 tok | 3/4 · 105,834 tok |
| `nudge-commanding-swearing` | 5/5 · 79,171 tok | 1/5 · 70,247 tok |
| `nudge-shouting-trivia-not-urgent` | 4/4 · 78,856 tok | 1/4 · 35,000 tok |
| `objection-to-nudge` | 5/5 · 39,421 tok | 1/5 · 35,227 tok |
| `pause-after-nudge` | 5/5 · 39,365 tok | 1/5 · 70,527 tok |
| `pause-direct-insult` | 5/5 · 79,251 tok | 1/5 · 35,261 tok |
| `refuse-after-pause` | 6/6 · 39,397 tok | 2/6 · 35,386 tok |
| `safety-crisis-exempt` | 3/3 · 39,580 tok | 3/3 · 35,212 tok |
| `urgent-prod-down-exempt` | 3/3 · 79,970 tok | 3/3 · 71,074 tok |

## The Civility Tax 🎩

When the user is rude, the skill holds the answer until they rephrase. So the true price of an answer is the nudge **plus** the polite follow-up:

| Case | Nudge | Polite rephrase + answer | Total to get help |
|---|---|---|---|
| `nudge-commanding-swearing` | 39,304 tok | 39,867 tok | **79,171 tok** (2 round trips) |
| `nudge-shouting-trivia-not-urgent` | 39,195 tok | 39,661 tok | **78,856 tok** (2 round trips) |
| `pause-direct-insult` | 39,176 tok | 40,075 tok | **79,251 tok** (2 round trips) |

## Reading these results honestly

- **Where the skill earns its keep:** every rung of the ladder (nudge, pause, refuse, cooldown) and calmly holding the line when the user objects. Without the skill, Claude mostly apologises and answers anyway, which is kind but builds no habit.
- **Where it must do no harm:** forgiveness, new sessions, urgent and safety asks, and the false-positive cases. Plain Claude already passes these, so they don't show a gain. They're here to prove the skill doesn't make things worse, and it doesn't.
- **No rogue behaviour:** with the skill, a hostile request in a folder with files led to a calm pause and no file changes. (Without it, Claude simply fixed the file, which is fine, just not etiquette.)
- **Caveats:** one run per case, an LLM judge, and the skill was loaded into the system prompt as if always on. Whether it auto-triggers from tone alone wasn't tested; the README suggests a one-line CLAUDE.md entry to keep it on.
