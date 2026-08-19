"""Cliente para a YouTube Data API v3.

Fluxo OAuth desktop (mesmo padrão do google-calendar-agent):
primeira execução abre o navegador; token.json é salvo e reutilizado.
"""

from __future__ import annotations

import os
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from agent_sdk import ToolExecutionError

# O escopo "youtube" (completo) já inclui readonly e upload.
# "youtube.force-ssl" foi descontinuado pelo Google (causava invalid_scope).
SCOPES = [
    "https://www.googleapis.com/auth/youtube",
]


def _secrets_dir() -> Path:
    """Diretório de segredos (override: YOUTUBE_SECRETS_PATH).

    Depths a partir deste arquivo (tools/youtube_client.py):
        parents[0] = tools/
        parents[1] = youtube-publisher-agent/
        parents[2] = raiz do workspace (F:\\ai-platform)
    """
    custom = os.getenv("YOUTUBE_SECRETS_PATH")
    if custom:
        return Path(custom).resolve()
    return Path(__file__).resolve().parents[2] / "secrets" / "youtube"


def _run_flow(client_secrets: Path, token_path: Path) -> Credentials:
    """Executa o fluxo OAuth no navegador e salva o token."""
    flow = InstalledAppFlow.from_client_secrets_file(str(client_secrets), SCOPES)
    creds = flow.run_local_server(port=0)
    token_path.parent.mkdir(parents=True, exist_ok=True)
    token_path.write_text(creds.to_json(), encoding="utf-8")
    return creds


def get_credentials() -> Credentials:
    """Retorna credenciais válidas (cache, refresh ou novo login).

    Raises:
        ToolExecutionError: Se o client_secret.json não existir.
    """
    secrets = _secrets_dir()
    client_secrets = secrets / "client_secret.json"
    token_path = secrets / "token.json"

    if not client_secrets.exists():
        raise ToolExecutionError(
            f"Client secret nao encontrado em {client_secrets}. "
            f"Baixe o OAuth client (Desktop app) no Google Cloud Console.",
            retry=False,
        )

    creds: Credentials | None = None
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            token_path.write_text(creds.to_json(), encoding="utf-8")
        else:
            creds = _run_flow(client_secrets, token_path)

    return creds


def get_youtube_service():
    """Retorna o service da YouTube Data API v3 autenticado."""
    return build(
        "youtube",
        "v3",
        credentials=get_credentials(),
        cache_discovery=False,  # evita warning de cache no Windows
    )