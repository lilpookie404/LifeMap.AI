# 🧭 LifeMap.AI — Phase 2 : Backend MVP

> Adaptive AI-powered roadmap generator for academics, career, and personal development.

---

## 🚀 Project Goal (Phase 2)
Produce and modify personalized roadmaps with simple bearer auth, core endpoints, and Postgres persistence.

### 🎯 MVP outcome
- POST `/profile:upsert` — store/update user profile domain JSON
- POST `/roadmap:generate` — generate and persist a roadmap version
- POST `/roadmap:revise` — append feedback and create a new version
- GET `/roadmap/{id}` — fetch roadmap + feedback history

---

## 🧩 Stack
| Layer | Tool |
|-------|------|
| Backend | FastAPI (Python 3.11) |
| Container | Docker (via OrbStack) |
| Database | PostgreSQL (SQLModel) |
| LLM Layer | LangChain placeholder |

---

## ⚙️ Quick Start (Docker + Compose)
1) Create an `.env` file at `lifemap/.env` with:

```
API_TOKEN=dev123
ENV=dev

DB_HOST=db
DB_PORT=5432
DB_NAME=lifemap
DB_USER=lifemap
DB_PASSWORD=lifemap_pw
```

2) Bring up the stack and initialize the database:

```
cd infra
docker compose up -d --build
cd ..
bash scripts/dev/migrate.sh
```

3) Open 👉 http://localhost:8000/docs

-- 

## 🧪 Smoke Tests (cURL)
Replace the token if you changed `API_TOKEN`.

Upsert profile:

```
curl -s -X POST http://localhost:8000/profile:upsert \
  -H "Authorization: Bearer dev123" -H "Content-Type: application/json" \
  -d '{"name":"Test User","email":"test@example.com","domain":"career","data":{"hours_per_week":10,"style":"fast"}}'
```

Generate roadmap (adjust `user_id` accordingly):

```
curl -s -X POST http://localhost:8000/roadmap:generate \
  -H "Authorization: Bearer dev123" -H "Content-Type: application/json" \
  -d '{"user_id":1,"domain":"career"}'
```

Revise roadmap (use returned `roadmap_id`):

```
curl -s -X POST http://localhost:8000/roadmap:revise \
  -H "Authorization: Bearer dev123" -H "Content-Type: application/json" \
  -d '{"roadmap_id":1,"feedback":{"signal_type":"missing_topic","notes":"Add system design"}}'
```

Get roadmap by id:

```
curl -s -X GET http://localhost:8000/roadmap/1 \
  -H "Authorization: Bearer dev123"
```

-- 

## 🧪 Example Endpoint
### Health
GET /health
→ {"status":"ok","env":"dev","version":"0.2.0-phase2"}

--

## 🗂️ Structure
lifemap/
├── api/
│   ├── app/
│   │   ├── core/config.py
│   │   ├── llm/provider.py
│   │   └── main.py
│   ├── Dockerfile
│   └── requirements.txt
├── infra/
│   └── docker-compose.yml
├── docs/
│   └── PRD.md
└── scripts/

--

## ✅ Phase 2 Deliverables
 Working FastAPI service with bearer auth
 Docker/OrbStack + Postgres (SQLModel)
 Roadmap persistence + feedback append
 Documented endpoints with OpenAPI summaries

--

## 🔁 Phase 3 — LLM & Adaptive Roadmap

### New
- Prompt templates per domain (`app/llm/prompts.py`).
- Strict JSON schema (`app/llm/schema.py`).
- LLM wrapper with fallback (`app/llm/provider.py`).
- Endpoints now validate plans before saving.

### Configure LLM (optional)
Add to `lifemap/.env` if you want real LLM output (fallback works without it):

```
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```

Restart the API container after changing env.

--
 
## 🔜 Next Phase (Phase 1)
Add PostgreSQL persistence
Define DB schema (users, profiles, roadmaps, feedback)
Replace fake roadmap with stored user data

--

###© 2025 LifeMap.AI · Created by Vaishnavi Awadhiya

