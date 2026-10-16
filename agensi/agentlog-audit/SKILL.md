---
name: agentlog-audit
description: Makes your agent keep a tamper-evident, signed log of its own actions through the agentlog MCP server, and answers "what did my agent do yesterday, and was the log changed?". Use when you run tools on a user's behalf and may have to prove what happened, when a user asks to audit, verify or replay an agent run, or when two parties dispute what an agent did.
when_to_use: |
  - You are about to run a multi-step task for a user (release check, refund, data change, message sending) and the steps may need to be proven later
  - User asks "what did my agent do yesterday / today / on <date>", "was the log tampered with", "is this run intact", "audit my agent"
  - Operator and client disagree about what an agent did or returned
  - User asks for an audit trail, action log, evidence, non-repudiation or a compliance log for an AI agent
  - Do NOT use for ordinary application logging, metrics, or tracing dashboards (this is evidence, not observability)
---

# agentlog-audit

The agentlog MCP server (`agentlog-mcp`, MIT, open source) records every step of an agent run as a signed, hash-chained entry. If anyone edits, deletes, reorders or re-signs a step afterwards, the verifier says which step and how. This skill tells you when to write to that log, when to read it, and what you may and may not claim.

Tools: `log_action`, `audit_day`, `verify_run`, `list_runs`, `get_run`, `diff_versions`.

## Step 0: check the server is connected

Look for the tools above in your tool list. If they are missing, do not pretend to log. Tell the user the agentlog MCP server is not connected and point them to `references/setup.md` (about 3 minutes: Node 22.18+, one clone, one start command, one config line). Continue the user's task without logging only if the user agrees.

## When you are the agent doing the work

1. Pick a stable `agent_id` (for example `release-checker`: lowercase, no spaces). Keep it the same across days so the verifier can match the key.
2. Start: `log_action` with `action: "run.start"` and the task in `note`. Keep the returned `run_id`.
3. After every tool call or model call that matters, `log_action` with the same `agent_id` and `run_id`:
   - `action: "tool.call"`, `tool`: tool name, `input`: arguments, `output`: result;
   - `action: "llm.call"` for a model call, `tool`: model name;
   - `action: "tool.error"` when a call failed, the error as `output`.
4. Finish: `log_action` with `action: "run.end"` and the final result as `output`. This seals the run. A run without a seal is reported as "open", so nobody can pass a cut-off run off as complete.
5. Log failures too. A log that only records successes is not evidence.

Privacy rules (hard):
- `note`, `agent_id`, `run_id` and `action` are public labels. Never put secrets, tokens, passwords or personal data there.
- Raw `input` and `output` stay on the server as private evidence; only their hashes enter the chain. Still, do not pass secrets in them.

## When the user asks about an agent

| User asks | Call | Notes |
|---|---|---|
| "What did my agent do yesterday, and was the log changed?" | `audit_day` | Default date is yesterday. Pass `tz` (IANA, e.g. `Europe/Berlin`) when you know the user's time zone. Read the returned text as is: it leads with the verdict. |
| "Is run X intact?" | `verify_run` | Needs `agent_id` and `run_id`. Use `list_runs` first if the user does not know the id. |
| "Which runs did agent A have today?" | `list_runs` | Optional `date`. |
| "Give me the evidence to check this myself" | `get_run` | Returns an `agentlog-export/v1` bundle that can be re-verified offline. `include_raw` adds private inputs and outputs: ask the user before using it. |
| "The client says the check returned 200, the operator says 503. Who is right?" | `diff_versions` | Pass the client's own copy of the disputed steps. Verdict per step: `operator`, `client`, `both`, `neither`, `no_anchor`. |

## Verdicts and what you may say

| Verdict | Meaning | You may say |
|---|---|---|
| intact | every step signed by the agent's key, linked from step 0, run sealed | "The log is intact: no step was changed after the agent signed it." |
| open | everything checks out so far, but the run never got `run.end` | "Nothing was altered, but the run never finished, so it may have stopped early." Never call it intact. |
| broken | a step was edited, deleted, re-signed by another key, or written after the seal | Name the step and the kind of break from `explain.first_break`. Say that this step cannot be trusted. |

Rules:
1. Never say a log is intact unless `verify_run` or `audit_day` said so in this conversation. No tool result, no verdict.
2. Do not guess why a break happened. The verifier proves that something changed, not who changed it or why.
3. Know the limit and say it when asked: someone who holds both the agent's key and the log file can rewrite a whole run consistently. Writing to the public Arkiv network (readonly entries) closes that gap; see `references/setup.md`. A log also cannot prove that an agent told the truth at the moment it wrote.
4. If a tool returns an error, show the error text to the user. Do not retry with invented ids.

## Example

User: "Check the release for v1.4.4, and keep a log I can show the client."

1. `log_action` `{ "agent_id": "release-checker", "action": "run.start", "note": "Check release v1.4.4" }` returns `run_id`.
2. You call the staging health endpoint. Then `log_action` `{ "agent_id": "release-checker", "run_id": "<id>", "action": "tool.call", "tool": "http_get", "input": {"url": "https://staging.example/health"}, "output": {"status": 503} }`.
3. You block the release and report why. `log_action` `{ ..., "action": "run.end", "output": {"result": "blocked: health check 503"} }`.
4. Next day the user asks: "What did release-checker do yesterday, and was the log changed?" You call `audit_day` and read the answer as is, for example: "Yesterday, release-checker ran 1 time, 3 logged steps in total. No log was tampered with."

More examples (dispute, broken run, open run) are in `references/examples.md`. The full tool and field reference is in `references/tool-reference.md`.

## Boundaries

- This skill only reads and writes the agentlog log. It does not change files, run shell commands, or contact any service except the agentlog server the user connected.
- Do not log on a user's behalf in a way they did not agree to: if the user did not ask for an audit trail, say you can keep one and ask.
- Source and issues: https://github.com/ttimesai-star/agentlog-mcp
