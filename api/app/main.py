from fastapi import FastAPI, Header, HTTPException, Path
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Literal, List
from .core.config import settings
from .llm.provider import generate_roadmap_struct, revise_roadmap_struct
from .llm.schema import validate_plan

from sqlmodel import Session, select, func
from .core.database import engine, User, Profile, Roadmap, Feedback
import json

app = FastAPI(
    title=settings.API_NAME,
    version=settings.API_VERSION,
    description=(
        "LifeMap.AI Phase 2 — Simple bearer auth plus endpoints to produce and revise "
        "personalized roadmaps (profile upsert, generate, revise, fetch)."
    ),
)

# ---------------- Auth ----------------
def verify_token(authorization: Optional[str]):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing/invalid Bearer token")
    token = authorization.split(" ", 1)[1].strip()
    if token != settings.API_TOKEN:
        raise HTTPException(status_code=403, detail="Forbidden")

# ---------------- Schemas ----------------
Domain = Literal["academics", "career", "personal"]

class ProfileUpsertInput(BaseModel):
    name: str
    email: str
    domain: Domain = "career"
    data: Dict[str, Any] = Field(default_factory=dict)

class GenerateInput(BaseModel):
    user_id: int
    domain: Domain

class FeedbackInput(BaseModel):
    signal_type: Literal["too_fast", "too_easy", "missing_topic", "change_goal", "other"]
    notes: Optional[str] = None

class ReviseInput(BaseModel):
    roadmap_id: int
    feedback: FeedbackInput

# ---------------- Health ----------------
@app.get(
    "/health",
    summary="Health check",
    description="Returns service status, environment, and API version.",
)
def health():
    return {"status": "ok", "env": settings.ENV, "version": settings.API_VERSION}

# ---------------- Profile: Upsert ----------------
@app.post(
    "/profile:upsert",
    summary="Upsert user profile",
    description=(
        "Creates or updates a user's profile and stores domain-specific JSON under "
        "`academics`, `career`, or `personal`."
    ),
)
def upsert_profile(payload: ProfileUpsertInput, authorization: Optional[str] = Header(None)):
    verify_token(authorization)

    with Session(engine) as session:
        # find or create user
        user = session.exec(select(User).where(User.email == payload.email)).first()
        if not user:
            user = User(name=payload.name, email=payload.email)
            session.add(user)
            session.commit()
            session.refresh(user)

        # find or create profile
        prof = session.exec(select(Profile).where(Profile.user_id == user.id)).first()
        if not prof:
            prof = Profile(user_id=user.id)
            session.add(prof)

        # store domain-specific JSON
        field_name = f"{payload.domain}_json"
        setattr(prof, field_name, json.dumps(payload.data))

        session.commit()
        return {"status": "ok", "user_id": user.id, "updated_domain": payload.domain}

# ---------------- Roadmap: Generate (v1 or next) ----------------
@app.post(
    "/roadmap:generate",
    summary="Generate roadmap",
    description=(
        "Generates the next version of a roadmap for a user and domain using the current "
        "profile context; persists to the `roadmaps` table."
    ),
)
def generate_roadmap(payload: GenerateInput, authorization: Optional[str] = Header(None)):
    verify_token(authorization)

    with Session(engine) as session:
        user = session.get(User, payload.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        profile = session.exec(select(Profile).where(Profile.user_id == user.id)).first()
        # choose domain data if present; otherwise empty dict
        domain_json = None
        if profile:
            domain_json = getattr(profile, f"{payload.domain}_json", None)
        profile_data = json.loads(domain_json) if domain_json else {"hours_per_week": 8, "style": "balanced"}

        # build plan via LLM (with safe fallback) and validate
        plan = generate_roadmap_struct(profile=profile_data, domain=payload.domain)
        plan = validate_plan(plan).model_dump()

        # compute next version
        # compute next version safely (MAX can be NULL on first insert)
        res = session.exec(
            select(func.max(Roadmap.version)).where(
                (Roadmap.user_id == user.id) & (Roadmap.domain == payload.domain)
            )
        ).first()
        curr_max = None
        if res is not None:
            # res can be a scalar or a tuple depending on driver/version
            curr_max = res[0] if isinstance(res, (tuple, list)) else res
        next_version = (curr_max or 0) + 1

        # persist roadmap
        rm = Roadmap(user_id=user.id, domain=payload.domain, version=next_version, plan_json=json.dumps(plan))
        session.add(rm)
        session.commit()
        session.refresh(rm)

        return {"roadmap_id": rm.id, "version": rm.version, "plan": plan}

# ---------------- Roadmap: Revise (new version + feedback) ----------------
@app.post(
    "/roadmap:revise",
    summary="Revise roadmap",
    description=(
        "Creates a new roadmap version based on prior plan and provided feedback, and "
        "appends the feedback to the `feedback` table."
    ),
)
def revise_roadmap(payload: ReviseInput, authorization: Optional[str] = Header(None)):
    verify_token(authorization)

    with Session(engine) as session:
        prev = session.get(Roadmap, payload.roadmap_id)
        if not prev:
            raise HTTPException(status_code=404, detail="Roadmap not found")

        # save feedback
        fb = Feedback(
            roadmap_id=prev.id,
            signal_type=payload.feedback.signal_type,
            notes=payload.feedback.notes
        )
        session.add(fb)

        prev_plan = json.loads(prev.plan_json)
        domain = prev.domain
        # LLM-aware revision with validation (falls back locally if no API key)
        new_plan = revise_roadmap_struct(plan=prev_plan, feedback=payload.feedback.model_dump())
        new_plan = validate_plan(new_plan).model_dump()

        # version bump
        new_version = prev.version + 1
        new_rm = Roadmap(
            user_id=prev.user_id,
            domain=domain,
            version=new_version,
            plan_json=json.dumps(new_plan)
        )
        session.add(new_rm)
        session.commit()
        session.refresh(new_rm)

        return {"roadmap_id": new_rm.id, "version": new_rm.version, "plan": json.loads(new_rm.plan_json)}

# ---------------- Roadmap: Get by ID ----------------
@app.get(
    "/roadmap/{roadmap_id}",
    summary="Get roadmap by id",
    description="Returns a stored roadmap including its plan and any associated feedback entries.",
)
def get_roadmap(roadmap_id: int = Path(..., gt=0), authorization: Optional[str] = Header(None)):
    verify_token(authorization)

    with Session(engine) as session:
        rm = session.get(Roadmap, roadmap_id)
        if not rm:
            raise HTTPException(status_code=404, detail="Roadmap not found")

        fbs = session.exec(select(Feedback).where(Feedback.roadmap_id == roadmap_id)).all()
        return {
            "roadmap_id": rm.id,
            "user_id": rm.user_id,
            "domain": rm.domain,
            "version": rm.version,
            "created_at": rm.created_at.isoformat(),
            "plan": json.loads(rm.plan_json),
            "feedback": [{"id": x.id, "signal_type": x.signal_type, "notes": x.notes, "created_at": x.created_at.isoformat()} for x in fbs]
        }
