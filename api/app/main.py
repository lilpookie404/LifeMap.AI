from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from .core.config import settings
from .llm.provider import fake_generate_roadmap

app = FastAPI(title=settings.API_NAME, version=settings.API_VERSION)

def verify_token(authorization: Optional[str]):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing/invalid Bearer token")
    token = authorization.split(" ", 1)[1].strip()
    if token != settings.API_TOKEN:
        raise HTTPException(status_code=403, detail="Forbidden")

class ProfileInput(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    profile: Dict[str, Any] = Field(default_factory=dict)

class GenerateInput(BaseModel):
    user_id: Optional[str] = None
    domain: str

@app.get("/health")
def health():
    return {"status": "ok", "env": settings.ENV, "version": settings.API_VERSION}

@app.post("/profile:upsert")
def upsert_profile(payload: ProfileInput, authorization: Optional[str] = Header(None)):
    verify_token(authorization)
    return {"status": "ok", "stored": True, "profile": payload.profile}

@app.post("/roadmap:generate")
def generate_roadmap(payload: GenerateInput, authorization: Optional[str] = Header(None)):
    verify_token(authorization)
    plan = fake_generate_roadmap({"hours_per_week":8,"style":"balanced"}, payload.domain)
    return JSONResponse(content=plan)
