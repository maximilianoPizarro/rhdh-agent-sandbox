/** Runtime config for ${{ values.name }} (LangChain.js). */
export const NAME = process.env.AGENT_NAME || "${{ values.name }}";
export const LANGUAGE = process.env.LANGUAGE || "nodejs";
export const FRAMEWORK = process.env.FRAMEWORK || "langchain-js";
export const AGENT_TYPE = process.env.AGENT_TYPE || "${{ values.agentType }}";
// Prefer Deployment env AGENT_SPEC (set by agent-applier from Component annotations).
export const AGENT_SPEC =
  process.env.AGENT_SPEC ||
  "You are a helpful namespace-scoped LangChain.js agent on Developer Sandbox.";
export const MODEL = process.env.MODEL || "${{ values.model }}";
export const LITELLM_API_BASE = (
  process.env.LITELLM_API_BASE || "http://rhdh-agent-sandbox-litellm:4000/v1"
).replace(/\/$/, "");
export const LITELLM_API_KEY = process.env.LITELLM_API_KEY || "";
export const LOG_LEVEL = (process.env.LOG_LEVEL || "INFO").toUpperCase();
export const PORT = Number(process.env.PORT || "8080");
