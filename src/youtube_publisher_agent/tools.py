"""Ferramentas do youtube-publisher-agent.

Este módulo ainda está em fase de scaffold. No passo seguinte, as funções
serão decoradas/registradas como ferramentas @tool do agent-sdk.
"""

from __future__ import annotations

TOOL_NAMES = [
    "youtube.list_channels",
    "youtube.list_playlists",
    "youtube.upload_video",
    "youtube.update_video_metadata",
]


def youtube_list_channels(max_results: int = 5):
    """Lista canais do usuário autenticado no YouTube."""
    raise NotImplementedError("Será implementado no passo 3 do F4.")


def youtube_list_playlists(max_results: int = 20):
    """Lista playlists do usuário autenticado no YouTube."""
    raise NotImplementedError("Será implementado no passo 3 do F4.")


def youtube_upload_video(
    file_path: str,
    title: str,
    description: str = "",
    tags: list[str] | None = None,
    category_id: str = "22",
    privacy_status: str = "private",
):
    """Envia um vídeo local para o YouTube."""
    raise NotImplementedError("Será implementado no passo 3 do F4.")


def youtube_update_video_metadata(
    video_id: str,
    title: str | None = None,
    description: str | None = None,
    tags: list[str] | None = None,
    category_id: str | None = None,
    privacy_status: str | None = None,
):
    """Atualiza metadados de um vídeo existente no YouTube."""
    raise NotImplementedError("Será implementado no passo 3 do F4.")