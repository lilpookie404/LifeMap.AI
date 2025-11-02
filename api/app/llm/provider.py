from typing import Dict, Any

def fake_generate_roadmap(profile: Dict[str, Any], domain: str) -> Dict[str, Any]:
    hours = profile.get("hours_per_week", 8)
    style = profile.get("style", "balanced")
    title = {
        "academics": "10-Week Study Plan",
        "career": "Backend Developer Internship Prep (10 Weeks)",
        "personal": "Personal Growth Plan (8 Weeks)",
    }.get(domain, f"{domain.title()} Plan")

    return {
        "domain": domain,
        "title": title,
        "milestones": [
            {"id": "m1", "title": "Orientation & Baseline"},
            {"id": "m2", "title": "Core Fundamentals"},
            {"id": "m3", "title": "Projects & Practice"},
            {"id": "m4", "title": "Assessment & Review"},
            {"id": "m5", "title": "Polish & Next Steps"}
        ],
        "constraints": {"hours_per_week": hours, "style": style},
        "notes": "Phase-0 static plan. Replace with real LLM later."
    }
