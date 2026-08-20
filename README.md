# FastCloak

> **FastCloak** is a FastAPI-based OAuth 2.0 / OpenID Connect reverse proxy designed to put authentication and authorization in front of internal web services, with Keycloak handling identity, sessions, roles, and groups.

<p align="center">
  <a href="https://github.com/Amirrdoustdar/FastCloak">
    <img src="https://img.shields.io/badge/GitHub-FastCloak-181717?logo=github" alt="GitHub">
  </a>
  <img src="https://img.shields.io/badge/FastAPI-0.109.0-009688?logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white" alt="Python 3.11">
  <img src="https://img.shields.io/badge/Keycloak-OIDC-4D4D4D?logo=keycloak&logoColor=white" alt="Keycloak">
  <img src="https://img.shields.io/badge/Redis-7-DC382D?logo=redis&logoColor=white" alt="Redis">
  <img src="https://img.shields.io/badge/PostgreSQL-15-4169E1?logo=postgresql&logoColor=white" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="MIT License">
</p>

FastCloak sits between users and protected upstream applications:

```text
                         ┌──────────────────┐
                         │      Client      │
                         └────────┬─────────┘
                                  │
                                  │ HTTPS / HTTP
                                  ▼
                    ┌──────────────────────────┐
                    │        FastCloak         │
                    │  FastAPI OAuth2 Proxy    │
                    │                          │
                    │  • Login / Callback      │
                    │  • Session Management    │
                    │  • Role / Group Checks   │
                    │  • Access Control        │
                    │  • Reverse Proxy         │
                    └───────┬─────────┬────────┘
                            │         │
                  OIDC      │         │ Redis
                            ▼         ▼
                     ┌──────────┐  ┌─────────┐
                     │ Keycloak │  │  Redis  │
                     └────┬─────┘  └─────────┘
                          │
                          │ identity / roles / groups
                          ▼
                    ┌────────────────┐
                    │ Upstream App   │
                    │ :9000 / HTTP   │
                    └────────────────┘
```

## Why FastCloak?

Many internal applications should not have to implement authentication, session handling, RBAC, and identity propagation themselves. FastCloak centralizes those concerns at the edge.

Instead of exposing an upstream application directly, place FastCloak in front of it and let the proxy:

- redirect unauthenticated users to the identity provider;
- complete the OAuth 2.0 / OIDC authorization-code flow;
- create and manage application sessions;
- enforce allowlists, roles, and groups;
- expose the authenticated identity to upstream services through trusted headers;
- proxy authenticated HTTP traffic to the target application.

## Features

### Authentication

- OAuth 2.0 / OpenID Connect login flow
- Keycloak integration
- Authorization-code callback handling
- CSRF `state` generation and validation
- Provider-side logout through Keycloak
- Session cookie based authentication

### Authorization

- Role-based access control (RBAC)
- Group-based access control
- Email allowlists
- Email-domain allowlists
- Reusable role-checking dependencies
- Protected application routes

### Reverse proxy

- GET, POST, PUT, DELETE, PATCH, and OPTIONS forwarding
- Query-string preservation
- Request-body forwarding
- Filtering of hop-by-hop headers
- Authenticated identity headers forwarded to upstream services
- `502 Bad Gateway` handling for unreachable upstreams
- `504 Gateway Timeout` handling for upstream timeouts

### Administration

Admin-only endpoints are provided for common Keycloak user-management operations:

- list users
- search users
- create users
- inspect users
- delete users
- list realm roles
- force user logout

### Operations

- Health endpoint: `GET /health`
- Readiness endpoint: `GET /ready`
- Redis-backed session architecture
- PostgreSQL-backed Keycloak in Docker Compose
- Docker Compose development environment
- SQLAlchemy integration
- Pytest test suite

## Tech stack

