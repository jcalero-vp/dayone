from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from onboarding_config import PROJECTS_DIR
from onboarding_models import Project


def load_project(project_id: str) -> dict[str, Any]:
    """Load a project definition by id from projects/<id>.yaml."""
    path = Path(PROJECTS_DIR) / f"{project_id}.yaml"
    if not path.exists():
        available = sorted(p.stem for p in Path(PROJECTS_DIR).glob("*.yaml"))
        raise FileNotFoundError(f"Project '{project_id}' not found. Available: {available}")
    with path.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    try:
        model = Project.model_validate(raw)
    except ValidationError as exc:
        raise ValueError(f"Project '{project_id}' has invalid YAML: {exc}") from exc

    return model.model_dump()
