from __future__ import annotations

import os
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

DEFAULT_SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force.ssl",
]


def get_credentials(
    token_file: str | None = None,
    client_secret_file: str | None = None,
    scopes: list[str] | None = None,
) -> Credentials:
    scopes = scopes or DEFAULT_SCOPES

    token_path = Path(
        token_file
        or os.environ.get("YOUTUBE_TOKEN_FILE", "youtube-token.json")
    )

    client_secret_path = Path(
        client_secret_file
        or os.environ.get("YOUTUBE_CLIENT_SECRET_FILE", "client_secret.json")
    )

    credentials: Credentials | None = None

    if token_path.exists():
        credentials = Credentials.from_authorized_user_file(str(token_path), scopes)

    if credentials and credentials.valid:
        return credentials

    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
        token_path.write_text(credentials.to_json(), encoding="utf-8")
        return credentials

    if not client_secret_path.exists():
        raise FileNotFoundError(
            f"Arquivo de client secrets não encontrado: {client_secret_path}. "
            "Defina YOUTUBE_CLIENT_SECRET_FILE ou coloque client_secret.json na raiz."
        )

    flow = InstalledAppFlow.from_client_secrets_file(
        str(client_secret_path),
        scopes=scopes,
    )

    credentials = flow.run_local_server(port=0)
    token_path.write_text(credentials.to_json(), encoding="utf-8")

    return credentials