| Component | Technology |
|---|---|
| API framework | FastAPI |
| Runtime | Python 3.11 |
| ASGI server | Uvicorn |
| Identity provider | Keycloak / OIDC |
| Authentication client | `python-keycloak` |
| HTTP client | HTTPX / aiohttp |
| Session store | Redis |
| Database layer | SQLAlchemy + Alembic |
| Identity database | PostgreSQL |
| Configuration | Pydantic Settings + `.env` |
| Authentication tokens | JOSE / JWT |
| Testing | Pytest + pytest-asyncio |
| Containerization | Docker + Docker Compose |

## Project structure

```text
FastCloak/
├── app/
│   ├── middleware/          # Authentication / request middleware
│   ├── models/              # Application/session models
│   ├── routers/             # HTTP endpoints
│   │   ├── admin.py
│   │   ├── auth.py
│   │   ├── health.py
│   │   ├── protected.py
│   │   └── proxy.py
│   ├── services/            # Business and integration logic
│   │   ├── keycloak_admin_service.py
│   │   ├── keycloak_service.py
│   │   ├── oauth2_service.py
│   │   ├── proxy_service.py
│   │   └── session_service.py
│   ├── utils/               # RBAC, token and Keycloak helpers
│   ├── config.py             # Application settings
│   ├── database.py           # SQLAlchemy setup
│   └── main.py               # Application entry point
├── keycloak/
│   └── realm-export.json     # Development realm configuration
├── tests/
│   ├── auth_test.py
│   ├── conftest.py
│   └── test_roles.py
├── .env.example
├── docker-compose.yml
├── dockerfile
├── requirments.txt
├── run.sh
└── README.md
```

## Request flow

A typical authenticated request follows this path:

```text
1. User requests an upstream resource
             │
             ▼
2. FastCloak checks for an authenticated session
             │
       ┌─────┴─────┐
       │           │
     valid       missing
       │           │
       │           ▼
       │     /auth/login
       │           │
       │           ▼
       │       Keycloak
       │           │
       │       callback
       │           │
       └─────◄─────┘
             │
             ▼
3. Roles / groups / email access checks
             │
       ┌─────┴─────┐
       │           │
     allowed      denied
       │           │
       ▼           ▼
4. Proxy       HTTP 403
   request
       │
       ▼
5. Upstream service
```

## Authentication endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/auth/login` | Start the OIDC login flow |
| `GET` | `/auth/callback` | Handle the identity-provider callback |
| `GET` | `/auth/logout` | End the local and provider session |
| `GET` | `/auth/me` | Return the authenticated user's identity and authorization data |

Example response from `/auth/me`:

```json
{
  "email": "user@example.com",
  "name": "Regular User",
  "username": "user",
  "avatar_url": null,
  "provider": "keycloak",
  "roles": ["app-user"],
  "groups": ["/users"],
  "email_verified": true
}
```

## Protected routes

The project includes example protected endpoints:

| Method | Endpoint | Access |
|---|---|---|
| `GET` | `/api/dashboard` | Authenticated users |
| `GET` | `/api/profile` | Authenticated users |
| `GET` | `/api/admin/panel` | `admin` role |
| `GET` | `/api/manager/reports` | `admin` or `manager` role |

## Admin API

| Method | Endpoint | Access |
|---|---|---|
| `GET` | `/admin/users` | Admin roles |
| `POST` | `/admin/users` | Admin roles |
| `GET` | `/admin/users/{user_id}` | Admin roles |
| `DELETE` | `/admin/users/{user_id}` | Admin roles |
| `GET` | `/admin/roles` | Admin roles |
| `POST` | `/admin/users/{user_id}/logout` | Admin roles |

## Identity propagation

After authentication, FastCloak injects identity information into proxied upstream requests:

```http
X-Auth-User: user@example.com
X-Auth-User-Name: Regular User
X-Auth-Provider: keycloak
X-Auth-Roles: app-user
X-Auth-Groups: /users
```

This lets an upstream application consume trusted identity context without implementing the full login flow itself.

> **Security requirement:** your network architecture must ensure that clients cannot bypass FastCloak and directly reach the upstream service. Otherwise, an attacker could forge these headers.

## Configuration

