import tomllib
from pathlib import Path


def test_pyproject_is_valid_toml():
    path = Path(__file__).parent.parent / "pyproject.toml"

    with path.open("rb") as file:
        data = tomllib.load(file)

    assert data["project"]["name"] == "youtube-publisher-agent"