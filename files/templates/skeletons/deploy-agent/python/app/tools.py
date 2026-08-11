"""Tools for ${{ values.name }} — selected by AGENT_TYPE."""
from __future__ import annotations

import json
import os
from typing import Any

import httpx
from langchain_core.tools import tool

from . import config


def _ns() -> str:
    return os.environ.get("NAMESPACE") or open(
        "/var/run/secrets/kubernetes.io/serviceaccount/namespace"
    ).read().strip()


def _k8s_headers() -> dict[str, str]:
    token = open("/var/run/secrets/kubernetes.io/serviceaccount/token").read().strip()
    return {"Authorization": f"Bearer {token}", "Accept": "application/json"}


@tool
def list_pods() -> str:
    """List pods in the current OpenShift namespace."""
    ns = _ns()
    url = f"https://kubernetes.default.svc/api/v1/namespaces/{ns}/pods"
    try:
        with httpx.Client(verify="/var/run/secrets/kubernetes.io/serviceaccount/ca.crt", timeout=30) as client:
            resp = client.get(url, headers=_k8s_headers())
            resp.raise_for_status()
            items = resp.json().get("items", [])
            rows = [
                {
                    "name": i["metadata"]["name"],
                    "phase": i.get("status", {}).get("phase"),
                    "ready": sum(
                        1
                        for c in i.get("status", {}).get("containerStatuses", []) or []
                        if c.get("ready")
                    ),
                }
                for i in items
            ]
            return json.dumps({"namespace": ns, "pods": rows}, indent=2)
    except Exception as exc:
        return json.dumps({"error": str(exc), "namespace": ns})


@tool
def get_deployment(name: str) -> str:
    """Get a Deployment by name in the current namespace."""
    ns = _ns()
    url = f"https://kubernetes.default.svc/apis/apps/v1/namespaces/{ns}/deployments/{name}"
    try:
        with httpx.Client(verify="/var/run/secrets/kubernetes.io/serviceaccount/ca.crt", timeout=30) as client:
            resp = client.get(url, headers=_k8s_headers())
            if resp.status_code == 404:
                return json.dumps({"error": "not found", "name": name, "namespace": ns})
            resp.raise_for_status()
            d = resp.json()
            return json.dumps(
                {
                    "name": d["metadata"]["name"],
                    "replicas": d.get("spec", {}).get("replicas"),
                    "available": d.get("status", {}).get("availableReplicas"),
                    "image": (d.get("spec", {}).get("template", {}).get("spec", {}).get("containers") or [{}])[0].get(
                        "image"
                    ),
                },
                indent=2,
            )
    except Exception as exc:
        return json.dumps({"error": str(exc)})


@tool
def lookup_cve(cve_id: str) -> str:
    """Look up a CVE using the public Red Hat Security Data API."""
    cve_id = cve_id.strip().upper()
    url = f"https://access.redhat.com/hydra/rest/securitydata/cve/{cve_id}.json"
    try:
        with httpx.Client(timeout=30) as client:
            resp = client.get(url)
            if resp.status_code == 404:
                return json.dumps({"error": "CVE not found in Red Hat data", "cve_id": cve_id})
            resp.raise_for_status()
            data = resp.json()
            return json.dumps(
                {
                    "cve_id": cve_id,
                    "threat_severity": data.get("threat_severity_rating") or data.get("severity"),
                    "cvss3": data.get("cvss3"),
                    "statement": (data.get("statement") or "")[:500],
                    "affected": [
                        {"package": p.get("package_name"), "product": p.get("product_name")}
                        for p in (data.get("affected_release") or [])[:8]
                    ],
                },
                indent=2,
            )
    except Exception as exc:
        return json.dumps({"error": str(exc), "cve_id": cve_id})


@tool
def check_lifecycle(product: str, version: str = "") -> str:
    """Check Red Hat product lifecycle status via the public lifecycle API."""
    url = "https://access.redhat.com/product-life-cycles/api/v1/products"
    try:
        with httpx.Client(timeout=30) as client:
            resp = client.get(url)
            resp.raise_for_status()
            products = resp.json().get("data") or resp.json()
            if not isinstance(products, list):
                products = []
            matches = []
            needle = product.lower()
            for p in products:
                name = (p.get("name") or p.get("product_name") or "")
                if needle in name.lower():
                    matches.append(p)
            if not matches:
                return json.dumps({"error": "product not found", "product": product, "hint": "try exact product name"})
            # Prefer first match; filter versions if provided
            selected = matches[0]
            versions = selected.get("versions") or selected.get("product_versions") or []
            if version and isinstance(versions, list):
                versions = [v for v in versions if version in str(v.get("name") or v)]
            return json.dumps(
                {
                    "product": selected.get("name") or selected.get("product_name"),
                    "version_filter": version or None,
                    "versions": versions[:10] if isinstance(versions, list) else versions,
                },
                indent=2,
                default=str,
            )
    except Exception as exc:
        return json.dumps({"error": str(exc), "product": product})


@tool
def search_docs(query: str) -> str:
    """Lightweight doc search stub for rag-agent demos (returns curated hints)."""
    hints = [
        "Use Developer Hub Lightspeed for MCP tool-calling against the namespace.",
        "LiteLLM aliases: granite, qwen3, litemaas-qwen.",
        "Red Hat agentic skills: https://www.redhat.com/en/agentic-skills",
        "Prefer list/get before mutate in OpenShift.",
    ]
    q = query.lower()
    hits = [h for h in hints if any(w in h.lower() for w in q.split() if len(w) > 2)]
    return json.dumps({"query": query, "hits": hits or hints[:2]}, indent=2)


def tools_for_agent_type(agent_type: str | None = None) -> list[Any]:
    agent_type = (agent_type or config.AGENT_TYPE or "tool-agent").lower()
    if agent_type == "chat-agent":
        return []
    if agent_type == "rag-agent":
        return [search_docs, check_lifecycle]
    # tool-agent (default): k8s + Red Hat security/lifecycle
    return [list_pods, get_deployment, lookup_cve, check_lifecycle]
