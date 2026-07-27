# SpecGuard remote audit engine (AWS SAM)

Fase 2 de la arquitectura (ver `docs/architecture.md`): expone el motor de
auditoria como una API HTTP, sin depender de que quien la llama tenga
`specguard` instalado. Reusa directamente `src/specguard/*` - el handler no
duplica ninguna logica, solo orquesta.

**Actualizacion (2026-07-26): desplegado y probado contra una cuenta AWS real.**
Endpoint en vivo: `https://ble6qlnav0.execute-api.us-east-1.amazonaws.com/prod/audit`
(stack `specguard-audit`, us-east-1). Probado con una auditoria real de punta
a punta: `POST` devuelve 200 con el reporte completo, y el reporte queda
persistido en DynamoDB con su TTL de 7 dias. Este endpoint es un bonus para
el video/pitch - el link de demo que se entrega sigue siendo GitHub Pages.

Dos bugs reales encontrados solo al desplegar de verdad (documentados aqui
porque no habrian aparecido sin intentarlo):

1. `ThrottleSettings` no es una propiedad valida de `AWS::Serverless::Api` -
   `sam build` lo rechaza. Va bajo `MethodSettings` (`ResourcePath: "/*"`,
   `HttpMethod: "*"`, `ThrottlingRateLimit`, `ThrottlingBurstLimit`).
2. El endpoint edge-optimizado por defecto (`EndpointConfiguration` sin
   especificar) devolvia `403 Forbidden` a traves de CloudFront en esta
   cuenta - sin resource policy, sin WAF, con el metodo y el permiso de
   Lambda correctamente configurados. Cambiar a `EndpointConfiguration: {Type: REGIONAL}`
   (bypassa CloudFront, pega directo a API Gateway regional) lo resolvio.
   Si tu API vuelve a dar Forbidden con todo lo demas bien, este es el
   primer sospechoso.

## Que despliega

- **AuditFunction** (Lambda, Python 3.12): recibe `POST /audit` con
  `{"requirements_md": "...", "tasks_md": "...", "diff": "...", "spec_name": "..."}`
  y devuelve el mismo JSON que produce `specguard audit`.
- **ReportsTable** (DynamoDB): guarda cada reporte por `report_id`, con TTL de
  7 dias (`expires_at`) para que no crezca sin limite.
- **AuditApi** (API Gateway REST API): throttling de 5 req/s (burst 10) para
  acotar el costo si el endpoint queda publico durante la ventana de demo.

## Prerequisitos

```bash
pip install aws-sam-cli   # o: brew install aws-sam-cli
aws configure             # credenciales de tu cuenta AWS
```

## Desplegar

```bash
cd infra
sam build
sam deploy --guided
```

`sam build` usa `CodeUri: ../` (raiz del repo) y `.samignore` en la raiz para
excluir tests, docs, dashboard, etc. del paquete de Lambda - solo entra
`src/` e `infra/`. `boto3` no se empaqueta: ya viene incluido en el runtime
de Lambda.

Al terminar, `sam deploy` imprime `AuditApiUrl`. Probar con:

```bash
curl -X POST "$AUDIT_API_URL" \
  -H "Content-Type: application/json" \
  -d @- <<'EOF'
{
  "spec_name": "demo",
  "requirements_md": "### Requirement 1: Demo\n**User Story:** As a user, I want a demo, so that it works.\n#### Acceptance Criteria\n1. WHEN called THEN it SHALL respond\n",
  "tasks_md": "",
  "diff": "diff --git a/demo.py b/demo.py\nnew file mode 100644\n--- /dev/null\n+++ b/demo.py\n@@ -0,0 +1,1 @@\n+def respond(): pass\n"
}
EOF
```

## Limitaciones de seguridad conocidas (sin resolver)

- **Sin autenticacion.** El endpoint queda publico. Para produccion real,
  agregar un API key de API Gateway (`ApiKeyRequired: true` + `UsagePlan`) o
  un authorizer (Cognito/IAM). Para la ventana de demo del hackathon, el
  throttling de 5 req/s es la unica mitigacion.
- **Limite de payload de 200 KB** aplicado en el handler (`MAX_BODY_BYTES`),
  ademas del limite propio de API Gateway. Ajustar si se necesitan diffs mas
  grandes.
- El IAM role de la funcion esta acotado a `DynamoDBCrudPolicy` sobre
  unicamente `ReportsTable` (least privilege) - no tiene ningun otro permiso.

## Eliminar todo

```bash
sam delete
```
