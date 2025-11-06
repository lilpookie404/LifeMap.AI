from typing import Dict, Any


def _build_profile_context(profile: Dict[str, Any], domain: str) -> str:
    """Build context string from profile signals for prompt conditioning."""
    hours = profile.get("hours_per_week", 8)
    style = profile.get("style", "balanced")
    target_role = profile.get("target_role") or profile.get("target_job")
    target_exam = profile.get("target_exam")
    experience_level = profile.get("experience_level", "beginner")
    
    context_parts = [
        f"Available time: {hours} hours per week",
        f"Learning style: {style}",
        f"Experience level: {experience_level}",
    ]
    
    if domain == "career" and target_role:
        context_parts.append(f"Target role: {target_role}")
    elif domain == "academics" and target_exam:
        context_parts.append(f"Target exam: {target_exam}")
    
    return ". ".join(context_parts) + "."


def career_prompt(profile: Dict[str, Any]) -> str:
    profile_ctx = _build_profile_context(profile, "career")
    return (
        "You are an expert career coach. Generate a structured JSON roadmap tailored to the user's profile. "
        f"Profile context: {profile_ctx} "
        "Use ONLY strict JSON, no prose. Required fields: "
        "title (string), domain (\"career\"), milestones (array of {id,title,description,resources}), "
        "timeline (array of {week, focus}), resources (array of {name, url}), check_ins (array of {week, goal}). "
        "Adjust milestone complexity, timeline pacing, and resource depth based on hours_per_week and learning style. "
        "If target_role is provided, align milestones toward that specific role."
    )


def academics_prompt(profile: Dict[str, Any]) -> str:
    profile_ctx = _build_profile_context(profile, "academics")
    return (
        "You are an academic mentor. Generate a structured JSON study roadmap tailored to the user's profile. "
        f"Profile context: {profile_ctx} "
        "Use ONLY strict JSON, no prose. Required fields: "
        "title (string), domain (\"academics\"), milestones, timeline, resources, check_ins. "
        "Adapt difficulty, pacing, and milestone depth based on hours_per_week, style, and experience_level. "
        "If target_exam is provided, structure milestones to prepare for that exam."
    )


def personal_prompt(profile: Dict[str, Any]) -> str:
    profile_ctx = _build_profile_context(profile, "personal")
    return (
        "You are a personal development coach. Generate a structured JSON growth plan tailored to the user's profile. "
        f"Profile context: {profile_ctx} "
        "Use ONLY strict JSON, no prose. Required fields: "
        "title (string), domain (\"personal\"), milestones, timeline, resources, check_ins. "
        "Ensure milestones are realistic for the given hours_per_week and align with the learning style."
    )


def get_feedback_fewshot_examples(signal_type: str) -> str:
    """Return few-shot examples for specific feedback types to guide revision."""
    examples = {
        "too_fast": (
            "Example: If user says 'too_fast', slow down the timeline by: "
            "1) Extending milestone durations, 2) Adding more practice weeks between milestones, "
            "3) Reducing weekly focus intensity, 4) Adding buffer weeks for review."
        ),
        "too_easy": (
            "Example: If user says 'too_easy', increase challenge by: "
            "1) Adding advanced topics to milestones, 2) Introducing harder projects earlier, "
            "3) Reducing hand-holding in descriptions, 4) Adding competitive/assessment elements."
        ),
        "missing_topic": (
            "Example: If user says 'missing_topic' with notes, add the requested topic by: "
            "1) Creating a new milestone or inserting into existing one, 2) Adding relevant resources, "
            "3) Adjusting timeline to accommodate, 4) Updating check_ins to track the new topic."
        ),
        "change_goal": (
            "Example: If user says 'change_goal', pivot the roadmap by: "
            "1) Revising milestone titles/descriptions to new goal, 2) Reordering or replacing milestones, "
            "3) Updating resources to match new direction, 4) Adjusting timeline if goal complexity changed."
        ),
        "other": (
            "Example: For 'other' feedback, interpret the notes and apply appropriate changes: "
            "adjust milestones, timeline, resources, or check_ins based on the specific request."
        ),
    }
    return examples.get(signal_type, examples["other"])


def get_revise_prompt(plan: Dict[str, Any], feedback: Dict[str, Any], domain: str) -> str:
    """Build revision prompt with feedback-driven few-shot guidance."""
    signal_type = feedback.get("signal_type", "other")
    notes = feedback.get("notes", "")
    fewshot = get_feedback_fewshot_examples(signal_type)
    
    return (
        f"You are revising a {domain} roadmap based on user feedback. "
        f"Feedback type: {signal_type}. "
        f"{'User notes: ' + notes if notes else ''} "
        f"{fewshot} "
        "Given the existing plan JSON and this feedback, return a NEW strict JSON plan with the same schema. "
        "Make concrete changes that address the feedback while maintaining plan coherence. "
        "Preserve valid parts of the original plan that don't conflict with the feedback."
    )


def get_generate_prompt(profile: Dict[str, Any], domain: str) -> str:
    """Get domain-specific prompt with profile conditioning."""
    prompt_funcs = {
        "career": career_prompt,
        "academics": academics_prompt,
        "personal": personal_prompt,
    }
    func = prompt_funcs.get(domain, career_prompt)
    return func(profile)


