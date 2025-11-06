# 🧭 LifeMap.AI — Phase 4 : Personalization & Feedback Mechanism

> Adaptive AI-powered roadmap generator for academics, career, and personal development.

---

## 🚀 Project Goal (Phase 4)
Personalized roadmaps with profile signal conditioning and feedback-driven adaptation. Full version history tracking.

### 🎯 Phase 4 Features
- **Profile Conditioning**: Prompts adapt to `hours_per_week`, `style`, `target_role`/`target_exam`, `experience_level`
- **Feedback-Driven Revision**: Few-shot examples guide LLM for `too_fast`, `too_easy`, `missing_topic`, `change_goal`
- **Version History**: Track all roadmap versions showing adaptive evolution
- **Core Endpoints**:
  - POST `/profile:upsert` — store/update user profile domain JSON
  - POST `/roadmap:generate` — generate personalized roadmap (profile-conditioned)
  - POST `/roadmap:revise` — revise with feedback-driven prompts
  - GET `/roadmap/{id}` — fetch roadmap + feedback history
  - GET `/roadmap/{user_id}/{domain}/history` — get all versions for a user/domain

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

Upsert profile (with Phase 4 profile signals):

```
curl -s -X POST http://localhost:8000/profile:upsert \
  -H "Authorization: Bearer dev123" -H "Content-Type: application/json" \
  -d '{"name":"Test User","email":"test@example.com","domain":"career","data":{"hours_per_week":10,"style":"fast","target_role":"Backend Engineer","experience_level":"intermediate"}}'
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

Get version history (Phase 4):

```
curl -s -X GET http://localhost:8000/roadmap/1/career/history \
  -H "Authorization: Bearer dev123"
```

-- 

## 🧪 Example Endpoint
### Health
GET /health
→ {"status":"ok","env":"dev","version":"0.4.0-phase4"}

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

## ✅ Phase 4 Deliverables
- Profile signal conditioning (hours, style, target_role/exam, experience_level)
- Feedback-driven prompts with few-shot examples for each feedback type
- Version history endpoint showing adaptive roadmap evolution
- Enhanced prompts that adapt milestones/timeline based on profile
- Full version tracking with incremental improvements

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
 
## 📊 Profile Signals (Phase 4)

Profile data influences roadmap generation:
- `hours_per_week`: Adjusts timeline pacing and milestone depth
- `style`: `fast`/`balanced`/`slow` affects learning intensity
- `target_role` (career): Aligns milestones toward specific job role
- `target_exam` (academics): Structures milestones for exam prep
- `experience_level`: `beginner`/`intermediate`/`advanced` adjusts complexity

## 🔄 Feedback Types (Phase 4)

Each feedback type triggers specific revision strategies:
- `too_fast`: Extends timeline, adds buffer weeks, reduces intensity
- `too_easy`: Adds advanced topics, harder projects, competitive elements
- `missing_topic`: Creates new milestones, adds resources, adjusts timeline
- `change_goal`: Pivots roadmap, reorders milestones, updates resources
- `other`: Interprets notes and applies appropriate changes

--

###© 2025 LifeMap.AI · Created by Vaishnavi Awadhiya

