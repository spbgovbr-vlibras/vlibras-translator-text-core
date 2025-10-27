{{- define "tradcoreGetAmqpUsername" -}}
{{- if and .Values.global .Values.global.amqp .Values.global.amqp.username (not .Values.externalServices.tradcore.amqp.username) }}
  {{- .Values.global.amqp.username -}}
{{- else if .Values.externalServices.tradcore.amqp.username -}}
  {{- .Values.externalServices.tradcore.amqp.username -}}
{{- else if .Values.rabbitmqha.rabbitmqUsername -}}
  {{- .Values.rabbitmqha.rabbitmqUsername -}}
{{- else -}}
  {{- "default-user" -}}
{{- end -}}
{{- end -}}

{{- define "tradcoreGetAmqpPassword" -}}
{{- if and .Values.global .Values.global.amqp .Values.global.amqp.password (not .Values.externalServices.tradcore.amqp.password) }}
  {{- .Values.global.amqp.password -}}
{{- else if .Values.externalServices.tradcore.amqp.password -}}
  {{- .Values.externalServices.tradcore.amqp.password -}}
{{- else if .Values.rabbitmqha.rabbitmqPassword -}}
  {{- .Values.rabbitmqha.rabbitmqPassword -}}
{{- else -}}
  {{- "default-password" -}}
{{- end -}}
{{- end -}}

{{- define "tradcoreGetAmqpHost" -}}
{{- if and .Values.global .Values.global.amqp .Values.global.amqp.host (not .Values.externalServices.tradcore.amqp.host) }}
  {{- .Values.global.amqp.host -}}
{{- else if .Values.externalServices.tradcore.amqp.host -}}
  {{- .Values.externalServices.tradcore.amqp.host -}}
{{- else if .Values.amqp.host -}}
  {{- .Values.amqp.host -}}
{{- else -}}
  {{- "localhost" -}}
{{- end -}}
{{- end -}}

{{- define "tradcoreGetAmqpPort" -}}
{{- if and .Values.global .Values.global.amqp .Values.global.amqp.port (not .Values.externalServices.tradcore.amqp.port) }}
  {{- .Values.global.amqp.port | toString -}}
{{- else if .Values.externalServices.tradcore.amqp.port -}}
  {{- .Values.externalServices.tradcore.amqp.port | toString -}}
{{- else if .Values.amqp.port -}}
  {{- .Values.amqp.port | toString -}}
{{- else -}}
  {{- "5432" -}}
{{- end -}}
{{- end -}}

{{/*
Define the name of the PostgreSQL secret to use.
*/}}
{{- define "tradcoreGetAmqpSecretName" -}}
{{- if and .Values.global .Values.global.amqp .Values.global.amqp.existingSecrets (not .Values.externalServices.tradcore.amqp.existingSecrets) }}
  {{- print .Values.global.amqp.existingSecrets }}
{{- else if .Values.externalServices.tradcore.amqp.existingSecrets }}
  {{- print .Values.externalServices.tradcore.amqp.existingSecrets }}
{{- else }}
  {{- print (include "tradcore.fullname" .) "-amqp-credentials" }}
{{- end }}
{{- end }}