FastCloak uses environment variables through Pydantic Settings. Copy the example environment file before starting the application:

```bash
cp .env.example .env
```

### Core settings

| Variable | Purpose | Example |
|---|---|---|
| `SECRET_KEY` | Application secret | `change-me` |
| `OAUTH2_PROVIDER` | Identity provider | `keycloak` |
| `KEYCLOAK_SERVER_URL` | Keycloak base URL | `http://localhost:8080` |
| `KEYCLOAK_REALM` | Keycloak realm | `my-realm` |
| `KEYCLOAK_CLIENT_ID` | OIDC client ID | `oauth2-proxy` |
| `KEYCLOAK_CLIENT_SECRET` | OIDC client secret | `...` |
| `KEYCLOAK_REDIRECT_URI` | OIDC callback | `http://localhost:8000/auth/callback` |
| `REDIS_URL` | Session Redis URL | `redis://localhost:6379` |
| `DATABASE_URL` | SQLAlchemy database URL | `sqlite:///./oauth2_proxy.db` |
| `UPSTREAM_URL` | Protected upstream | `http://localhost:9000` |
| `ALLOWED_EMAILS` | Exact email allowlist | `[]` |
| `ALLOWED_DOMAINS` | Domain allowlist | `[]` |
| `REQUIRED_ROLES` | Required Keycloak roles | `[]` |
| `REQUIRED_GROUPS` | Required Keycloak groups | `[]` |
| `COOKIE_SECURE` | Require HTTPS cookies | `true` in production |
| `COOKIE_HTTPONLY` | Prevent JS cookie access | `true` |

The repository's example configuration also defines token/session lifetimes, CORS settings, cookie attributes, and optional Google/GitHub OAuth credentials. The current OAuth service initializes Keycloak as the supported provider path. 

## Docker Compose quick start

The repository includes a development stack containing:

- FastCloak
- Keycloak
- PostgreSQL
- Redis
- an example `httpbin` upstream
- Adminer

Start the stack with:

```bash
cp .env.example .env
docker compose up --build
```

Then use:

```text
FastCloak     http://localhost:8000
Keycloak      http://localhost:8080
Adminer       http://localhost:8081
Upstream      http://localhost:9000
PostgreSQL   localhost:5432
Redis        localhost:6379
```

The Docker Compose file imports the development Keycloak realm from `keycloak/realm-export.json`. That realm defines the `my-realm` realm, an `oauth2-proxy` OIDC client, example roles (`admin`, `manager`, `app-user`, `developer`), and example groups. 

### Development users

The checked-in development realm contains sample users for local testing:

| Username | Role(s) | Group |
|---|---|---|
| `admin` | `admin`, `app-user` | `/admins` |
| `manager` | `manager`, `app-user` | `/managers` |
| `developer` | `developer`, `app-user` | `/developers` |
| `user` | `app-user` | `/users` |

> **Never reuse these development credentials in a real deployment.** The realm export also contains a client secret and sample passwords, so treat it as development-only configuration and rotate secrets before production use.

## Local development

