"""Tests for the AWS starter preparation script (Phase 5)."""
from __future__ import annotations

import pytest

import accelerator.prepare_starter as prep


SAMPLE_AGENT = '''\
"""Sample starter agent."""
from strands_tools import calculator, current_time

from tools.knowledge_base import search_knowledge_base
from tools.url_fetcher import fetch_url_content
from tools.weather import get_current_weather
from tools.web_search import ddg_web_search

# generic setup

def handler(payload, _context):
    tools = [
        search_knowledge_base,
        ddg_web_search,
        fetch_url_content,
        calculator,
        get_current_weather,
        current_time
    ]

    system_prompt = (
        "You are a helpful AI assistant with memory. "
        "You also have access to: weather information for US locations, "
        "calculator for math, and current time/date."
    )

    return {"tools": tools, "system_prompt": system_prompt}
'''


def test_copy_and_patch_starter(tmp_path, monkeypatch):
    repo_root = prep.REPO_ROOT
    starter_dir = tmp_path / "sample-strands-agentcore-starter"
    monkeypatch.setattr(prep, "STARTER_DIR", starter_dir)
    monkeypatch.setattr(prep, "REPO_ROOT", repo_root)

    # Set up a fake starter structure.
    (starter_dir / "agent" / "tools").mkdir(parents=True, exist_ok=True)
    my_agent = starter_dir / "agent" / "my_agent.py"
    my_agent.write_text(SAMPLE_AGENT, encoding="utf-8")

    prep.copy_domain_files()
    prep.rewrite_tool_imports()
    prep.patch_agent()

    # Domain files copied/generated under renamed modules, all inside agent/
    # (the CDK Agent stack only packages agent/ as the Docker/CodeBuild source).
    assert (starter_dir / "agent" / "onboarding_config.py").exists()
    assert (starter_dir / "agent" / "onboarding_models.py").exists()
    assert (starter_dir / "agent" / "onboarding_prompts.py").exists()
    assert (starter_dir / "agent" / "onboarding_memory_backend.py").exists()
    assert (starter_dir / "agent" / "profiles" / "backend-dev.yaml").exists()
    assert (starter_dir / "agent" / "projects" / "payments-platform.yaml").exists()

    # onboarding_config.py is generated (not copied verbatim) with paths
    # relative to the starter's flat agent/ directory.
    config_text = (starter_dir / "agent" / "onboarding_config.py").read_text(encoding="utf-8")
    assert 'PROFILES_DIR = AGENT_DIR / "profiles"' in config_text
    assert 'PROJECTS_DIR = AGENT_DIR / "projects"' in config_text

    # Tool files are present and imports rewritten to the starter's flat style
    # (no "agent." package prefix, matching my_agent.py's own imports).
    load_profile = starter_dir / "agent" / "tools" / "load_profile.py"
    assert load_profile.exists()
    load_profile_text = load_profile.read_text(encoding="utf-8")
    assert "from onboarding_config import" in load_profile_text
    assert "from agent.onboarding_config import" not in load_profile_text

    track_progress = starter_dir / "agent" / "tools" / "track_progress.py"
    track_progress_text = track_progress.read_text(encoding="utf-8")
    assert "import onboarding_memory_backend as memory_backend" in track_progress_text

    # my_agent.py was patched with imports and tools.
    patched = my_agent.read_text(encoding="utf-8")
    assert "from tools.load_profile import load_profile" in patched
    assert "from tools.load_project import load_project" in patched
    assert "generate_onboarding_plan" in patched
    assert "mark_step_done" in patched
    assert "        load_profile," in patched
    assert "developer onboarding plans" in patched


def test_patch_agent_raises_on_missing_marker(tmp_path, monkeypatch):
    starter_dir = tmp_path / "starter"
    (starter_dir / "agent").mkdir(parents=True)
    my_agent = starter_dir / "agent" / "my_agent.py"
    my_agent.write_text("# nothing relevant\n", encoding="utf-8")

    monkeypatch.setattr(prep, "STARTER_DIR", starter_dir)

    with pytest.raises(ValueError):
        prep.patch_agent()
