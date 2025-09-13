# Technical Specification for DocSign Project

## Architecture (Including Alembic)
- **Framework**: FastAPI with async SQLAlchemy (asyncpg driver), Jinja2 templates, static files.
- **Layers**: core/ (settings), db/ (models, sessions), routers/ (endpoints), services/ (integrations), templates/, static/.
- **DB Init**: Auto-create tables on startup; enable pg_trgm and unaccent extensions.
- **Alembic**: env.py loads DATABASE_URL from .env; supports autogenerate revisions. Workflow: `alembic revision --autogenerate -m "msg"` then `alembic upgrade head`.

## Backend
- **Components**:
  - main.py: Registers routers, mounts statics, startup hook (init_db).
  - core/settings.py: Config (AUTH_BASE_URL, AUTH_ENDPOINT_PATH, DATABASE_URL).
  - routers/auth.py: SIGEX-based ECP login, sets uid cookie.
  - routers/user.py: Dashboard, email update, logout (clear cookie).
  - routers/documents.py: Partner search (pg_trgm similarity), document creation.
  - services/auth_service.py: SIGEX integration.
- **Endpoints**:
  - Auth: POST /get (nonce), POST /check (verify signature).
  - User: GET /user/dashboard, POST /user/email, GET /user/logout.
  - Documents: GET /documents/partners?query=&limit=, POST /documents.
- **Features**:
  - ECP login (NCALayer → SIGEX), certificate parsing, user upsert, uid cookie.
  - User dashboard with profile (email required; modal for add/change).
  - Partner fuzzy search by full_name, organization, email, iin, bin; sorted by similarity.
  - Document creation: Owner + up to 4 partners, base64 PDF storage, participant/status tracking.

## Frontend
- **Components**:
  - Templates: index.html (home), user_dashboard.html (dashboard), partials/create_document_tab.html.
  - Scripts: main.js (ECP login), create_document.js (doc creation), ncaWebSocketManager.js, ncalayer.js, authService.js.
- **Features**:
  - Home: ECP/egovMobile login buttons.
  - Dashboard: Tabs for Create Document, Pending Signatures, My Documents, Profile.
  - Create Document: Single-field partner search, results list; select up to 4, removable list; PDF upload/preview (<embed>); POST to server with success/error messages.
  - Profile: Display IIN/BIN/Full Name/Org/Date; email modal; logout button.
  - Auth Flow: WebSocket to NCALayer, get nonce, sign, verify; handle phys/jur persons.

## Database
- **Tables**:
  - users: id (PK), iin (UNIQUE, index), bin (index, nullable), full_name (nullable), organization (nullable), email, created_at, updated_at.
  - documents: id (PK), owner_id, title, file_name, file_base64, status, created_at, updated_at.
  - document_participants: id (PK), document_id, user_id, role (initiator|signer), status (pending|signed), signed_at.
- **Indexes**: GIN + pg_trgm on full_name, organization, email, iin, bin.
- **Migrations**: Autogenerate from models; apply via Alembic.

## Quick Start (Local)
1. Clone, create venv: `python -m venv venv; venv\Scripts\activate`.
2. Install: `pip install -r requirements.txt`.
3. .env: `DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost/localdb`.
4. Create DB `localdb` in PostgreSQL; run app once for extensions.
5. Migrations: `alembic upgrade head`; for changes: `alembic revision --autogenerate -m "msg"; alembic upgrade head`.
6. Run: `python main.py`; access http://localhost:8000.

## Implemented
- Full ECP auth cycle with SIGEX/NCALayer.
- User management (upsert, profile, email).
- Partner fuzzy search.
- Document creation/storage.
- DB auto-init and migrations.

## Not Implemented
- egovMobile auth.
- PDF signing/verification.
- Document signing workflows.