{{- define "tradcoreGetRedisCache" -}}
{{- if and .Values.global .Values.global.redis .Values.global.redis.cachename (not .Values.externalServices.tradcore.redis.cachename) }}
  {{- .Values.global.redis.cachename -}}
{{- else if .Values.externalServices.tradcore.redis.cachename -}}``
  {{- .Values.externalServices.tradcore.redis.cachename -}}
{{- else if .Values.redis.cachename -}}
  {{- .Values.redis.cachename -}}
{{- else -}}
  {{- "tradcore" -}}
{{- end -}}
{{- end -}}

{{- define "tradcoreGetRedisPassword" -}}
{{- if and .Values.global .Values.global.redis .Values.global.redis.password (not .Values.externalServices.tradcore.redis.password) }}
  {{- .Values.global.redis.password -}}
{{- else if .Values.externalServices.tradcore.redis.password -}}
  {{- .Values.externalServices.tradcore.redis.password -}}
{{- else if .Values.redis.password -}}
  {{- .Values.redis.password -}}
{{- else -}}
  {{- "default-password" -}}
{{- end -}}
{{- end -}}

{{- define "tradcoreGetRedisHost" -}}
{{- if and .Values.global .Values.global.redis .Values.global.redis.host (not .Values.externalServices.tradcore.redis.host) }}
  {{- .Values.global.redis.host -}}
{{- else if .Values.externalServices.tradcore.redis.host -}}
  {{- .Values.externalServices.tradcore.redis.host -}}
{{- else if .Values.redis.host -}}
  {{- .Values.redis.host -}}
{{- else -}}
  {{- "localhost" -}}
{{- end -}}
{{- end -}}

{{- define "tradcoreGetRedisPort" -}}
{{- if and .Values.global .Values.global.redis .Values.global.redis.port (not .Values.externalServices.tradcore.redis.port) }}
  {{- .Values.global.redis.port | toString -}}
{{- else if .Values.externalServices.tradcore.redis.port -}}
  {{- .Values.externalServices.tradcore.redis.port | toString -}}
{{- else if .Values.redis.port -}}
  {{- .Values.redis.port | toString -}}
{{- else -}}
  {{- "6379" -}}
{{- end -}}
{{- end -}}

{{/*
Define the name of the redis secret to use.
*/}}
{{- define "tradcoreGetRedisSecretName" -}}
{{- if and .Values.global .Values.global.redis .Values.global.redis.existingSecrets (not .Values.externalServices.tradcore.redis.existingSecrets) }}
  {{- print .Values.global.redis.existingSecrets }}
{{- else if .Values.externalServices.tradcore.redis.existingSecrets }}
  {{- print .Values.externalServices.tradcore.redis.existingSecrets }}
{{- else }}
  {{- print (include "tradcore.fullname" .) "-cache-credentials" }}
{{- end }}
{{- end }}