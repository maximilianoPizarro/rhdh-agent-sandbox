"""${{ values.name }} — LangGraph agent with HTTP API."""
from __future__ import annotations

import json
import logging
import time
import uuid
from typing import Annotated, Any, TypedDict

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages

from . import config
from .tools import tools_for_agent_type

logging.basicConfig(level=getattr(logging, config.LOG_LEVEL, logging.INFO), format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("agent")

TOOLS = tools_for_agent_type(config.AGENT_TYPE)
TOOL_MAP = {t.name: t for t in TOOLS}


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    reply: str


def _llm() -> ChatOpenAI:
    llm = ChatOpenAI(
        model=config.MODEL,
        api_key=config.LITELLM_API_KEY or "unused",
        base_url=config.LITELLM_API_BASE,
        temperature=0.2,
    )
    if TOOLS:
        return llm.bind_tools(TOOLS)
    return llm


def parse_input(state: AgentState) -> dict[str, Any]:
    return {}


def call_llm(state: AgentState) -> dict[str, Any]:
    llm = _llm()
    system = SystemMessage(
        content=(
            f"You are agent {config.NAME} ({config.FRAMEWORK}/{config.LANGUAGE}). "
            f"Agent type: {config.AGENT_TYPE}. Specification: {config.AGENT_SPEC}"
        )
    )
    messages = [system] + list(state["messages"])
    response = llm.invoke(messages)
    return {"messages": [response]}


def maybe_tools(state: AgentState) -> str:
    last = state["messages"][-1]
    if isinstance(last, AIMessage) and getattr(last, "tool_calls", None):
        return "tools"
    return "respond"


def run_tools(state: AgentState) -> dict[str, Any]:
    last = state["messages"][-1]
    outs: list[ToolMessage] = []
    for tc in last.tool_calls or []:
        name = tc.get("name")
        args = tc.get("args") or {}
        tool = TOOL_MAP.get(name)
        if not tool:
            content = json.dumps({"error": f"unknown tool {name}"})
        else:
            try:
                content = tool.invoke(args)
            except Exception as exc:
                content = json.dumps({"error": str(exc)})
        outs.append(ToolMessage(content=str(content), tool_call_id=tc.get("id", name)))
    return {"messages": outs}


def format_response(state: AgentState) -> dict[str, Any]:
    last = state["messages"][-1]
    text = getattr(last, "content", None) or str(last)
    if isinstance(text, list):
        text = " ".join(str(x) for x in text)
    return {"reply": str(text)}


def build_graph():
    g = StateGraph(AgentState)
    g.add_node("parse", parse_input)
    g.add_node("llm", call_llm)
    g.add_node("tools", run_tools)
    g.add_node("respond", format_response)
    g.set_entry_point("parse")
    g.add_edge("parse", "llm")
    g.add_conditional_edges("llm", maybe_tools, {"tools": "tools", "respond": "respond"})
    g.add_edge("tools", "llm")
    g.add_edge("respond", END)
    return g.compile()


GRAPH = build_graph()
app = FastAPI(title=config.NAME)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
@app.get("/healthz")
def health():
    return {"status": "ok", "framework": config.FRAMEWORK, "language": config.LANGUAGE}


@app.get("/")
def root():
    return {
        "service": config.NAME,
        "framework": config.FRAMEWORK,
        "language": config.LANGUAGE,
        "model": config.MODEL,
        "agentType": config.AGENT_TYPE,
        "agentSpec": config.AGENT_SPEC,
        "tools": list(TOOL_MAP.keys()),
    }


@app.get("/v1/graph")
def graph_info():
    return {
        "nodes": ["parse", "llm", "tools", "respond"],
        "edges": [
            "parse->llm",
            "llm->tools|respond",
            "tools->llm",
            "respond->END",
        ],
        "framework": "langgraph",
    }


@app.post("/v1/chat")
async def chat(request: Request):
    rid = request.headers.get("X-Request-Id") or uuid.uuid4().hex[:12]
    started = time.monotonic()
    body = await request.json()
    user = body.get("message") or body.get("prompt") or ""
    log.info("chat_start request_id=%s chars=%s model=%s", rid, len(user), config.MODEL)
    try:
        result = GRAPH.invoke({"messages": [HumanMessage(content=user)], "reply": ""})
        reply = result.get("reply") or ""
        ms = int((time.monotonic() - started) * 1000)
        log.info("chat_ok request_id=%s duration_ms=%s", rid, ms)
        return JSONResponse(
            {
                "reply": reply,
                "model": config.MODEL,
                "framework": config.FRAMEWORK,
                "requestId": rid,
            }
        )
    except Exception as exc:
        log.exception("chat_failed request_id=%s", rid)
        return JSONResponse({"error": str(exc), "requestId": rid}, status_code=502)


log.info(
    "agent_started name=%s framework=%s language=%s model=%s agent_type=%s tools=%s",
    config.NAME,
    config.FRAMEWORK,
    config.LANGUAGE,
    config.MODEL,
    config.AGENT_TYPE,
    list(TOOL_MAP.keys()),
)
