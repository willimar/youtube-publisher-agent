from youtube_publisher_agent.tools import (
    youtube_list_channels,
    youtube_list_playlists,
    youtube_update_video_metadata,
    youtube_upload_video,
)


def test_tools_have_names():
    assert youtube_list_channels.name == "youtube.list_channels"
    assert youtube_list_playlists.name == "youtube.list_playlists"
    assert youtube_upload_video.name == "youtube.upload_video"
    assert youtube_update_video_metadata.name == "youtube.update_video_metadata"