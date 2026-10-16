"""Text of the Agensi listing for agentlog-audit. Every sentence in sample_output is a real output of the server
(see verify/skill_e2e.mjs and the README demo)."""

NAME = "Agent Action Log: tamper-evident audit trail for AI agents"

SUMMARY = ("Your agent logs every step into a signed, hash-chained record, then answers "
           "'what did my agent do yesterday, and was the log changed?' with proof.")

DESCRIPTION = """\
## What it does

AI agents now run tools that matter: they approve releases, issue refunds, send messages, change records. What an agent did is usually kept in a log on the operator's server, and after an incident that log is the only evidence, held by the party with the most reason to change it.

This skill makes your agent keep that evidence properly. It drives the free, open-source **agentlog MCP server** (MIT): every step of a run (tool call, model call, error, end of run) is hashed, signed with the agent's key and linked to the step before it. If anyone edits, deletes, reorders or re-signs a step afterwards, the verifier says **which step and how**.

## What the skill teaches your agent

- **When to log:** at the start of a multi-step task, after every tool or model call, on errors, and at the end (the end seals the run, so a cut-off run shows as *open*, never as complete).
- **When to read:** "what did my agent do yesterday?", "was the log tampered with?", "is run X intact?", "who is right, the client or the operator?".
- **What it may claim:** never "intact" unless a verify tool said so in this conversation; "open" is not "intact"; it proves a change, not who made it.
- **Privacy:** no secrets or personal data in the public labels (`note`, `agent_id`, `run_id`). Raw inputs and outputs stay on your server; only hashes enter the chain.

## What is in the package

- `SKILL.md`: triggers, the logging routine, the audit routine, verdict wording, boundaries, one worked example.
- `references/setup.md`: connect the server in about 3 minutes (Node.js 22.18+, one clone, one start command).
- `references/tool-reference.md`: the six tools (`log_action`, `audit_day`, `verify_run`, `list_runs`, `get_run`, `diff_versions`) and their fields.
- `references/examples.md`: clean, open, tampered and disputed runs with real outputs.

## Honest limits

- It needs the agentlog MCP server running (free, MIT, local SQLite). The skill alone does not log anything.
- Someone who holds both the agent's key and the log file can rewrite a whole run consistently. The server can also write to the public Arkiv network (read-only entries) to close that gap; this is optional and uses a test key.
- A log cannot prove that an agent told the truth at the moment it wrote.
- Checked end to end with the official MCP TypeScript SDK client against a live server (log, verify open and sealed run, list, daily audit, export, dispute replay). Not yet tried inside every individual agent listed in the compatibility strip.

Source, tests (66 passing) and demo video: https://github.com/ttimesai-star/agentlog-mcp
"""

SAMPLE_INPUT = ("Check release v1.4.4 against the staging health endpoint. Keep a log I can show the client, "
                "and tomorrow I will ask what you did.")

SAMPLE_OUTPUT = """\
## Summary

Release v1.4.4 is blocked: staging health returned 503. The run is logged and sealed: 3 signed steps.

## What the agent logged (agentlog MCP server)

| Step | Call | Content |
|---|---|---|
| 0 | `log_action` action `run.start` | note: "Check release v1.4.4" |
| 1 | `log_action` action `tool.call`, tool `http_get` | input `{"url": "https://staging.example/health"}`, output `{"status": 503}` |
| 2 | `log_action` action `run.end` | output `{"result": "blocked: health check 503"}` |

Only the hashes of input and output enter the chain; the raw data stays on your server as private evidence.

## Next day: "What did release-checker do yesterday, and was the log changed?"

The agent calls `audit_day` and reads the answer as is:

> Yesterday, release-checker ran 1 time, 3 logged steps in total. The task was: Check release v1.4.4. Every log is intact: signed by the agent, linked, and sealed.

## If someone rewrites the 503 to 200 in the database

The same question now returns:

> Yesterday, release-checker ran 1 time, 3 logged steps in total. The task was: Check release v1.4.4. Warning: one log was tampered with. In the run at 5:08 PM, "Check release v1.4.4", step 1 cannot be trusted: its content was edited after the agent signed it.

## Next steps

- `get_run` returns an export anyone can re-verify offline.
- If the client and the operator disagree about the 503, `diff_versions` replays each side's copy against what the agent signed and says who is right.
"""

COMPAT = ("Needs the free agentlog MCP server (Node.js 22.18+) connected to your agent over Streamable HTTP or stdio. "
          "Verified end to end with the official MCP TypeScript SDK client; not yet tested in each individual agent.")

REQUIREMENTS = "agentlog-mcp (free MCP server, MIT)\nNode.js 22.18 or newer"

PERM_NOTES = ("Instructions only: the package has no scripts. The skill makes your agent call the agentlog MCP server "
              "you connected yourself (local by default, 127.0.0.1). It does not touch files, run commands or contact "
              "any other service.")

DOC_LINK = "https://github.com/ttimesai-star/agentlog-mcp"
DEMO_VIDEO = "https://youtu.be/SgZo5ZqYfaM"

FAQ = [
    ("Does this skill log anything by itself?",
     "No. It tells your agent how to use the agentlog MCP server. Connect that server first (references/setup.md, about 3 minutes)."),
    ("Does the log leave my machine?",
     "No, by default. State is a local SQLite file and one key per agent. Writing to the public Arkiv network is optional and only hashes and signatures go there."),
    ("Can it prove who changed a log?",
     "No. It proves that a step was edited, deleted, reordered or re-signed, and which step. It does not identify the author of the change."),
]
