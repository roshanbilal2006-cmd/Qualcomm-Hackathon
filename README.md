# LandSense AI — IoT + MCP Service

## Overview

This is the IoT + MCP module of **LandSense AI**, a multi-device construction
intelligence platform. This module is a self-contained data layer exposing
sensor and RERA (construction project) data through a stable REST API.

The backend never knows whether data originates from a real Arduino, a
simulated reading, a local mock dataset, or a live government API — every
data source is hidden behind an adapter implementing a stable interface.
Switching between Demo Mode and Live Mode is a configuration change only;
no backend or route-level code changes are required.

## Folder Structure
iot_mcp_service/
├── main.py                      # Application entrypoint, wires everything together
├── config/                      # Settings and logging configuration
├── routes/                      # Thin HTTP layer (FastAPI routers)
├── services/                    # Business logic, depends only on interfaces
├── interfaces/                  # Abstract contracts (SensorProvider, RERAProvider)
├── adapters/                    # Concrete implementations (dummy, Arduino, mock, live)
│   ├── sensor/
│   └── rera/
├── models/                      # Pydantic schemas (the API contract)
├── middleware/                  # Request logging middleware
├── utils/                       # Request ID, timing, typed exceptions
├── data/mock_rera.json          # Seed dataset for mock RERA mode
├── tests/                       # Route-level integration tests
├── requirements.txt
└── .env.example
## Installation

Requires Python 3.12. ARM64-compatible (no CUDA, no platform-locked binaries).

```bash
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Copy the environment template:

```bash
cp .env.example .env
```

## Running Locally

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The service starts in **Demo Mode** by default (`SENSOR_MODE=demo`,
`RERA_MODE=mock`) — no Arduino hardware or live RERA access required.

Interactive API docs are available at `http://localhost:8000/docs` once running.

Run tests:

```bash
pytest tests/
```

## Demo Mode vs Live Mode

Switching modes is done entirely through environment variables in `.env` —
no code changes are required in `routes/`, `services/`, or `models/`.

| Variable | `demo` / `mock` (default) | `live` |
|---|---|---|
| `SENSOR_MODE` | Generates realistic random sensor values | Reads real data from Arduino over serial |
| `RERA_MODE` | Serves data from `data/mock_rera.json` | Calls the live RERA API (`LIVE_RERA_BASE_URL`) |

To switch to live sensor mode:
```bash
SENSOR_MODE=live
ARDUINO_PORT=/dev/ttyUSB0
```

To switch to live RERA mode (once a live endpoint is available):
```bash
RERA_MODE=live
LIVE_RERA_BASE_URL=https://example-rera-api.gov.in
LIVE_RERA_API_KEY=your-key-here
```

Restart the process after changing `.env` — the adapter factory (`adapters/factory.py`)
resolves the correct implementation once, at startup.

## Available REST APIs

### `GET /sensor`
Returns the current sensor reading, or `{"status": "offline"}` if unavailable.
```json
{
  "device_id": "UNO-Q",
  "timestamp": "2026-07-08T10:15:32Z",
  "noise_db": 72.4,
  "pm25": 38.1,
  "pm10": 61.7
}
```

### `GET /nearby_projects`
Returns a list of nearby RERA projects. **Fields are locked** to `name`,
`builder`, `status`, `distance` only — no `id` is exposed here.
```json
[
  { "name": "Prestige Tech Park", "builder": "Prestige Group", "status": "Approved", "distance": 0.9 }
]
```

> **Integration note:** Because `/nearby_projects` intentionally omits `id`,
> the backend cannot navigate directly from this endpoint to `/project/{id}`.
> Use `GET /rera` to obtain project identifiers if detail lookups are needed.
> This is a deliberate, documented limitation — see "Known Limitations" below.

### `GET /project/{id}`
Returns full project detail for a given id. `404` if not found.
```json
{
  "id": "RERA-KA-00123",
  "name": "Prestige Tech Park",
  "builder": "Prestige Group",
  "status": "Approved",
  "distance": 0.9
}
```

### `GET /rera`
Returns the full RERA dataset as a plain JSON array (includes `id`).

### `GET /status`
Reports current mode and health.
```json
{
  "arduino": "connected",
  "sensor_mode": "demo",
  "rera_mode": "mock",
  "mcp": "healthy"
}
```

## Known Limitations

- `/nearby_projects` does not expose `id` — see integration note above.
  If project-detail navigation from this endpoint becomes a requirement,
  the team must explicitly agree to revise this contract.
- `nearby_projects` currently does not compute real geographic distance —
  `distance` values come from the mock dataset. Real distance calculation
  will require the backend to pass location context in a future contract
  revision (reserved but unimplemented `lat`/`lng` query params).

## Future Migration Path

**Real Arduino:** Implement/verify the wire-format parsing in
`adapters/sensor/arduino_sensor_adapter.py` (currently expects
comma-separated `noise_db,pm25,pm10`), set `SENSOR_MODE=live` and
`ARDUINO_PORT` in `.env`. No other file needs to change.

**Live Karnataka RERA:** Implement the actual request/response handling in
`adapters/rera/live_rera_adapter.py` (currently a structural stub using
`httpx`), set `RERA_MODE=live`, `LIVE_RERA_BASE_URL`, and
`LIVE_RERA_API_KEY` in `.env`. No other file needs to change.

**Additional future sources** (Weather, AQI, Metro, Government/Satellite
APIs): add a new interface (if a new domain) or new adapter (if it fits an
existing interface), register it in `adapters/factory.py`, and expose it
via a new service/route if needed — existing files remain untouched.