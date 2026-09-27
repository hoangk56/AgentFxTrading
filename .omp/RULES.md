# AgentFxTrading — OMP sticky rules

The delivery rules live in `../AGENTS.md` and are the only source of truth. In short:

1. Run the tests (`pytest` from the repo root; research changes also need
   `research/.venv/bin/python -m pytest research/tests`).
2. **Never commit or push on your own.** Leave the changes in the working tree, report what changed and the
   test result, and wait for the user to ask. When asked, push the current branch, not `main`.
3. On the VPS, restart `agentfx.service` if `app/`, `templates/` or `static/` changed, and the affected
   `cbot-*` container if `cBot/*.cs` or bot parameters changed.
