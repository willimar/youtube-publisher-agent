from __future__ import annotations

from googleapiclient.discovery import build

from youtube_publisher_agent.auth import get_credentials


def get_youtube_service():
    credentials = get_credentials()

    return build(
        "youtube",
        "v3",
        credentials=credentials,
    )