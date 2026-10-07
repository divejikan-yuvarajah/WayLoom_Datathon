# Local Synthetic FastAPI Service

FastAPI is an optional engineering convenience, not an organizer requirement. Install the isolated dependencies with:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-integration.txt
```

Start the loopback-only synthetic service:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.integration_api:app --host 127.0.0.1 --port 8088
```

Example request:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8088/v1/demand-forecast -ContentType application/json -Body '{"depot":"Demo Depot","brand":"Fresh","iso_year":2026,"iso_week":42,"forecast_horizon":1}'
```

Routes are health, contract metadata, model initialization, delivery risk, demand forecast, aggregate allocation insight, and synthetic deferral examples. Interactive OpenAPI is available locally at `/docs`.

The default configuration has no CORS origins and does not load real models. Do not bind a private-local mode publicly. Stop the service with `Ctrl+C`.
