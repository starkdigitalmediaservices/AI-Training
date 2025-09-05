## Math Agents - Calculator (A2A-Ready)

A lightweight multi-agent setup where three HTTP agents (Calculator, Unit Converter, Statistics) communicate using a shared A2A message contract over REST. This repo contains the Calculator agent, a web UI, a CLI client, and a pipeline orchestrator for sequential workflows.

### Components
1. Calculator Agent (this repo): `calculator_agent_network.py`
2. Web UI (served by Flask): `templates/index.html`, `static/app.js`, `static/styles.css`
3. CLI client: `cli_calculator.py`
4. Orchestrator (sequential flow): `pipeline_orchestrator.py`
5. Teammates’ agents (external): Unit Converter (port 5002), Statistics (port 5003)

### A2A Message Contract
- Endpoint: POST `/message`
- Request:
```json
{
  "sender": "<agent_or_client_name>",
  "correlation_id": "uuid-1234",
  "trace": ["calculator@192.168.1.10:5001"],
  "message": { "operation": "add", "data": {"numbers": [10,20,30]} }
}
```
- Response:
```json
{
  "agent": "calculator_agent",
  "response": { "result": 60 },
  "correlation_id": "uuid-1234",
  "trace": ["calculator@192.168.1.10:5001"]
}
```
- Keep this envelope consistent across agents.

### Endpoints (Calculator Agent)
1. GET `/` → Web UI
2. GET `/health` → status JSON (agent info, ports, peer URLs)
3. GET `/network-info` → env + URL diagnostics
4. POST `/calculate` → direct math ops (request: `{operation, data}`)
5. POST `/message` → A2A entrypoint (request: A2A contract)

### Setup
1. Create venv and install dependencies:
   - `python3 -m venv venv`
   - `source venv/bin/activate`
   - `pip install -r requirements.txt`
2. Create `.env` (or use `.env.example` as a template):
   - `CALCULATOR_PORT=5001`
   - `UNIT_CONVERTER_HOST=<unit-ip>` `UNIT_CONVERTER_PORT=5002` (or `UNIT_CONVERTER_URL`)
   - `STATISTICS_HOST=<stats-ip>` `STATISTICS_PORT=5003` (or `STATISTICS_URL`)

### Run
1. Start the Calculator agent:
   - `source venv/bin/activate`
   - `python calculator_agent_network.py`
2. Open the Web UI: `http://localhost:5001/`
3. CLI usage (non-interactive):
   - `python cli_calculator.py -o add --numbers 10,20,30`
4. CLI usage (interactive):
   - `python cli_calculator.py`

### Sequential Workflow (Calculator → Unit Converter → Statistics)
1. Ensure each agent is reachable:
   - Calculator: `http://<calc-ip>:5001/health`
   - Unit Converter: `http://<unit-ip>:5002/health`
   - Statistics: `http://<stats-ip>:5003/health`
2. Run the orchestrator with URLs:
   - `python pipeline_orchestrator.py --calculator-url http://<calc-ip>:5001 --unit-url http://<unit-ip>:5002 --statistics-url http://<stats-ip>:5003 --numbers 10,20,30 --from-unit meter --to-unit feet --stats-op mean`
3. Or use env vars instead of flags:
   - `export CALCULATOR_URL=http://<calc-ip>:5001`
   - `export UNIT_CONVERTER_URL=http://<unit-ip>:5002`
   - `export STATISTICS_URL=http://<stats-ip>:5003`
   - `python pipeline_orchestrator.py`
4. Output shows three steps and the final result with a shared `correlation_id`.

### Orchestration Styles
1. Orchestrator pattern (default here): a small client calls agents in order. Simple and debuggable.
2. Chained A2A (optional): each agent’s `/message` computes and forwards to the next when a “next hop” is provided. Requires coordinated changes across teams.

### Networking Options
1. LAN (same subnet): use `http://<lan-ip>:<port>` and open ports 5001–5003 on firewalls.
2. VPN (Tailscale / ZeroTier): use stable VPN IPs (100.x or virtual network IPs).
3. Tunnels (ngrok / Cloudflare Tunnel): use full `https://...` URLs in env (the `*_URL` variables).

### Testing
1. Local API tests: `python test_calculator.py`
2. Health checks: GET `/health` on each agent
3. Web UI: `http://localhost:5001/` (responsive, animated)

### Troubleshooting
1. Port in use: change port in `.env` and restart.
2. Connection errors: verify peer URLs, open firewall, confirm `/health`.
3. JSON errors: ensure the A2A envelope matches the contract and that each agent returns `{ "response": { "result": ... } }`.

### Folder Structure
```
.
├── calculator_agent_network.py
├── cli_calculator.py
├── pipeline_orchestrator.py
├── requirements.txt
├── templates/
│   └── index.html
├── static/
│   ├── app.js
│   └── styles.css
└── test_calculator.py
```

### Approach Summary
1. Keep a consistent A2A contract across agents.
2. Start with the orchestrator for sequential flows; add chained forwarding later if the team prefers full A2A chaining.
3. Use env variables to point to teammates’ agents (LAN/VPN/Tunnel).
4. Validate each step independently (health checks) before end-to-end runs.
