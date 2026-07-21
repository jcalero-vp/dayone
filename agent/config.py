from __future__ import annotations

import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PROFILES_DIR = REPO_ROOT / "profiles"
PROJECTS_DIR = REPO_ROOT / "projects"
PROGRESS_DIR = REPO_ROOT / ".local-progress"
ENV_FILE = REPO_ROOT / ".env"


def load_runtime_config(dotenv_path: str | os.PathLike[str] | None = None) -> dict[str, str]:
    """Load runtime configuration from a dotenv file or process environment.

    The Bedrock-backed agent requires at minimum AWS_REGION and BEDROCK_MODEL_ID.
    """
    env_path = Path(dotenv_path or ENV_FILE)
    values: dict[str, str] = {}

    if env_path.exists():
        for raw_line in env_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip()

    merged = {**os.environ, **values}

    required_keys = ["AWS_REGION", "BEDROCK_MODEL_ID"]
    missing = [key for key in required_keys if not merged.get(key)]
    if missing:
        raise ValueError(
            "Missing required configuration: " + ", ".join(missing) + 
            ". Create .env from .env.example and set the values before running the Bedrock agent."
        )

    return {
        "AWS_REGION": merged["AWS_REGION"],
        "BEDROCK_MODEL_ID": merged["BEDROCK_MODEL_ID"],
    }
