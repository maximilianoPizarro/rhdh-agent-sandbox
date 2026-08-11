/** Tools for ${{ values.name }} — selected by AGENT_TYPE. */
import { DynamicStructuredTool } from "@langchain/core/tools";
import { z } from "zod";
import fs from "node:fs";
import * as config from "./config.js";

function ns() {
  if (process.env.NAMESPACE) return process.env.NAMESPACE;
  return fs.readFileSync("/var/run/secrets/kubernetes.io/serviceaccount/namespace", "utf8").trim();
}

function k8sHeaders() {
  const token = fs.readFileSync("/var/run/secrets/kubernetes.io/serviceaccount/token", "utf8").trim();
  return { Authorization: `Bearer ${token}`, Accept: "application/json" };
}

export const listPods = new DynamicStructuredTool({
  name: "list_pods",
  description: "List pods in the current OpenShift namespace",
  schema: z.object({}),
  func: async () => {
    const namespace = ns();
    const url = `https://kubernetes.default.svc/api/v1/namespaces/${namespace}/pods`;
    try {
      const resp = await fetch(url, { headers: k8sHeaders() });
      const data = await resp.json();
      const pods = (data.items || []).map((i) => ({
        name: i.metadata?.name,
        phase: i.status?.phase,
      }));
      return JSON.stringify({ namespace, pods }, null, 2);
    } catch (exc) {
      return JSON.stringify({ error: String(exc), namespace });
    }
  },
});

export const getDeployment = new DynamicStructuredTool({
  name: "get_deployment",
  description: "Get a Deployment by name in the current namespace",
  schema: z.object({ name: z.string() }),
  func: async ({ name }) => {
    const namespace = ns();
    const url = `https://kubernetes.default.svc/apis/apps/v1/namespaces/${namespace}/deployments/${name}`;
    try {
      const resp = await fetch(url, { headers: k8sHeaders() });
      if (resp.status === 404) return JSON.stringify({ error: "not found", name, namespace });
      const d = await resp.json();
      return JSON.stringify(
        {
          name: d.metadata?.name,
          replicas: d.spec?.replicas,
          available: d.status?.availableReplicas,
        },
        null,
        2
      );
    } catch (exc) {
      return JSON.stringify({ error: String(exc) });
    }
  },
});

export const lookupCve = new DynamicStructuredTool({
  name: "lookup_cve",
  description: "Look up a CVE using the public Red Hat Security Data API",
  schema: z.object({ cve_id: z.string() }),
  func: async ({ cve_id }) => {
    const id = cve_id.trim().toUpperCase();
    const url = `https://access.redhat.com/hydra/rest/securitydata/cve/${id}.json`;
    try {
      const resp = await fetch(url);
      if (resp.status === 404) return JSON.stringify({ error: "CVE not found", cve_id: id });
      const data = await resp.json();
      return JSON.stringify(
        {
          cve_id: id,
          threat_severity: data.threat_severity_rating || data.severity,
          statement: (data.statement || "").slice(0, 500),
        },
        null,
        2
      );
    } catch (exc) {
      return JSON.stringify({ error: String(exc), cve_id: id });
    }
  },
});

export const checkLifecycle = new DynamicStructuredTool({
  name: "check_lifecycle",
  description: "Check Red Hat product lifecycle status",
  schema: z.object({
    product: z.string(),
    version: z.string().optional().default(""),
  }),
  func: async ({ product, version }) => {
    const url = "https://access.redhat.com/product-life-cycles/api/v1/products";
    try {
      const resp = await fetch(url);
      const body = await resp.json();
      const products = body.data || body || [];
      const needle = product.toLowerCase();
      const matches = (Array.isArray(products) ? products : []).filter((p) =>
        String(p.name || p.product_name || "")
          .toLowerCase()
          .includes(needle)
      );
      if (!matches.length) return JSON.stringify({ error: "product not found", product });
      return JSON.stringify({ product: matches[0].name || matches[0].product_name, version_filter: version || null }, null, 2);
    } catch (exc) {
      return JSON.stringify({ error: String(exc), product });
    }
  },
});

export const searchDocs = new DynamicStructuredTool({
  name: "search_docs",
  description: "Lightweight doc search for rag-agent demos",
  schema: z.object({ query: z.string() }),
  func: async ({ query }) => {
    const hints = [
      "Use Developer Hub Lightspeed for MCP tool-calling.",
      "LiteLLM aliases: granite, qwen3, litemaas-qwen.",
      "Red Hat agentic skills: https://www.redhat.com/en/agentic-skills",
    ];
    return JSON.stringify({ query, hits: hints }, null, 2);
  },
});

export function toolsForAgentType(agentType = config.AGENT_TYPE) {
  const t = String(agentType || "tool-agent").toLowerCase();
  if (t === "chat-agent") return [];
  if (t === "rag-agent") return [searchDocs, checkLifecycle];
  return [listPods, getDeployment, lookupCve, checkLifecycle];
}
