# OpenMontage MCP for ChatGPT

This package exposes three read-only tools:

- `om_list_pipelines` — list pipeline manifests and declared stages.
- `om_get_capabilities` — return the registered tool inventory and availability.
- `om_estimate_production` — report a pipeline's declared default budget; it is not a live quote.

The MCP integration does not execute production tools, accept arbitrary paths, or run shell commands.

## Local stdio mode

Install dependencies and run:

```bash
python -m pip install -r requirements.txt
python -m integrations.mcp_server.server
```

## Remote Streamable HTTP mode

1. Check out the branch/repository on an Ubuntu or Debian server at `/opt/OpenMontage`.
2. Run `sudo bash deploy/install-mcp.sh`. It installs Python dependencies, generates a bearer token in `/etc/openmontage/mcp.env` if one does not exist, and installs/starts the systemd service.
3. Configure a domain and TLS certificate, then adapt `deploy/nginx-openmontage-mcp.conf.example` for that domain and certificate.
4. Keep the Python listener bound to `127.0.0.1:8000`; expose only HTTPS via the reverse proxy. Do not open port 8000 publicly.
5. Verify that requests without `Authorization: Bearer <token>` return HTTP 401 and that authenticated MCP requests reach the server.
6. Configure the HTTPS MCP URL (typically `https://YOUR_DOMAIN/mcp`) in ChatGPT if the account/workspace supports custom MCP connectors and its authentication options are compatible with this bearer-token gate.

Environment variables:

- `OM_MCP_TRANSPORT=streamable-http`
- `OM_MCP_BEARER_TOKEN` — required, minimum 32 characters.
- `OM_MCP_HOST=127.0.0.1`
- `OM_MCP_PORT=8000`

The backend is deliberately read-only for this first milestone. Authenticated transport does not replace TLS, host firewalling, secret rotation, or deployment-specific access controls. The reverse-proxy example is a template; TLS certificate directives must be supplied by the server operator.

## Current scope and next step

The code provides discovery/preflight only. Actual remote deployment requires SSH/server access and a real domain/TLS configuration. Production execution, durable jobs, budget enforcement, and per-project authorization are not yet implemented.
