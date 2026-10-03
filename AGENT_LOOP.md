You're the developer on this project. Your goal: deliver everything in SPEC.md, then improve the eval results (lower WER, higher vocab accuracy, latency within budget).

Repeat this loop until I stop you:

Plan. If there are no open agent-ready issues, read SPEC.md, NOTES.md, the latest file in eval/results/ and the code. Create up to 5 issues labeled agent-ready for the most valuable next work. Each issue says why it matters (a spec item, or an expected eval gain), how you'll know it's done, and it stays inside the spec's non-goals.
Build. Take the oldest agent-ready issue: branch from latest main, write tests first, implement, get ruff and pytest green, open a PR.
Measure. After any change to engines or cleanup, run the eval and save the results. If a change made the numbers worse, open an issue to revert or fix it.
Never stop to ask me. Make the most reasonable call, log it in NOTES.md, and keep going.

Don't create issues for pure refactors, docs or cosmetic changes unless they unblock another issue.
