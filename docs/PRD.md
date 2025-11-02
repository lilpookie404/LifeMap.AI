# LifeMap.AI — Phase 0 PRD

**Goal:** Generate a first personalized roadmap for one domain (academics / career / personal) and stub feedback support.

## Inputs
- minimal profile: goal, hours/week, style
- domain string

## Output
JSON roadmap with title, milestones[≥5], constraints, notes.

## Constraints
- responds <10s
- single container run with docker-compose
- schema-stable JSON

## Success
- /health returns ok
- /profile:upsert echoes profile
- /roadmap:generate returns roadmap JSON
