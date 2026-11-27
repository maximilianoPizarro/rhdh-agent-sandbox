{{/*
Expand the name of the chart.
*/}}
{{- define "rhdh-agent-sandbox.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "rhdh-agent-sandbox.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{- define "rhdh-agent-sandbox.labels" -}}
helm.sh/chart: {{ include "rhdh-agent-sandbox.name" . }}-{{ .Chart.Version | replace "+" "_" }}
app.kubernetes.io/name: {{ include "rhdh-agent-sandbox.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{- define "rhdh-agent-sandbox.selectorLabels" -}}
app.kubernetes.io/name: {{ include "rhdh-agent-sandbox.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{- define "rhdh-agent-sandbox.namespace" -}}
{{- .Release.Namespace }}
{{- end }}

{{/*
OpenShift apps domain (RHDH 2.1: rhdh.openshift.clusterRouterBase).
Falls back to legacy rhdh.global.clusterRouterBase for older overrides.
*/}}
{{- define "rhdh-agent-sandbox.clusterRouterBase" -}}
{{- $v := "" -}}
{{- if and .Values.rhdh .Values.rhdh.openshift .Values.rhdh.openshift.clusterRouterBase -}}
{{- $v = .Values.rhdh.openshift.clusterRouterBase -}}
{{- else if and .Values.rhdh .Values.rhdh.global .Values.rhdh.global.clusterRouterBase -}}
{{- $v = .Values.rhdh.global.clusterRouterBase -}}
{{- end -}}
{{- default "apps.example.com" $v -}}
{{- end }}

{{/*
CPU model InferenceService predictor service DNS (OpenAI-compatible /v1).
*/}}
{{- define "rhdh-agent-sandbox.cpuModelApiBase" -}}
{{- $name := .Values.models.cpu.name | default "local-cpu" -}}
http://{{ $name }}-predictor.{{ .Release.Namespace }}.svc.cluster.local:{{ .Values.models.cpu.servicePort | default 80 }}/v1
{{- end }}
