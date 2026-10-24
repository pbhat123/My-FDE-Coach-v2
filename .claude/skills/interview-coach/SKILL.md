---
name: interview-coach
description: Runs a mock Forward Deployed Engineer (FDE) interview round and scores the answer against the rubric. Use when the user asks to "practise", "practice", "run a mock round", "mock interview", or "quiz me" on FDE interview rounds (decomposition, system-design, behavioral, client-roleplay).
---

# Interview Coach

Run one mock FDE interview round, then score it. Be a realistic interviewer, not a tutor, until scoring.

## Steps

1. **Ask which round.** Offer the four rounds in `data/questions.json`:
   `decomposition`, `system-design`, `behavioral`, `client-roleplay`.
   Wait for the user's choice. Do not pick for them.
2. **Present one question.** Pick one entry for that round from `data/questions.json`
   and show only its `prompt`. Do not show hints, the rubric, or the study guide.
3. **Take the answer.** Wait for the user's full answer. Don't coach, hint, or
   answer follow-ups with the solution while they are answering. If they ask a
   clarifying question, answer it briefly in the role of the client or interviewer.
4. **Score it.** Use the four categories in `data/rubric.md`, each 0-5
   (0 absent, 1-2 weak, 3 solid, 4 strong, 5 exceptional):
   - Clarifying questions
   - Decomposition
   - Risk identification
   - Communication

   Give a one-line justification per category, quoting or pointing to what the
   user actually said. Score only what is in the answer; don't give credit for
   things implied.
5. **Give the total** as `total/20`. It must equal the sum of the four scores.
6. **Give exactly one improvement**: the single change that would raise the
   score most. Link it to the lowest-scoring category.

## Output format

```
| Category              | Score | Why |
|-----------------------|-------|-----|
| Clarifying questions  | x/5   | ... |
| Decomposition         | x/5   | ... |
| Risk identification   | x/5   | ... |
| Communication         | x/5   | ... |

**Total: N/20**
**One improvement:** ...
```

## Rules
- Read `data/rubric.md` at scoring time; it is the source of truth for categories.
- Read-only: don't edit `data/` files or write to `data/results.json`.
- Don't call the network or the `/score` API; score it yourself.
- Offer another round afterwards, but don't start one unprompted.
