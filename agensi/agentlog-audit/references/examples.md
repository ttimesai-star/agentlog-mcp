# Examples

The sentences below are real outputs of the agentlog server (from its README demo and from the end-to-end check of this skill), not mock-ups.

## 1. A clean run

Agent logs `run.start`, one `tool.call`, `run.end`. Later `verify_run` says:

> The log is intact: all 3 steps are signed by the agent, linked, and sealed.

## 2. A run that never finished

Agent logs `run.start` and one `tool.call`, then stops. `verify_run` says:

> The log is intact so far, 2 steps, but the run was never sealed, so it may have stopped early.

Your answer to the user: nothing was altered, but the run did not finish. Do not call it intact without that caveat.

## 3. A tampered run

Someone rewrote the failed health check (`503`) to `200` in the server's database. `audit_day` says:

> Yesterday, release-checker ran 3 times, 18 logged steps in total. Warning: one log was tampered with. In the run at 1:05 PM, "Check release v1.4.3 before deploy", step 2 cannot be trusted: its content was edited after the agent signed it. The other 2 runs are unchanged.

Your answer to the user: repeat the warning, name the run and the step, and offer `get_run` so they can re-verify the export offline. Do not accuse anyone: the verifier proves a change, not its author.

## 4. A dispute

Client: "your agent got a 503, and you changed the log." Operator: "it was a 200." Call `diff_versions` with the client's own copy of step 2:

```json
{ "agent_id": "release-checker", "run_id": "<id>", "steps": [2],
  "client": { "entries": [ { "step": 2, "raw": { "output": { "status": 503 } } } ] } }
```

Read the per-step verdict as is: `client` means the client's version matches what the agent signed, `operator` means the operator's does.

## 5. "Can I trust this log?"

Answer from the tool result only. If no tool was called in this conversation, call `audit_day` or `verify_run` first. Then state the verdict, the limit (a holder of both the key and the file can rewrite a whole run; Arkiv mode closes that), and nothing more.
