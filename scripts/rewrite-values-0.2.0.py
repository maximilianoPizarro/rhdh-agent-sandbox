#!/usr/bin/env python3
"""Rewrite values.yaml for chart 0.2.0 / RHDH 2.1."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
text = (ROOT / "values.yaml").read_text(encoding="utf-8")
start = text.index("catalog:")
end = text.index("# Subchart: official Red Hat Developer Hub")
middle = text[start:end]

header = r'''# Default values for rhdh-agent-sandbox (OpenShift Developer Sandbox only).
#
# Install (fresh install required for 0.2.0 / RHDH 2.1 — PG18 cannot reuse PG15 PVC):
#   helm uninstall rhdh-agent -n "$(oc project -q)"
#   oc delete pvc -l app.kubernetes.io/name=developer-hub --ignore-not-found
#   oc delete pvc data-rhdh-agent-sandbox-postgresql-0 --ignore-not-found
#   helm upgrade --install rhdh-agent . -n "$(oc project -q)" \
#     --set secrets.modelApiKey="$(oc whoami -t)" \
#     --set rhdh.openshift.clusterRouterBase=apps.rm2.thpm.p1.openshiftapps.com

nameOverride: ""
# Keep service DNS short and stable: <fullname>-mcp / <fullname>-litellm
fullnameOverride: "rhdh-agent-sandbox"

# Hub branding (formulario Helm / values.schema.json)
hub:
  title: Agent-friendly Developer Hub
  orgName: Sandbox
  branding:
    fullLogo: ""
    iconLogo: ""
    fullLogoWidth: 180
    theme:
      light:
        primaryColor: "#EE0000"
        headerColor1: "#151515"
        headerColor2: "#EE0000"
        navigationIndicatorColor: "#EE0000"
      dark:
        primaryColor: "#FF3333"
        headerColor1: "#151515"
        headerColor2: "#FF3333"
        navigationIndicatorColor: "#FF3333"
  plugins:
    scorecard: true
    adoptionInsights: false
    # MCP Chat community overlay is not reliably published for BS 1.54.9; IA replaces it.
    mcpChat: false

# Chart-managed CPU model (ServingRuntime + InferenceService). Default ON.
# Wired to LiteLLM alias local-cpu and Intelligent Assistant. No PVC (emptyDir download).
models:
  cpu:
    enabled: true
    name: local-cpu
    runtime: llamacpp
    image: ghcr.io/ggml-org/llama.cpp:server
    imagePullPolicy: IfNotPresent
    # Public GGUF (~0.5B Q4). Avoid storageUri — KServe storage-initializer requests ~20Gi.
    modelUrl: https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF/resolve/main/qwen2.5-0.5b-instruct-q4_k_m.gguf
    contextSize: 2048
    maxTokens: 256
    emptyDirSizeLimit: 1Gi
    enableRoute: true
    servicePort: 80
    resources:
      requests:
        cpu: 500m
        memory: 2Gi
      limits:
        cpu: "1"
        memory: 3Gi

# Hub Kubernetes plugin API (derived from rhdh.openshift.clusterRouterBase when apiUrl is empty).
cluster:
  name: sandbox
  apiUrl: ""

# Bootstrap secrets (generated if create=true and keys empty)
secrets:
  create: true
  name: rhdh-agent-sandbox-secrets
  backendSecret: ""
  litellmMasterKey: ""
  mcpToken: ""
  # Optional: legacy shared-models token (unused when only local-cpu is configured)
  modelApiKey: ""
  # LiteMaaS bearer for optional tool-calling model (litemaas-qwen)
  litemaasApiKey: ""

litellm:
  enabled: true
  image:
    repository: litellm/litellm-non_root
    tag: v1.82.3-stable
    pullPolicy: IfNotPresent
  service:
    port: 4000
  route:
    enabled: true
    tls:
      termination: edge
  resources:
    requests:
      cpu: 50m
      memory: 512Mi
    limits:
      cpu: 500m
      memory: 1536Mi
  models:
    # Chart CPU InferenceService (default). apiBase rewritten in litellm-configmap when models.cpu.enabled.
    - name: local-cpu
      modelId: local-cpu
      apiBase: http://local-cpu-predictor:80/v1
      apiKeyEnv: LITELLM_MASTER_KEY
      supportsFunctionCalling: false
      dropTools: true
    # Optional external tool-calling model
    - name: litemaas-qwen
      modelId: Qwen3.6-35B-A3B
      apiBase: https://litemaas.rhoai.rh-aiservices-bu.com/v1
      apiKeyEnv: LITEMAAS_API_KEY
      supportsFunctionCalling: true
      dropTools: false
  defaultModel: local-cpu
  litemaasSecret:
    name: litemaas-credentials
    key: api-key
  postgres:
    enabled: false

mcp:
  enabled: true
  quarkus:
    enabled: true
    image:
      repository: quay.io/maximilianopizarro/openshift-mcp-server
      tag: latest
      pullPolicy: IfNotPresent
    service:
      port: 8080
    route:
      enabled: false
    resources:
      requests:
        cpu: 100m
        memory: 256Mi
      limits:
        cpu: "1"
        memory: 512Mi
  kubernetes:
    # Revived with public image. Set false if pod cannot become Ready.
    enabled: true
    image:
      repository: quay.io/maximilianopizarro/openshift-mcp-server
      tag: latest
      pullPolicy: IfNotPresent
    service:
      port: 8085
    route:
      enabled: false
    resources:
      requests:
        cpu: 50m
        memory: 128Mi
      limits:
        cpu: 500m
        memory: 512Mi
  inspector:
    enabled: false
  serviceAccount:
    create: true
    name: rhdh-agent-mcp
  rbac:
    create: true

'''

rhdh = r'''
# Subchart: official Red Hat Developer Hub 2.1 (alias rhdh)
# Values are flattened vs 1.x — see Red Hat migration guide 1.x → 2.1.
rhdh:
  enabled: true
  nameOverride: developer-hub
  openshift:
    # REQUIRED: sandbox apps domain, e.g. apps.rm2.thpm.p1.openshiftapps.com
    clusterRouterBase: ""
    route:
      enabled: true
      annotations:
        haproxy.router.openshift.io/timeout: 5m
  auth:
    backend:
      enabled: true
      existingSecretRef:
        name: rhdh-agent-sandbox-secrets
        key: backend-secret
  dynamicPlugins:
    includes:
      - dynamic-plugins.default.yaml
    # Sandbox PVC quota is often full — do not use ephemeral PVC for plugins.
    volume:
      type: emptyDir
    plugins:
      - package: oci://ghcr.io/redhat-developer/rhdh-plugin-export-overlays/backstage-plugin-kubernetes-backend:bs_1.54.9__0.21.10!backstage-plugin-kubernetes-backend
        enabled: true
      - package: oci://ghcr.io/redhat-developer/rhdh-plugin-export-overlays/backstage-plugin-kubernetes:bs_1.54.9__0.12.22!backstage-plugin-kubernetes
        enabled: true
      - package: oci://ghcr.io/redhat-developer/rhdh-plugin-export-overlays/backstage-community-plugin-topology:bs_1.54.9__3.0.7!backstage-community-plugin-topology
        enabled: true
      - package: oci://ghcr.io/redhat-developer/rhdh-plugin-export-overlays/backstage-community-plugin-tekton:bs_1.54.9__4.0.5!backstage-community-plugin-tekton
        enabled: true
      - package: oci://ghcr.io/redhat-developer/rhdh-plugin-export-overlays/backstage-community-plugin-scaffolder-backend-module-kubernetes:bs_1.54.9__2.21.0!backstage-community-plugin-scaffolder-backend-module-kubernetes
        enabled: true
      - package: oci://ghcr.io/redhat-developer/rhdh-plugin-export-overlays/red-hat-developer-hub-backstage-plugin-scorecard:bs_1.54.9__4.5.2!red-hat-developer-hub-backstage-plugin-scorecard
        enabled: true
      - package: oci://ghcr.io/redhat-developer/rhdh-plugin-export-overlays/red-hat-developer-hub-backstage-plugin-scorecard-backend:bs_1.54.9__4.5.2!red-hat-developer-hub-backstage-plugin-scorecard-backend
        enabled: true
      - package: oci://ghcr.io/redhat-developer/rhdh-plugin-export-overlays/red-hat-developer-hub-backstage-plugin-scorecard-backend-module-filecheck:bs_1.54.9__1.1.7!red-hat-developer-hub-backstage-plugin-scorecard-backend-module-filecheck
        enabled: true
      - package: oci://quay.io/maximilianopizarro/rhdh-agent-sandbox:scaffolder-backend-module-catalog-register-0.2.0!plugin
        enabled: true
  intelligentAssistant:
    enabled: true
    existingSecret: rhdh-agent-sandbox-secrets
    config:
      stack:
        existingConfigMap:
          name: rhdh-agent-sandbox-lightspeed-stack
          key: lightspeed-stack.yaml
    okp:
      enabled: false
    core:
      resources:
        requests:
          cpu: 100m
          memory: 512Mi
        limits:
          cpu: 1000m
          memory: 2Gi
  podAnnotations:
    app.openshift.io/custom-icon: "https://raw.githubusercontent.com/redhat-developer/rhdh/main/packages/app/public/favicon-96x96.png"
  resources:
    requests:
      cpu: 250m
      memory: 1Gi
    limits:
      cpu: 1000m
      memory: 2Gi
  appConfig:
    app:
      title: Agent-friendly Developer Hub
      branding:
        fullLogoWidth: 180
        theme:
          light:
            primaryColor: "#EE0000"
            headerColor1: "#151515"
            headerColor2: "#EE0000"
            navigationIndicatorColor: "#EE0000"
          dark:
            primaryColor: "#FF3333"
            headerColor1: "#151515"
            headerColor2: "#FF3333"
            navigationIndicatorColor: "#FF3333"
    auth:
      environment: development
      providers:
        guest:
          userEntityRef: user:default/guest
          dangerouslyAllowOutsideDevelopment: true
    permission:
      enabled: false
    techdocs:
      builder: local
      publisher:
        type: local
    catalog:
      locations:
        - type: file
          target: /opt/app-root/src/catalog/all.yaml
          rules:
            - allow: [Component, System, API, Resource, Location, Template, User, Group]
        - type: file
          target: /opt/app-root/src/scaffolder-registered/entities/*.yaml
          rules:
            - allow: [Component, API, Resource, Location, System]
    backend:
      auth:
        externalAccess:
          - type: legacy
            options:
              secret: ${BACKEND_SECRET}
              subject: legacy-default-config
          - type: static
            options:
              token: ${MCP_TOKEN}
              subject: mcp-clients
      reading:
        allow:
          - host: github.com
          - host: raw.githubusercontent.com
          - host: "*.github.io"
    kubernetes:
      customResources:
        - group: tekton.dev
          apiVersion: v1
          plural: pipelines
        - group: tekton.dev
          apiVersion: v1
          plural: pipelineruns
        - group: tekton.dev
          apiVersion: v1
          plural: taskruns
        - group: route.openshift.io
          apiVersion: v1
          plural: routes
        - group: serving.kserve.io
          apiVersion: v1beta1
          plural: inferenceservices
        - group: serving.kserve.io
          apiVersion: v1alpha1
          plural: servingruntimes
      serviceLocatorMethod:
        type: multiTenant
      clusterLocatorMethods:
        - type: config
          clusters:
            - url: ${K8S_CLUSTER_URL}
              name: ${K8S_CLUSTER_NAME}
              authProvider: serviceAccount
              skipTLSVerify: true
              skipMetricsLookup: true
              serviceAccountToken: ${K8S_CLUSTER_TOKEN}
    intelligent-assistant:
      systemPrompt: >-
        You are the agent-friendly Developer Hub demo assistant on OpenShift Developer Sandbox.
        Prefer catalog, TechDocs, and namespace-scoped MCP tools. Stay inside the user namespace.
        When diagnosing cluster state, list/get before mutate and summarize risk.
      servers:
        - id: vllm/local-cpu
          url: http://rhdh-agent-sandbox-litellm:4000/v1
          model: local-cpu
        - id: vllm/litemaas-qwen
          url: http://rhdh-agent-sandbox-litellm:4000/v1
          model: litemaas-qwen
      mcpServers:
        - name: mcp-integration-tools
          token: ${MCP_TOKEN}
  extraEnv:
    - name: MCP_TOKEN
      valueFrom:
        secretKeyRef:
          name: rhdh-agent-sandbox-secrets
          key: mcp-token
    - name: LITELLM_API_KEY
      valueFrom:
        secretKeyRef:
          name: rhdh-agent-sandbox-secrets
          key: litellm-master-key
    - name: NODE_OPTIONS
      value: "--no-node-snapshot"
    - name: CLUSTER_ROUTER_BASE
      valueFrom:
        secretKeyRef:
          name: rhdh-agent-sandbox-cluster
          key: router-base
    - name: K8S_CLUSTER_NAME
      valueFrom:
        secretKeyRef:
          name: rhdh-agent-sandbox-cluster
          key: cluster-name
    - name: K8S_CLUSTER_URL
      valueFrom:
        secretKeyRef:
          name: rhdh-agent-sandbox-cluster
          key: api-url
    - name: K8S_CLUSTER_TOKEN
      valueFrom:
        secretKeyRef:
          name: rhdh-agent-sandbox-hub-k8s-reader
          key: token
  extraVolumeMounts:
    - name: rhdh-agent-catalog
      mountPath: /opt/app-root/src/catalog
      readOnly: true
    - name: scaffolder-assets
      mountPath: /opt/app-root/src/scaffolder-assets
      readOnly: true
    - name: registered-catalog
      mountPath: /opt/app-root/src/scaffolder-registered/entities
      readOnly: true
  extraVolumes:
    - name: rhdh-agent-catalog
      configMap:
        name: rhdh-agent-sandbox-catalog
    - name: scaffolder-assets
      projected:
        sources:
          - configMap:
              name: rhdh-agent-sandbox-scaffolder-assets
              items:
                - key: deploy-agent-README.md
                  path: skeletons/deploy-agent/README.md
                - key: deploy-agent-catalog-info.yaml
                  path: skeletons/deploy-agent/catalog-info.yaml
                - key: deploy-agent-devfile.yaml
                  path: skeletons/deploy-agent/devfile.yaml
                - key: python-manifests.yaml
                  path: agent-runtimes/python/manifests.yaml
                - key: python-catalog-info.yaml
                  path: agent-runtimes/python/catalog-info.yaml
                - key: nodejs-manifests.yaml
                  path: agent-runtimes/nodejs/manifests.yaml
                - key: nodejs-catalog-info.yaml
                  path: agent-runtimes/nodejs/catalog-info.yaml
                - key: quarkus-manifests.yaml
                  path: agent-runtimes/quarkus/manifests.yaml
                - key: quarkus-catalog-info.yaml
                  path: agent-runtimes/quarkus/catalog-info.yaml
    - name: registered-catalog
      configMap:
        name: rhdh-agent-sandbox-registered-catalog
  postgresql:
    primary:
      persistence:
        size: 1Gi
      resources:
        requests:
          cpu: 50m
          memory: 256Mi
        limits:
          cpu: 500m
          memory: 512Mi
'''

out = header + "\n" + middle + rhdh
(ROOT / "values.yaml").write_text(out, encoding="utf-8")
print(f"wrote values.yaml ({len(out.splitlines())} lines)")
