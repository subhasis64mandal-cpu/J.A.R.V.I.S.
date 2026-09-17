# J.A.R.V.I.S. security baseline

J.A.R.V.I.S. is a local-first assistant. Security is a runtime design requirement, not a final hardening step.

## Threat model

The important boundaries are:

1. **Untrusted natural language -> brain**
   - Treat model output as untrusted data.
   - A model must not invent permissions, tools, confirmations, files, devices, or completed actions.
   - External text must never become an executable command merely because the model suggested it.

2. **Brain -> execution**
   - Only explicitly registered routes/tools may execute.
   - State-changing capabilities require allowlists and confirmation where appropriate.
   - Arbitrary shell and arbitrary Python remain disabled.

3. **Browser/web content -> runtime**
   - Web retrieval is bounded.
   - Browser navigation uses fixed allowlisted endpoints.
   - User-controlled URLs must not silently become privileged internal requests.

4. **Local HTTP -> runtime**
   - Home Base and Local Agent bind to loopback only.
   - Request bodies and arguments are size-bounded.
   - Security response headers are emitted for local web surfaces.
   - Avoid adding permissive CORS. Cross-origin access should be introduced only with an explicit authenticated design.

5. **Workflows -> external services**
   - n8n is optional and operator-configured.
   - Workflow endpoints must use HTTPS or loopback HTTP.
   - Secrets stay in environment variables or a secret store, never source control.
   - Workflow execution is a control action and is confirmation-gated.

6. **Persistent data -> operator**
   - Local memory and audit logs should remain outside the repository.
   - Audit records redact common credential fields.
   - Sensitive values should not be echoed into the UI or logs.

## Security checklist

Hacksplaining lessons that directly map to this project include Prompt Injection, Data Extraction Attacks, Slop Squatting (LLM Supply Chain), Command Execution, Broken Access Control, CSRF, SSRF, Logging and Monitoring, Information Leakage, Lax Security Settings, Remote Code Execution, Path Traversal, Toxic Dependencies, CORS, and Unencrypted Communication. The lesson catalog is maintained by Hacksplaining. See https://www.hacksplaining.com/lessons.

The project deliberately uses allowlists, bounded inputs, loopback networking, explicit capability metadata, confirmation tokens, and local audit logging to address these classes of risk.

## Dependency rule

Optional automation packages are not installed merely because an AI can name them. Review a package and pin/upgrade it deliberately before adding it to the runtime.

PyAutoGUI, BeautifulSoup, and Selenium remain uninstalled until the corresponding bounded adapters are designed and reviewed.
