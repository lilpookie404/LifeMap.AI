from typing import Dict, Any
import os
import json
from .prompts import get_generate_prompt, get_revise_prompt
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
        # Include profile data in user message for additional context
        user_msg = json.dumps({"profile": profile, "domain": domain}, indent=2)

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
    """Generate roadmap with profile-conditioned prompts."""
    prompt = get_generate_prompt(profile, domain)
    return _call_openai_json(prompt, profile, domain)


def revise_roadmap_struct(plan: Dict[str, Any], feedback: Dict[str, Any], domain: str) -> Dict[str, Any]:
    """Revise roadmap using feedback-driven prompts with few-shot examples."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or OpenAI is None:
        # Local revision with feedback-aware adjustments
        try:
            validated = validate_plan(plan).model_dump()
        except Exception:
            validated = _fallback_plan({}, domain)
        
        signal_type = feedback.get("signal_type", "other")
        notes = feedback.get("notes") or signal_type
        
        # Apply feedback-aware local edits
        if signal_type == "too_fast" and validated.get("timeline"):
            # Extend timeline by adding buffer weeks
            last_week = max([t.get("week", 0) for t in validated.get("timeline", [])], default=0)
            validated["timeline"].extend([
                {"week": last_week + 1, "focus": "Buffer week for review"},
                {"week": last_week + 2, "focus": "Additional practice"}
            ])
        elif signal_type == "too_easy" and validated.get("milestones"):
            # Add challenge note to first milestone
            if validated["milestones"]:
                validated["milestones"][0]["description"] = (
                    (validated["milestones"][0].get("description") or "") + 
                    " [Enhanced: Increased difficulty per feedback]"
                ).strip()
        elif signal_type == "missing_topic" and notes:
            # Add a new milestone for missing topic
            new_id = f"m{len(validated.get('milestones', [])) + 1}"
            validated.setdefault("milestones", []).append({
                "id": new_id,
                "title": f"Additional: {notes[:50]}",
                "description": f"Added per user feedback: {notes}",
                "resources": []
            })
        
        validated.setdefault("check_ins", []).append({
            "week": len(validated.get("timeline", [])) + 1,
            "goal": f"Review changes from {signal_type} feedback"
        })
        return validate_plan(validated).model_dump()

    try:
        client = OpenAI(api_key=api_key)
        system_msg = get_revise_prompt(plan, feedback, domain)
        user_msg = json.dumps({"plan": plan, "feedback": feedback}, indent=2)
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
