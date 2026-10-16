// Create the SKILL.md example run, tamper step 1 in SQLite, restart server, ask audit_day. Usage: node tamper_check.mjs <port> <phase> <run_id?>
import { Client } from "@modelcontextprotocol/sdk/client/index.js"
import { StreamableHTTPClientTransport } from "@modelcontextprotocol/sdk/client/streamableHttp.js"
const [port, phase, runArg] = process.argv.slice(2)
const c = new Client({ name: "tamper-check", version: "1" })
await c.connect(new StreamableHTTPClientTransport(new URL(`http://127.0.0.1:${port}/mcp`)))
const call = async (name, args) => { const r = await c.callTool({ name, arguments: args }); if (r.isError) throw new Error(r.content[0].text); return r }
const agent_id = "release-checker"
if (phase === "seed") {
  const s = await call("log_action", { agent_id, action: "run.start", note: "Check release v1.4.4" })
  const run_id = s.structuredContent.run_id
  await call("log_action", { agent_id, run_id, action: "tool.call", tool: "http_get", input: { url: "https://staging.example/health" }, output: { status: 503 } })
  await call("log_action", { agent_id, run_id, action: "run.end", output: { result: "blocked: health check 503" } })
  console.log(run_id)
} else {
  console.log((await call("audit_day", { date: "today", tz: "Europe/Berlin" })).content[0].text)
  console.log((await call("verify_run", { agent_id, run_id: runArg })).content[0].text)
}
await c.close()
