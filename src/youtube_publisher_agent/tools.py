from __future__ import annotations

from pathlib import Path

from agent_sdk import ToolExecutionError, ToolResult, tool

from youtube_publisher_agent.youtube_client import get_youtube_service


@tool(
    name="youtube.list_channels",
    description="Lista os canais do usuário autenticado no YouTube.",
)
def youtube_list_channels(max_results: int = 5) -> ToolResult:
    try:
        youtube = get_youtube_service()

        response = (
            youtube.channels()
            .list(
                part="snippet,contentDetails,statistics",
                mine=True,
                maxResults=max_results,
            )
            .execute()
        )

        channels = []

        for item in response.get("items", []):
            channels.append(
                {
                    "id": item.get("id"),
                    "title": item.get("snippet", {}).get("title"),
                    "description": item.get("snippet", {}).get("description"),
                    "video_count": item.get("statistics", {}).get("videoCount"),
                    "view_count": item.get("statistics", {}).get("viewCount"),
                }
            )

        return ToolResult(
            success=True,
            data={"channels": channels},
        )

    except Exception as exc:
        raise ToolExecutionError(f"Falha ao listar canais: {exc}") from exc


@tool(
    name="youtube.list_playlists",
    description="Lista playlists do usuário autenticado no YouTube.",
)
def youtube_list_playlists(max_results: int = 20) -> ToolResult:
    try:
        youtube = get_youtube_service()

        response = (
            youtube.playlists()
            .list(
                part="snippet,status",
                mine=True,
                maxResults=max_results,
            )
            .execute()
        )

        playlists = []

        for item in response.get("items", []):
            playlists.append(
                {
                    "id": item.get("id"),
                    "title": item.get("snippet", {}).get("title"),
                    "description": item.get("snippet", {}).get("description"),
                    "privacy": item.get("status", {}).get("privacyStatus"),
                    "published_at": item.get("snippet", {}).get("publishedAt"),
                }
            )

        return ToolResult(
            success=True,
            data={"playlists": playlists},
        )

    except Exception as exc:
        raise ToolExecutionError(f"Falha ao listar playlists: {exc}") from exc


@tool(
    name="youtube.upload_video",
    description="Envia um vídeo local para o YouTube.",
)
def youtube_upload_video(
    file_path: str,
    title: str,
    description: str = "",
    tags: list[str] | None = None,
    category_id: str = "22",
    privacy_status: str = "private",
) -> ToolResult:
    path = Path(file_path).expanduser().resolve()

    if not path.exists():
        raise ToolExecutionError(f"Arquivo de vídeo não encontrado: {path}")

    if privacy_status not in {"public", "unlisted", "private"}:
        raise ToolExecutionError(
            "privacy_status deve ser 'public', 'unlisted' ou 'private'."
        )

    try:
        from googleapiclient.http import MediaFileUpload

        youtube = get_youtube_service()

        body = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags or [],
                "categoryId": category_id,
            },
            "status": {
                "privacyStatus": privacy_status,
                "selfDeclaredMadeForKids": False,
            },
        }

        media = MediaFileUpload(
            str(path),
            mimetype="video/*",
            chunksize=1024 * 1024 * 10,
            resumable=True,
        )

        request = youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media,
        )

        response = None

        while response is None:
            status, response = request.next_chunk()

        video_id = response.get("id")

        return ToolResult(
            success=True,
            data={
                "video_id": video_id,
                "video_url": f"https://www.youtube.com/watch?v={video_id}",
                "privacy_status": privacy_status,
            },
        )

    except Exception as exc:
        raise ToolExecutionError(f"Falha ao enviar vídeo: {exc}") from exc


@tool(
    name="youtube.update_video_metadata",
    description="Atualiza metadados de um vídeo existente no YouTube.",
)
def youtube_update_video_metadata(
    video_id: str,
    title: str | None = None,
    description: str | None = None,
    tags: list[str] | None = None,
    category_id: str | None = None,
    privacy_status: str | None = None,
) -> ToolResult:
    try:
        youtube = get_youtube_service()

        existing = (
            youtube.videos()
            .list(
                part="snippet,status",
                id=video_id,
            )
            .execute()
        )

        items = existing.get("items", [])

        if not items:
            raise ToolExecutionError(f"Vídeo não encontrado: {video_id}")

        video = items[0]

        snippet = video.get("snippet", {})
        status = video.get("status", {})

        if title is not None:
            snippet["title"] = title

        if description is not None:
            snippet["description"] = description

        if tags is not None:
            snippet["tags"] = tags

        if category_id is not None:
            snippet["categoryId"] = category_id

        if privacy_status is not None:
            if privacy_status not in {"public", "unlisted", "private"}:
                raise ToolExecutionError(
                    "privacy_status deve ser 'public', 'unlisted' ou 'private'."
                )

            status["privacyStatus"] = privacy_status

        body = {
            "id": video_id,
            "snippet": snippet,
            "status": status,
        }

        updated = (
            youtube.videos()
            .update(
                part="snippet,status",
                body=body,
            )
            .execute()
        )

        return ToolResult(
            success=True,
            data={
                "video_id": updated.get("id"),
                "title": updated.get("snippet", {}).get("title"),
                "privacy_status": updated.get("status", {}).get("privacyStatus"),
            },
        )

    except ToolExecutionError:
        raise

    except Exception as exc:
        raise ToolExecutionError(f"Falha ao atualizar vídeo: {exc}") from exc