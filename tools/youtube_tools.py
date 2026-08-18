"""Ferramentas reais do youtube-publisher-agent integradas com o agent-sdk."""

from __future__ import annotations

from pathlib import Path

from agent_sdk import ToolExecutionError, ToolResult, tool

from tools.youtube_client import get_youtube_service


@tool("youtube_list_channels")
def youtube_list_channels(max_results: int = 5) -> ToolResult:
    """Lista os canais do usuario autenticado no YouTube.

    Args:
        max_results: Numero maximo de canais a retornar.

    Returns:
        Dicionario com a lista de canais (id, title, description).
    """
    try:
        youtube = get_youtube_service()
        response = youtube.channels().list(
            part="snippet,contentDetails,statistics",
            mine=True,
            maxResults=max_results,
        ).execute()

        channels = [
            {
                "id": item.get("id"),
                "title": item.get("snippet", {}).get("title"),
                "description": item.get("snippet", {}).get("description"),
            }
            for item in response.get("items", [])
        ]
        return ToolResult.ok({"channels": channels})
    except Exception as exc:
        raise ToolExecutionError(f"Falha ao listar canais: {exc}", retry=True) from exc


@tool("youtube_list_playlists")
def youtube_list_playlists(max_results: int = 20) -> ToolResult:
    """Lista playlists do usuario autenticado no YouTube.

    Args:
        max_results: Numero maximo de playlists a retornar.

    Returns:
        Dicionario com a lista de playlists (id, title, privacy).
    """
    try:
        youtube = get_youtube_service()
        response = youtube.playlists().list(
            part="snippet,status",
            mine=True,
            maxResults=max_results,
        ).execute()

        playlists = [
            {
                "id": item.get("id"),
                "title": item.get("snippet", {}).get("title"),
                "privacy": item.get("status", {}).get("privacyStatus"),
            }
            for item in response.get("items", [])
        ]
        return ToolResult.ok({"playlists": playlists})
    except Exception as exc:
        raise ToolExecutionError(f"Falha ao listar playlists: {exc}", retry=True) from exc


@tool("youtube_upload_video")
def youtube_upload_video(
    file_path: str,
    title: str,
    description: str = "",
    tags: list[str] | None = None,
    category_id: str = "22",
    privacy_status: str = "private",
) -> ToolResult:
    """Envia um video local para o YouTube.

    Args:
        file_path: Caminho para o arquivo de video.
        title: Titulo do video.
        description: Descricao do video.
        tags: Lista de tags (opcional).
        category_id: ID da categoria do YouTube (default: 22 = People & Blogs).
        privacy_status: Privacidade (private, public, unlisted).

    Returns:
        Dicionario com video_id e URL.
    """
    path = Path(file_path).expanduser().resolve()
    if not path.exists():
        raise ToolExecutionError(
            f"Arquivo de video nao encontrado: {path}", retry=False
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

        media = MediaFileUpload(str(path), mimetype="video/*", resumable=True)
        request = youtube.videos().insert(
            part="snippet,status", body=body, media_body=media
        )

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"Uploaded {int(status.progress() * 100)}%")

        video_id = response.get("id")
        return ToolResult.ok({
            "video_id": video_id,
            "url": f"https://www.youtube.com/watch?v={video_id}",
        })
    except Exception as exc:
        raise ToolExecutionError(f"Falha ao enviar video: {exc}", retry=True) from exc


@tool("youtube_update_video_metadata")
def youtube_update_video_metadata(
    video_id: str,
    title: str | None = None,
    description: str | None = None,
    tags: list[str] | None = None,
    privacy_status: str | None = None,
) -> ToolResult:
    """Atualiza metadados de um video existente no YouTube.

    Args:
        video_id: ID do video a atualizar.
        title: Novo titulo (opcional).
        description: Nova descricao (opcional).
        tags: Novas tags (opcional).
        privacy_status: Nova privacidade (opcional).

    Returns:
        Dicionario com video_id e status da atualizacao.
    """
    try:
        youtube = get_youtube_service()
        existing = youtube.videos().list(part="snippet,status", id=video_id).execute()

        if not existing.get("items"):
            raise ToolExecutionError(f"Video nao encontrado: {video_id}", retry=False)

        video = existing["items"][0]
        snippet = video["snippet"]
        status = video["status"]

        if title:
            snippet["title"] = title
        if description:
            snippet["description"] = description
        if tags:
            snippet["tags"] = tags
        if privacy_status:
            status["privacyStatus"] = privacy_status

        response = (
            youtube.videos()
            .update(
                part="snippet,status",
                body={"id": video_id, "snippet": snippet, "status": status},
            )
            .execute()
        )

        return ToolResult.ok({
            "video_id": response.get("id"),
            "status": "updated",
        })
    except Exception as exc:
        raise ToolExecutionError(f"Falha ao atualizar video: {exc}", retry=True) from exc