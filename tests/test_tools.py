from youtube_publisher_agent.tools import TOOL_NAMES


def test_tool_names_are_unique():
    assert len(TOOL_NAMES) == len(set(TOOL_NAMES))


def test_expected_tools_exist():
    expected = {
        "youtube.list_channels",
        "youtube.list_playlists",
        "youtube.upload_video",
        "youtube.update_video_metadata",
    }

    assert set(TOOL_NAMES) == expected