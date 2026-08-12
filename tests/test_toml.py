import tomllib
from pathlib import Path


def test_pyproject_is_valid_toml():
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"

    with pyproject_path.open("rb") as file:
        data = tomllib.load(file)

    assert data["project"]["name"] == "youtube-publisher-agent"


def test_agent_sdk_source_exists():
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"

    with pyproject_path.open("rb") as file:
        data = tomllib.load(file)

    sources = data.get("tool", {}).get("uv", {}).get("sources", {})

    assert "agent-sdk" in sources