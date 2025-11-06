from typing import Dict


def career_prompt() -> str:
    return (
        "You are an expert career coach. Generate a structured JSON roadmap for a backend developer track. "
        "Use ONLY strict JSON, no prose. Fields: title (string), domain (\"career\"), milestones (array of {id,title,description,resources}), "
        "timeline (array of {week, focus}), resources (array of {name, url}), check_ins (array of {week, goal}). "
        "Tailor to constraints like hours_per_week and style from the provided profile."
    )


def academics_prompt() -> str:
    return (
        "You are an academic mentor. Generate a structured JSON study roadmap. "
        "Use ONLY strict JSON, no prose. Fields: title (string), domain (\"academics\"), milestones, timeline, resources, check_ins. "
        "Adapt difficulty and pacing to the profile."
    )


def personal_prompt() -> str:
    return (
        "You are a personal development coach. Generate a structured JSON growth plan. "
        "Use ONLY strict JSON, no prose. Fields: title (string), domain (\"personal\"), milestones, timeline, resources, check_ins. "
        "Ensure plan is realistic for the given hours_per_week."
    )


DOMAIN_TO_PROMPT: Dict[str, str] = {
    "career": career_prompt(),
    "academics": academics_prompt(),
    "personal": personal_prompt(),
}


