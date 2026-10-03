#!/usr/bin/env python3
"""Stop hook: keep the agent working through AGENT_LOOP.md instead of
stopping after each PR.

It does nothing unless the loop is on: AGENT_LOOP.md tells the agent to
create .claude/LOOP_ACTIVE (gitignored) when it starts. That keeps ordinary
sessions and the GitHub Actions review/fix runs from being pushed to loop.

While the loop is on, each attempt to end the turn is blocked and the agent
is told to continue, until either:
  - the agent deletes .claude/LOOP_ACTIVE (the loop's stop condition was met), or
  - this session has been pushed AGENT_LOOP_MAX_CONTINUES times (default 40),
    a cap that keeps a stuck agent from looping forever.
"""
import json
import os
import pathlib
import sys

data = json.load(sys.stdin)
project = pathlib.Path(os.environ.get("CLAUDE_PROJECT_DIR", "."))

if not (project / ".claude" / "LOOP_ACTIVE").exists():
    sys.exit(0)

max_continues = int(os.environ.get("AGENT_LOOP_MAX_CONTINUES", "40"))
session_id = data.get("session_id", "default")
counter = pathlib.Path(f"/tmp/agent-loop-{session_id}.count")
count = int(counter.read_text()) if counter.exists() else 0

if count >= max_continues:
    sys.exit(0)

counter.write_text(str(count + 1))
print(
    json.dumps(
        {
            "decision": "block",
            "reason": (
                f"Keep going (continuation {count + 1}/{max_continues}). "
                "Follow AGENT_LOOP.md: pick the next agent-ready issue, or plan "
                "new ones if none are open, and continue. Don't wait for PRs to "
                "merge. Only if AGENT_LOOP.md's stop condition is met: delete "
                ".claude/LOOP_ACTIVE, post your final summary, then stop."
            ),
        }
    )
)
