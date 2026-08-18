"""Teste de autenticacao OAuth e listagem de canais do YouTube."""

from __future__ import annotations

import json

from tools.youtube_tools import youtube_list_channels


def main() -> None:
    print("Iniciando teste de autenticacao e listagem de canais...")

    try:
        resultado = youtube_list_channels(max_results=5)
    except Exception as exc:
        print(f"ERRO: {exc}")
        return

    if resultado.sucesso:
        print("SUCESSO!")
        print(json.dumps(resultado.dados, ensure_ascii=False, indent=2))
    else:
        print(f"FALHA: {resultado.erro}")


if __name__ == "__main__":
    main()