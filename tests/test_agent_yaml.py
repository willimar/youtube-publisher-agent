from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")


def test_agent_yaml_parses():
    agent_path = (
        Path(__file__).parent.parent / "agents" / "youtube-publisher.yaml"
    )

    data = yaml.safe_load(agent_path.read_text(encoding="utf-8"))

    assert data["name"] == "youtube-publisher-agent"
    assert data["version"] == "0.1.0"
    assert "tools" in data
    assert "prompts" in data