Create a virtual environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirments.txt
```

Configure your environment:

```bash
cp .env.example .env
```

Start FastAPI with Uvicorn:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Open the interactive API documentation at:

```text
http://localhost:8000/docs
```

## Testing

Run the test suite with:

```bash
pytest
```

For coverage:

```bash
pytest --cov=app --cov-report=term-missing
```

The repository currently contains authentication and role-oriented tests under `tests/`.

## Health and observability

FastCloak provides:

```http
GET /health
GET /ready
```

Example health response:

```json
{
  "status": "healthy",
  "timestamp": "2026-01-01T12:00:00",
  "service": "OAuth2 Proxy",
  "version": "1.0.0"
}
```

The current readiness implementation is intentionally lightweight; it reports application readiness but does not yet verify the live Redis/database dependency chain. 

## Production deployment guidance

FastCloak should be treated as an authentication boundary, not simply another FastAPI service.

Before deploying it to production:

1. Put FastCloak behind TLS and a hardened ingress/reverse proxy.
2. Set `COOKIE_SECURE=true` and use a strong, unique `SECRET_KEY`.
3. Replace all development Keycloak credentials and client secrets.
4. Disable or remove the sample development realm users.
5. Ensure upstream services are reachable only from the FastCloak network.
6. Restrict the admin API to trusted operators and networks.
7. Configure explicit roles/groups rather than relying on permissive defaults.
8. Configure Redis persistence/availability according to your session requirements.
9. Configure PostgreSQL for Keycloak with production credentials and backups.
10. Add real dependency checks to `/ready` before using it as an orchestration gate.
11. Add structured logging, metrics, tracing, and rate limiting for internet-facing deployments.
12. Pin and regularly review all production dependencies.

## Security considerations

FastCloak handles credentials, identity assertions, authorization decisions, and session state. That makes the proxy a high-value security component.

### Trust boundary

The headers `X-Auth-User`, `X-Auth-Roles`, and related headers should be trusted only when they originate from FastCloak. Upstream applications must not be directly exposed to untrusted clients.

### Session cookies

The project supports HTTP-only, secure, SameSite, and domain cookie settings. For production deployments, HTTPS and secure cookies should be mandatory.

### Access control defaults

The authorization layer can enforce roles, groups, exact email addresses, and email domains. Review these settings carefully: an empty allowlist changes the decision path and can fall back to provider-side authorization logic.

### Secrets

Do not commit real values for:

- `SECRET_KEY`
- `KEYCLOAK_CLIENT_SECRET`
- Keycloak admin credentials
- Redis credentials
- database credentials

Use environment secrets, a secret manager, or your deployment platform's protected configuration system.

## Known repository caveats

This section is intentionally explicit because documentation should not hide operational issues.

### 1. Dependency filename mismatch

The repository currently stores the dependency file as `requirments.txt`, while `dockerfile` and `run.sh` refer to `requirements.txt`. A clean deployment should standardize this filename before relying on those automation paths.

### 2. Application entry point consistency

The repository's `dockerfile` and startup script expect `app.main:app`. The current checked-in `app/main.py` content shown in the repository is database setup code and does not expose the FastAPI `app` object. The entry point should be reconciled before claiming the container is production-ready.

### 3. Development secrets are present in the realm export

The example Keycloak realm includes a client secret and sample user passwords. These are suitable only for local development. They should not survive into a production deployment.

### 4. Readiness is currently shallow

`/ready` does not yet validate Redis or database connectivity. A production readiness probe should validate the dependencies that are required for successful authenticated requests.

## Roadmap

- [ ] Standardize packaging and dependency file naming
- [ ] Finalize a single authoritative FastAPI entry point
- [ ] Add robust Redis/database readiness checks
- [ ] Add middleware-level security hardening and request limits
- [ ] Add structured logging and correlation IDs
- [ ] Add metrics and tracing
- [ ] Add CI for tests, formatting, linting, and type checking
- [ ] Add security scanning and dependency auditing
- [ ] Add production Docker and development Docker Compose profiles
- [ ] Add comprehensive integration tests against Keycloak + Redis + upstream
- [ ] Document reverse-proxy deployment behind Nginx/Traefik/Caddy
- [ ] Add automated secret and configuration validation

## Contributing

Contributions are welcome.

A useful contribution should ideally include:

- a focused change with a clear problem statement;
- tests for new authentication, authorization, or proxy behavior;
- documentation updates for configuration changes;
- no credentials, tokens, or environment secrets in commits.

Recommended development checks:

```bash
black app tests
flake8 app tests
mypy app
pytest
```

## License

FastCloak is licensed under the [MIT License](LICENSE).

## Author

**Amir Reza Doostdar**

- GitHub: [@Amirrdoustdar](https://github.com/Amirrdoustdar)
- Repository: [Amirrdoustdar/FastCloak](https://github.com/Amirrdoustdar/FastCloak)

---

<p align="center">
  Built with FastAPI, Keycloak, Redis, and PostgreSQL.
</p>.
