from pydantic import BaseModel, Field, HttpUrl, ValidationError
from typing import List, Optional


class Resource(BaseModel):
    name: str
    url: Optional[HttpUrl] = None


class Milestone(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    resources: List[Resource] = Field(default_factory=list)


class TimelineEntry(BaseModel):
    week: int
    focus: str


class CheckIn(BaseModel):
    week: int
    goal: str


class RoadmapPlan(BaseModel):
    domain: str
    title: str
    milestones: List[Milestone]
    timeline: List[TimelineEntry] = Field(default_factory=list)
    resources: List[Resource] = Field(default_factory=list)
    check_ins: List[CheckIn] = Field(default_factory=list)
    constraints: Optional[dict] = None


def validate_plan(data: dict) -> RoadmapPlan:
    return RoadmapPlan.model_validate(data)


