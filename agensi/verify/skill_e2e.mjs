// Follows agensi/agentlog-audit/SKILL.md step by step against a live agentlog-mcp server.
// Usage: node agensi/verify/skill_e2e.mjs http://127.0.0.1:8799/mcp
import { Client } from "@modelcontextprotocol/sdk/client/index.js"
import { StreamableHTTPClientTransport } from "@modelcontextprotocol/sdk/client/streamableHttp.js"
const url = process.argv[2]
const c = new Client({ name: "skill-e2e", version: "1" })
await c.connect(new StreamableHTTPClientTransport(new URL(url)))
const tools = (await c.listTools()).tools.map((t) => t.name).sort()
const want = ["audit_day", "diff_versions", "get_run", "list_runs", "log_action", "verify_run"]
if (JSON.stringify(tools) !== JSON.stringify(want)) throw new Error("tools: " + tools)
const call = async (name, args) => { const r = await c.callTool({ name, arguments: args }); if (r.isError) throw new Error(name + ": " + r.content[0].text); return r }
const agent_id = "release-checker"
const s = await call("log_action", { agent_id, action: "run.start", note: "Check release v1.4.4" })
const run_id = s.structuredContent.run_id ?? s.structuredContent.entry?.run_id
if (!run_id) throw new Error("no run_id: " + JSON.stringify(s.structuredContent))
await call("log_action", { agent_id, run_id, action: "tool.call", tool: "http_get", input: { url: "https://staging.example/health" }, output: { status: 503 } })
// open run must not be called intact
const open = await call("verify_run", { agent_id, run_id })
console.log("OPEN  :", open.content[0].text)
if (!/never|open|not (been )?(sealed|finished)/i.test(open.content[0].text)) throw new Error("open run not reported as open")
await call("log_action", { agent_id, run_id, action: "run.end", output: { result: "blocked: health check 503" } })
const ok = await call("verify_run", { agent_id, run_id })
console.log("SEALED:", ok.content[0].text)
const lr = await call("list_runs", { agent_id, date: "today" })
console.log("LIST  :", lr.content[0].text.slice(0, 200))
const ad = await call("audit_day", { date: "today", tz: "Europe/Berlin" })
console.log("DAY   :", ad.content[0].text)
const gr = await call("get_run", { agent_id, run_id })
console.log("EXPORT:", Object.keys(gr.structuredContent).join(","), JSON.stringify(gr.structuredContent).length, "bytes")
const df = await call("diff_versions", { agent_id, run_id, steps: [1], client: { entries: [{ step: 1, raw: { input: { url: "https://staging.example/health" }, output: { status: 503 } } }] } })
console.log("DIFF  :", df.content[0].text)
if (!/both versions match/i.test(df.content[0].text)) throw new Error("diff_versions on an untampered run should say both versions match")
await c.close()
