from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

try:
    from ..config import PROFILES_DIR
    from ..models import Profile
except ImportError:  # pragma: no cover - allows running the module as a script
    from config import PROFILES_DIR
    from models import Profile


def load_profile(profile_id: str) -> dict[str, Any]:
    """Load an onboarding profile by id from profiles/<id>.yaml."""
    path = Path(PROFILES_DIR) / f"{profile_id}.yaml"
    if not path.exists():
        available = sorted(p.stem for p in Path(PROFILES_DIR).glob("*.yaml"))
        raise FileNotFoundError(f"Profile '{profile_id}' not found. Available: {available}")
    with path.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    try:
        model = Profile.model_validate(raw)
    except ValidationError as exc:
        raise ValueError(f"Profile '{profile_id}' has invalid YAML: {exc}") from exc

    return model.model_dump()
