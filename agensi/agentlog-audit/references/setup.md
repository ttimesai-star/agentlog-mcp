# Setup: connect the agentlog MCP server (about 3 minutes)

agentlog-mcp is a free, MIT-licensed MCP server. This skill only tells your agent how to use it. You need the server running once.

Requirements: Node.js 22.18 or newer, git.

## 1. Get and start the server

```bash
git clone https://github.com/ttimesai-star/agentlog-mcp.git
cd agentlog-mcp
npm install
npm start
```

The server listens on `http://127.0.0.1:8787/mcp` (loopback only). State is a local SQLite file in `.agentlog-mcp/`, plus one key per agent in `.agentlog-mcp/agent-keys.json` (git-ignored). Keep that folder; it is the log.

Optional demo with three sample runs and a tamper button: `npm run demo`, then open http://localhost:8787 in Chrome or Edge.

## 2. Tell your agent about it

Any client that speaks Streamable HTTP MCP uses the URL `http://127.0.0.1:8787/mcp`.

Claude Code:

```bash
claude mcp add --transport http agentlog http://127.0.0.1:8787/mcp
```

Clients that launch servers themselves (stdio): command `node`, arguments `--conditions=agentlog-source src/main.ts --stdio`, working directory = the cloned folder.

Check: your agent should now list the tools `log_action`, `audit_day`, `verify_run`, `list_runs`, `get_run`, `diff_versions`.

## 3. Useful settings (environment variables)

| Variable | Default | Use |
|---|---|---|
| `PORT`, `HOST` | `8787`, `127.0.0.1` | change the listen address |
| `AGENTLOG_TOKEN` | none | require a bearer token on `/mcp` (set it if you listen beyond loopback) |
| `AGENTLOG_TZ` | system time zone | what "yesterday" means when the client sends no `tz` |
| `AGENTLOG_DATA` | `./.agentlog-mcp` | where the log and keys live |

## 4. Optional: a log the operator cannot rewrite (Arkiv)

By default, someone who holds both the agent's key and the SQLite file can rewrite a whole run consistently. To close that gap, write steps to the public Arkiv network, where entries are read-only. Set `AGENTLOG_WRITE=arkiv` and `AGENTLOG_PRIVATE_KEY` (a funded Arkiv test key) before `npm start`.

Reading and verifying runs from Arkiv needs no key: call `verify_run` with `source: "arkiv"`. Raw inputs and outputs still stay in the local file; only hashes and signatures go to the network.

## Security notes

- Never put secrets or personal data in `note`, `agent_id` or `run_id`: they are public labels.
- Raw inputs and outputs never enter the hash chain, only their hashes.
- The server refuses requests without a valid session, from a foreign `Origin`, or with a foreign `Host`.
