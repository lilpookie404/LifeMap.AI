# 🧭 LifeMap.AI — Phase 0 : Foundations

> Adaptive AI-powered roadmap generator for academics, career, and personal development.

---

## 🚀 Project Goal (Phase 0)
Lay the foundation for LifeMap.AI:
- Basic **FastAPI backend**
- Dockerized via **OrbStack**
- Stub **LLM module** (`fake_generate_roadmap`)
- API routes ready for expansion in Phase 1

### 🎯 MVP outcome
Generate a fake but structured roadmap JSON for a chosen domain (`academics`, `career`, or `personal`).

---

## 🧩 Stack
| Layer | Tool |
|-------|------|
| Backend | FastAPI (Python 3.11) |
| Container | Docker (via OrbStack) |
| Database | PostgreSQL (stubbed for Phase 1) |
| LLM Layer | LangChain placeholder |

---

## ⚙️ Run Locally (without Docker)
cd api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd app
uvicorn main:app --reload

Open 👉 http://127.0.0.1:8000/docs

-- 

## 🐳 Run with Docker (OrbStack)
cd infra
docker compose up --build

Then visit 👉 http://localhost:8000/docs

-- 

## 🧪 Example Endpoints
### Health
GET /health
→ {"status":"ok","env":"dev","version":"0.0.1-phase0"}

### Generate Roadmap
POST /roadmap:generate
Authorization: Bearer dev123
{
  "domain": "career"
}
→ returns roadmap JSON with 5 milestones

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

## ✅ Phase 0 Deliverables
 Working FastAPI service
 Docker/OrbStack integration
 Fake LLM roadmap generator
 Tested /health, /profile:upsert, /roadmap:generate
 Code pushed to GitHub

--
 
## 🔜 Next Phase (Phase 1)
Add PostgreSQL persistence
Define DB schema (users, profiles, roadmaps, feedback)
Replace fake roadmap with stored user data

--

###© 2025 LifeMap.AI · Created by Vaishnavi Awadhiya

