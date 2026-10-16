# Tool reference

All tools are on the agentlog MCP server. Ids (`agent_id`, `run_id`) are short labels: letters, digits, dots, dashes, underscores, colons (1 to 64 characters).

## log_action (writes)

Append one signed step to a run. Omit `run_id` to start a new run; the response carries the `run_id` to reuse.

| Field | Required | Meaning |
|---|---|---|
| `agent_id` | yes | stable name of the agent, e.g. `release-checker` |
| `run_id` | no | run to append to; omit to start a new one |
| `action` | yes | `run.start`, `tool.call`, `llm.call`, `tool.error`, `run.end`, or your own verb (max 64 chars) |
| `tool` | no | tool or model name |
| `input`, `output` | no | any JSON; kept as private evidence, only hashes enter the chain |
| `note` | no | short public label, max 280 chars. On `run.start`: the task. No secrets, no personal data |

`run.end` seals the run: it commits to the step count and the head hash.

## audit_day (read-only)

"What did my agent do yesterday, and was the log changed?" Lists the day's runs in the user's time zone, verifies each, returns a spoken summary that leads with the verdict, plus an audit card for hosts that render MCP Apps.

| Field | Meaning |
|---|---|
| `agent_id` | optional; omit to audit every agent |
| `date` | `yesterday` (default), `today`, or `YYYY-MM-DD` |
| `tz` | IANA time zone, e.g. `Europe/Berlin` |
| `source` | `local` (default) or `arkiv` |

## verify_run (read-only)

Recompute every hash and signature of one run and follow the links from step 0. Needs `agent_id` and `run_id` (optional `source`). Verdict: `intact`, `open`, `broken`. For `broken`, `explain.first_break` gives the step and the kind of break: edited, deleted, forked, re-signed by a foreign key, bad signature, or written after the seal.

## list_runs (read-only)

Runs of an agent, optionally of one day. Fields: `agent_id`, `date`, `tz`, `source`, `limit` (1 to 200).

## get_run (read-only)

The run as an `agentlog-export/v1` bundle anyone can re-verify offline. Fields: `agent_id`, `run_id`, `source`, `include_raw` (adds the private inputs and outputs; ask the user first).

## diff_versions (read-only)

Two parties disagree about what the agent did. Checks each party's raw version of the disputed steps against what the agent signed.

| Field | Meaning |
|---|---|
| `agent_id`, `run_id` | the run |
| `client` | the client's version: `{ entries: [{ step, raw: { input?, output? }, claim? }] }` |
| `operator` | optional operator version, same shape; defaults to the server's own copy |
| `steps` | optional list of step numbers to check |

Verdict per step: `operator`, `client`, `both`, `neither`, `no_anchor` (the chain holds no hash for that step).
