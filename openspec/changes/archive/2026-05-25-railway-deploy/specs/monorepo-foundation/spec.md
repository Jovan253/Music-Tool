## MODIFIED Requirements

### Requirement: Frontend can reach backend in development
The FastAPI backend SHALL have CORS configured to accept requests from origins listed in the `CORS_ORIGINS` environment variable (comma-separated). When `CORS_ORIGINS` is not set, the backend SHALL fall back to accepting `http://localhost:5173`. The frontend SHALL read the API base URL from the `VITE_API_BASE_URL` environment variable.

#### Scenario: Frontend fetches health check during development
- **WHEN** the frontend makes a fetch to `${VITE_API_BASE_URL}/health` with both servers running
- **THEN** the request succeeds without a CORS error

#### Scenario: Deployed frontend reaches deployed backend
- **WHEN** `CORS_ORIGINS` is set to the Vercel app URL on Railway
- **THEN** requests from that origin succeed without a CORS error

#### Scenario: Multiple origins accepted
- **WHEN** `CORS_ORIGINS` is set to a comma-separated list of URLs
- **THEN** requests from any listed origin succeed without a CORS error
