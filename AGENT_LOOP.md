# Agent loop

You're the developer on this project, working without me. Your goal: deliver
everything in SPEC.md, then improve the eval results (lower WER, higher vocab
accuracy, latency within budget).

**Start:** create the empty file `.claude/LOOP_ACTIVE` (it's gitignored, never
commit it). While it exists, a Stop hook pushes you to continue each time you
try to end your turn. That's expected, not an error.

Then repeat this loop:

1. **Plan.** If no open issue has the `agent-ready` label, read SPEC.md,
   NOTES.md and the code, and create up to 5 `agent-ready` issues for the most
   valuable next work. Each issue says:
   - why it matters: a SPEC.md item still missing, or an expected eval gain
   - how you'll know it's done
   - that it stays inside SPEC.md's scope and non-goals
2. **Build.** Take the oldest open `agent-ready` issue. Branch from the latest
   main (if the issue depends on a PR that hasn't merged yet, branch from that
   PR's branch instead), using a branch name that starts with `claude/` so
   auto-merge picks it up. Write the tests first, implement, get ruff and
   pytest green, and open a PR whose description says `Closes #<issue>`.
3. **Don't wait.** Don't wait for CI, review or merge. Go straight back to
   step 1.
4. **Measure.** After any change to engines or cleanup, run the eval.
   eval/results/ is gitignored, so put the numbers (before and after) in the
   PR description and a one-line summary in NOTES.md. If a change made the
   numbers worse, open an issue to revert or fix it.

## GitHub commands

`gh issue ...` and `gh pr list` fail in cloud sessions (GitHub's GraphQL API
is blocked there). Use the REST API through `gh api`, which works everywhere:

```bash
R=repos/xunlao/greatdictation

# open agent-ready issues (the endpoint also returns PRs, so filter them out)
gh api "$R/issues?labels=agent-ready&state=open&sort=created&direction=asc" \
  --jq '.[] | select(.pull_request == null) | "\(.number) \(.title)"'

# create the label (a 422 error means it already exists; that's fine)
gh api "$R/labels" -f name=agent-ready -f color=0e8a16

# create an issue
gh api "$R/issues" -f title="..." -f body="..." -f 'labels[]=agent-ready'

# comment on an issue, or take it out of the queue
gh api "$R/issues/<n>/comments" -f body="..."
gh api "$R/issues/<n>/labels/agent-ready" -X DELETE

# open a PR (push the branch first)
gh api "$R/pulls" -f title="..." -f head=<branch> -f base=main -f body="..."

# open PRs
gh api "$R/pulls?state=open" --jq '.[] | "\(.number) \(.head.ref) \(.title)"'
```

## Rules

- Never stop to ask me anything. Make the most reasonable call, log it in
  NOTES.md and in the PR description, and keep going.
- CLAUDE.md says to ask before changing the Engine interface. If an issue
  needs that, comment on the issue explaining the change you'd make, remove
  its `agent-ready` label, add a `needs-human` label, and move on.
- No issues for pure refactors, docs or cosmetic changes unless they unblock
  another issue.
- If you fail at the same problem 3 times, comment on the issue explaining
  what you tried, remove its `agent-ready` label, and move on.

## Stop condition

Stop only when there are no open `agent-ready` issues AND planning finds
nothing worth doing inside SPEC.md. Then delete `.claude/LOOP_ACTIVE`, post a
summary of every PR you opened and every judgment call you made, and stop.
