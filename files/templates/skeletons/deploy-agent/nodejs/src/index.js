/**
 * ${{ values.name }} — LangChain.js agent HTTP server.
 */
import http from "node:http";
import { ChatOpenAI } from "@langchain/openai";
import { HumanMessage, SystemMessage } from "@langchain/core/messages";
import { createReactAgent } from "@langchain/langgraph/prebuilt";
import * as config from "./config.js";
import { toolsForAgentType } from "./tools.js";

const TOOLS = toolsForAgentType(config.AGENT_TYPE);

function log(level, msg, fields = {}) {
  const levels = { DEBUG: 10, INFO: 20, WARN: 30, ERROR: 40 };
  if ((levels[level] || 20) < (levels[config.LOG_LEVEL] || 20)) return;
  const extra = Object.entries(fields)
    .filter(([, v]) => v !== undefined && v !== "")
    .map(([k, v]) => `${k}=${v}`)
    .join(" ");
  console.log(`${new Date().toISOString()} ${level} ${msg}${extra ? " " + extra : ""}`);
}

function json(res, code, obj, requestId) {
  const body = JSON.stringify(obj);
  const headers = { "Content-Type": "application/json", "Content-Length": Buffer.byteLength(body) };
  if (requestId) headers["X-Request-Id"] = requestId;
  res.writeHead(code, headers);
  res.end(body);
}

async function readBody(req) {
  const chunks = [];
  for await (const c of req) chunks.push(c);
  const raw = Buffer.concat(chunks).toString("utf8") || "{}";
  return JSON.parse(raw);
}

function buildAgent() {
  const llm = new ChatOpenAI({
    modelName: config.MODEL,
    openAIApiKey: config.LITELLM_API_KEY || "unused",
    configuration: { baseURL: config.LITELLM_API_BASE },
    temperature: 0.2,
  });
  if (!TOOLS.length) {
    return {
      async invoke(input) {
        const messages = [
          new SystemMessage(
            `You are agent ${config.NAME} (${config.FRAMEWORK}). Type=${config.AGENT_TYPE}. ${config.AGENT_SPEC}`
          ),
          new HumanMessage(input.messages?.[0]?.content || input),
        ];
        const resp = await llm.invoke(messages);
        return { messages: [resp] };
      },
    };
  }
  return createReactAgent({ llm, tools: TOOLS });
}

const agent = buildAgent();

const server = http.createServer(async (req, res) => {
  const rid = req.headers["x-request-id"] || Math.random().toString(16).slice(2, 14);
  const url = new URL(req.url || "/", `http://${req.headers.host || "localhost"}`);

  if (req.method === "GET" && (url.pathname === "/health" || url.pathname === "/healthz")) {
    return json(res, 200, { status: "ok", framework: config.FRAMEWORK, language: config.LANGUAGE }, rid);
  }
  if (req.method === "GET" && url.pathname === "/") {
    return json(
      res,
      200,
      {
        service: config.NAME,
        framework: config.FRAMEWORK,
        language: config.LANGUAGE,
        model: config.MODEL,
        agentType: config.AGENT_TYPE,
        agentSpec: config.AGENT_SPEC,
        tools: TOOLS.map((t) => t.name),
        runtime: process.version,
      },
      rid
    );
  }
  if (req.method === "GET" && url.pathname === "/v1/runtime") {
    return json(res, 200, { runtime: "nodejs", version: process.version, framework: config.FRAMEWORK }, rid);
  }
  if (req.method === "POST" && url.pathname === "/v1/chat") {
    const started = Date.now();
    try {
      const body = await readBody(req);
      const user = body.message || body.prompt || "";
      log("INFO", "chat_start", { request_id: rid, chars: user.length, model: config.MODEL });
      const result = await agent.invoke({
        messages: [
          new SystemMessage(
            `You are agent ${config.NAME} (${config.FRAMEWORK}). Type=${config.AGENT_TYPE}. ${config.AGENT_SPEC}`
          ),
          new HumanMessage(user),
        ],
      });
      const msgs = result.messages || [];
      const last = msgs[msgs.length - 1];
      const reply = typeof last?.content === "string" ? last.content : JSON.stringify(last?.content ?? last);
      log("INFO", "chat_ok", { request_id: rid, duration_ms: Date.now() - started });
      return json(res, 200, { reply, model: config.MODEL, framework: config.FRAMEWORK, requestId: rid }, rid);
    } catch (exc) {
      log("ERROR", "chat_failed", { request_id: rid, error: String(exc) });
      return json(res, 502, { error: String(exc), requestId: rid }, rid);
    }
  }
  return json(res, 404, { error: "not found", requestId: rid }, rid);
});

server.listen(config.PORT, "0.0.0.0", () => {
  log("INFO", "agent_started", {
    port: config.PORT,
    framework: config.FRAMEWORK,
    language: config.LANGUAGE,
    model: config.MODEL,
    agent_type: config.AGENT_TYPE,
    tools: TOOLS.map((t) => t.name).join(","),
  });
});
