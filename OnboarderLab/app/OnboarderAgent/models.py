"""Pydantic models for the declarative onboarding domain."""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class RepositoryAccess(BaseModel):
    model_config = ConfigDict(extra="forbid")

    access: str = "pending"


class PermissionSet(BaseModel):
    model_config = ConfigDict(extra="forbid")

    aws: list[str] = Field(default_factory=list)
    repositories: RepositoryAccess = Field(default_factory=RepositoryAccess)
    ci_cd: list[str] = Field(default_factory=list)


class BaseChecklist(BaseModel):
    model_config = ConfigDict(extra="forbid")

    day_1: list[str] = Field(default_factory=list)
    week_1: list[str] = Field(default_factory=list)


class Repository(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    description: str = ""
    clone_url: str = "<clone-url-pending>"
    bootstrap: str = "# bootstrap pending"
    test: str = "# test command pending"


class Profile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    name: str
    summary: str
    permissions: PermissionSet = Field(default_factory=PermissionSet)
    base_checklist: BaseChecklist = Field(default_factory=BaseChecklist)
    approvals_required: list[str] = Field(default_factory=list)


class Project(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    name: str
    business_goal: str = "Pending documentation."
    architecture_summary: str = "Pending documentation."
    repositories: list[Repository] = Field(default_factory=list)
    key_docs: list[str] = Field(default_factory=list)
    first_tasks: list[str] = Field(default_factory=list)
    risk_notes: list[str] = Field(default_factory=list)
