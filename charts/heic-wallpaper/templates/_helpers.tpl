{{/* Expand the name of the chart */}}
{{- define "heicwallpaper.names.name" -}}
  {{- $globalNameOverride := "" -}}
  {{- if hasKey .Values "global" -}}
    {{- $globalNameOverride = (default $globalNameOverride .Values.global.nameOverride) -}}
  {{- end -}}
  {{- default .Chart.Name (default .Values.nameOverride $globalNameOverride) | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/* Create chart name and version as used by the chart label */}}
{{- define "heicwallpaper.names.chart" -}}
  {{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "heicwallpaper.names.fullname" -}}
  {{- $name := include "heicwallpaper.names.name" . -}}
  {{- $globalFullNameOverride := "" -}}
  {{- if hasKey .Values "global" -}}
    {{- $globalFullNameOverride = (default $globalFullNameOverride .Values.global.fullnameOverride) -}}
  {{- end -}}
  {{- if or .Values.fullnameOverride $globalFullNameOverride -}}
    {{- $name = default .Values.fullnameOverride $globalFullNameOverride -}}
  {{- else -}}
    {{- if contains $name .Release.Name -}}
      {{- $name = .Release.Name -}}
    {{- else -}}
      {{- $name = printf "%s-%s" .Release.Name $name -}}
    {{- end -}}
  {{- end -}}
  {{- trunc 63 $name | trimSuffix "-" -}}
{{- end -}}

{{/* Common labels shared across objects */}}
{{- define "heicwallpaper.labels" -}}
helm.sh/chart: {{ include "heicwallpaper.names.chart" . }}
{{ include "heicwallpaper.labels.selectorLabels" . }}
  {{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
  {{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}


{{/* Selector labels shared across objects */}}
{{- define "heicwallpaper.labels.selectorLabels" -}}
app.kubernetes.io/name: {{ include "heicwallpaper.names.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}


{{- define "heicwallpaper.lookupSecretKey" -}}
  {{- $namespace := index . 0 -}}
  {{- $secretName := index . 1 -}}
  {{- $key := index . 2 -}}
  {{- $secret := lookup "v1" "Secret" $namespace $secretName -}}
  {{- if $secret -}}
    {{- if hasKey $secret.data $key -}}
      {{- $secretValue := index $secret.data $key -}}
      {{ $secretValue | b64dec }}
    {{- else -}}
      {{- fail (printf "Secret '%s' does not have key '%s'" $secretName $key) -}}
    {{- end -}}
  {{- else -}}
    {{- fail (printf "Secret '%s' not found in namespace '%s'" $secretName $namespace) -}}
  {{- end -}}
{{- end -}}

{{- define "heicwallpaper.databasePassword" -}}
  {{- if and .Values.postgresql.auth.existingSecret (not (empty .Values.postgresql.auth.existingSecret)) -}}
    {{ include "heicwallpaper.lookupSecretKey" (list .Release.Namespace .Values.postgresql.auth.existingSecret "password") }}
  {{- else -}}
    {{ .Values.postgresql.auth.password }}
  {{- end -}}
{{- end -}}


{{- define "heicwallpaper.appEnvironment" }}
- name: BROKER_URL
  value: "redis://{{ .Release.Name }}-redis-master:6379/0"
- name: PUBLIC_URL
  value: "{{ $.Values.heicwallpaper.public_url }}"
- name: PUBLIC_ASSET_URL
  value: "{{ $.Values.heicwallpaper.public_asset_url }}"
- name: DB_NAME
  value: {{ .Values.postgresql.auth.database }}
- name: DB_PASSWORD
{{ if .Values.postgresql.auth.existingSecret }}
  valueFrom:
    secretKeyRef:
      name: {{ .Values.postgresql.auth.existingSecret }}
      key: password
{{ else }}
  value: {{ .Values.postgresql.auth.password }}
{{ end }}
- name: DB_HOST
  value: {{ (include "heicwallpaper.names.fullname" .) }}-postgresql-hl
- name: DB_USER
  value: {{ .Values.postgresql.auth.username }}
{{- end}}
