{{- /*
Shared stub: tiny HTTP agent that echoes AGENT_SPEC and proxies chat to LiteLLM.
Language images only change the base image label; the runtime is a portable shell+python one-liner via ubi-minimal isn't enough for all —
use python UBI for all three stubs so Sandbox pulls one image, with FRAMEWORK label distinguishing LangGraph / LangChain.js / LangChain4j intent.
*/ -}}
{{- define "rhdh-agent-sandbox.agentDeployment" -}}
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .name }}
  namespace: {{ .namespace }}
  labels:
    app.kubernetes.io/name: {{ .name }}
    app.kubernetes.io/component: agent
    app.kubernetes.io/part-of: {{ .fullname }}
    rhdh-agent-sandbox.io/language: {{ .language }}
    rhdh-agent-sandbox.io/framework: {{ .framework }}
  annotations:
    app.openshift.io/runtime: {{ .language }}
    app.openshift.io/connects-to: '[{"apiVersion":"apps/v1","kind":"Deployment","name":"{{ .fullname }}-litellm"}]'
spec:
  replicas: 1
  selector:
    matchLabels:
      app.kubernetes.io/name: {{ .name }}
  template:
    metadata:
      labels:
        app.kubernetes.io/name: {{ .name }}
        app.kubernetes.io/component: agent
        app.kubernetes.io/part-of: {{ .fullname }}
        rhdh-agent-sandbox.io/language: {{ .language }}
      annotations:
        app.openshift.io/runtime: {{ .language }}
    spec:
      containers:
        - name: agent
          image: {{ .image | default "registry.access.redhat.com/ubi9/python-311:latest" }}
          imagePullPolicy: IfNotPresent
          ports:
            - name: http
              containerPort: 8080
          env:
            - name: MODEL
              value: {{ .model | default "granite" | quote }}
            - name: FRAMEWORK
              value: {{ .framework | quote }}
            - name: LANGUAGE
              value: {{ .language | quote }}
            - name: AGENT_SPEC
              value: {{ .agentSpec | default "You are a helpful namespace-scoped agent." | quote }}
            - name: LITELLM_API_BASE
              value: http://{{ .fullname }}-litellm:{{ .litellmPort }}/v1
            - name: LITELLM_API_KEY
              valueFrom:
                secretKeyRef:
                  name: {{ .secretsName }}
                  key: litellm-master-key
          command: ["python3", "-u", "/app/server.py"]
          volumeMounts:
            - name: app
              mountPath: /app
          readinessProbe:
            httpGet:
              path: /health
              port: http
            initialDelaySeconds: 5
            periodSeconds: 10
          resources:
            requests:
              cpu: 25m
              memory: 64Mi
            limits:
              cpu: 200m
              memory: 256Mi
      volumes:
        - name: app
          configMap:
            name: {{ .fullname }}-agent-runtime
---
apiVersion: v1
kind: Service
metadata:
  name: {{ .name }}
  namespace: {{ .namespace }}
  labels:
    app.kubernetes.io/name: {{ .name }}
    app.kubernetes.io/component: agent
    app.kubernetes.io/part-of: {{ .fullname }}
spec:
  selector:
    app.kubernetes.io/name: {{ .name }}
  ports:
    - name: http
      port: 8080
      targetPort: http
{{- end -}}
