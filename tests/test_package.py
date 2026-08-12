from youtube_publisher_agent import AGENT_NAME, __version__


def test_version():
    assert __version__ == "0.1.0"


def test_agent_name():
    assert AGENT_NAME == "youtube-publisher-agent"