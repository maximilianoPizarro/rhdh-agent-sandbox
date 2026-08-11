"""Runtime configuration for ${{ values.name }} (LangGraph agent)."""
import os

NAME = os.environ.get("AGENT_NAME", "${{ values.name }}")
LANGUAGE = os.environ.get("LANGUAGE", "python")
FRAMEWORK = os.environ.get("FRAMEWORK", "langgraph")
AGENT_TYPE = os.environ.get("AGENT_TYPE", "${{ values.agentType }}")
# Prefer Deployment env AGENT_SPEC (set by agent-applier from Component annotations).
AGENT_SPEC = os.environ.get(
    "AGENT_SPEC",
    "You are a helpful namespace-scoped LangGraph agent on Developer Sandbox.",
)
MODEL = os.environ.get("MODEL", "${{ values.model }}")
LITELLM_API_BASE = os.environ.get("LITELLM_API_BASE", "http://rhdh-agent-sandbox-litellm:4000/v1").rstrip("/")
LITELLM_API_KEY = os.environ.get("LITELLM_API_KEY", "")
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
PORT = int(os.environ.get("PORT", "8080"))
