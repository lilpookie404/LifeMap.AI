from typing import Dict, Any
import os
import json
from .prompts import DOMAIN_TO_PROMPT
from .schema import RoadmapPlan, validate_plan

try:
    from openai import OpenAI  # type: ignore
except Exception:  # pragma: no cover - optional import
    OpenAI = None  # type: ignore


def _fallback_plan(profile: Dict[str, Any], domain: str) -> Dict[str, Any]:
    hours = profile.get("hours_per_week", 8)
    style = profile.get("style", "balanced")
    base = {
        "domain": domain,
        "title": {
            "academics": "Structured Study Plan",
            "career": "Backend Developer Prep Plan",
            "personal": "Personal Growth Plan",
        }.get(domain, f"{domain.title()} Plan"),
        "milestones": [
            {"id": "m1", "title": "Orientation & Baseline", "resources": []},
            {"id": "m2", "title": "Core Fundamentals", "resources": []},
            {"id": "m3", "title": "Projects & Practice", "resources": []},
            {"id": "m4", "title": "Assessment & Review", "resources": []},
            {"id": "m5", "title": "Polish & Next Steps", "resources": []}
        ],
        "timeline": [{"week": i + 1, "focus": f"Week {i+1} focus"} for i in range(8)],
        "resources": [],
        "check_ins": [{"week": 4, "goal": "Midpoint review"}, {"week": 8, "goal": "Final review"}],
        "constraints": {"hours_per_week": hours, "style": style},
    }
    # Validate shape to guarantee downstream correctness
    return RoadmapPlan.model_validate(base).model_dump()


def _call_openai_json(prompt: str, profile: Dict[str, Any], domain: str) -> Dict[str, Any]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or OpenAI is None:
        return _fallback_plan(profile, domain)

    try:
        client = OpenAI(api_key=api_key)
        system_msg = prompt
        user_msg = json.dumps({"profile": profile, "domain": domain})

        rsp = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg},
            ],
            temperature=0.4,
        )
        content = rsp.choices[0].message.content or "{}"
        try:
            data = json.loads(content)
        except Exception:
            return _fallback_plan(profile, domain)
        try:
            return validate_plan(data).model_dump()
        except Exception:
            return _fallback_plan(profile, domain)
    except Exception:
        # Network/quota/errors → safe fallback
        return _fallback_plan(profile, domain)


def generate_roadmap_struct(profile: Dict[str, Any], domain: str) -> Dict[str, Any]:
    prompt = DOMAIN_TO_PROMPT.get(domain, DOMAIN_TO_PROMPT["career"])  # default to career style
    return _call_openai_json(prompt, profile, domain)


def revise_roadmap_struct(plan: Dict[str, Any], feedback: Dict[str, Any]) -> Dict[str, Any]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or OpenAI is None:
        # Simple local revision: append note to last milestone and add a check-in
        try:
            validated = validate_plan(plan).model_dump()
        except Exception:
            validated = _fallback_plan({}, plan.get("domain", "career"))
        notes = feedback.get("notes") or feedback.get("signal_type", "feedback")
        if validated.get("milestones"):
            validated["milestones"][0]["description"] = (
                (validated["milestones"][0].get("description") or "") + f" Revised: {notes}"
            ).strip()
        validated.setdefault("check_ins", []).append({"week": len(validated.get("timeline", [])) + 1, "goal": "Review changes"})
        return validate_plan(validated).model_dump()

    try:
        client = OpenAI(api_key=api_key)
        system_msg = (
            "You revise plans. Given an existing JSON plan and feedback, return a NEW strict JSON plan with the same schema."
        )
        user_msg = json.dumps({"plan": plan, "feedback": feedback})
        rsp = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg},
            ],
            temperature=0.3,
        )
        content = rsp.choices[0].message.content or "{}"
        try:
            data = json.loads(content)
        except Exception:
            return plan
        try:
            return validate_plan(data).model_dump()
        except Exception:
            return plan
    except Exception:
        # Network/quota/errors → keep prior plan but remain functional
        return plan
