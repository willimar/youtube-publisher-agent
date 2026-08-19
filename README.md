# YouTube Publisher Agent

Agente de consulta e publicação no YouTube, executado pela **Agent Platform** (`platform-core`).

> **Escopo v0.1: somente leitura.** O agente consulta canais e playlists reais da conta autenticada. As ferramentas de escrita (`upload_video`, `update_video_metadata`) existem e falam com a API, mas o agente v0.1 é instruído a nunca agir sem pedido explícito — publicação assistida entra na v0.2, com confirmação humana.

## Como funciona

- **Declarativo**: o agente é definido em `agents/youtube-readonly.yml` (spec da plataforma)
- **Ferramentas reais**: módulos em `tools/` registrados via `@tool` do `agent-sdk`
- **LLM local**: Ollama (`llama3.1:8b`) — nada sai da máquina além das chamadas à API do Google
- **OAuth 2.0 desktop**: primeira execução abre o navegador; `token.json` é salvo e reutilizado

## Estrutura

```
youtube-publisher-agent/
├── agents/
│   └── youtube-readonly.yml      # agente v0.1 (somente leitura)
├── tools/
│   ├── __init__.py
│   ├── youtube_client.py         # OAuth + service da YouTube Data API v3
│   └── youtube_tools.py          # 4 ferramentas @tool
├── test_oauth.py                 # teste manual de autenticação
├── pyproject.toml
└── README.md
```

## Requisitos

- Python >= 3.11 e [uv](https://docs.astral.sh/uv/)
- Workspace da plataforma configurado (`setup.ps1` no repo `agent-platform`)
- Ollama rodando com o modelo `llama3.1:8b`
- Projeto no Google Cloud com a **YouTube Data API v3** habilitada

## Setup do OAuth (Google)

1. No [Google Cloud Console](https://console.cloud.google.com):
   - Habilite a **YouTube Data API v3**
   - Em **OAuth consent screen → Scopes**, adicione:
     - `https://www.googleapis.com/auth/youtube`
     - (o escopo completo já engloba `readonly` e `upload`; o antigo `youtube.force-ssl` foi descontinuado e causa `invalid_scope`)
   - Adicione seu e-mail em **Test users** (app em modo testing)
2. Crie um **OAuth client ID → Desktop app** e baixe o JSON
3. Salve como:

```
<raiz do workspace>/secrets/youtube/client_secret.json
```

> Override: defina `YOUTUBE_SECRETS_PATH` apontando para outro diretório de segredos.

4. Rode o teste de autenticação (abre o navegador na 1ª vez e cria `token.json`):

```powershell
cd youtube-publisher-agent
uv run python test_oauth.py
```

Saída esperada: `SUCESSO!` + JSON com seus canais.

## Uso pela plataforma

Da raiz do workspace:

```powershell
# Validação pré-voo
uv run platform validate youtube-publisher-agent/agents/youtube-readonly.yml

# Descoberta de ferramentas
uv run platform tools list youtube-publisher-agent/agents/youtube-readonly.yml

# Execução end-to-end
uv run platform run youtube-publisher-agent/agents/youtube-readonly.yml --verbose
```

Exemplo de resultado real:

```
+------------------------------ Resultado Final ------------------------------+
| O canal do usuário é o "Willimar Augusto Rocha" e existem duas playlists:  |
| "Arquitetura de Software" (privada) e "Favorites" (pública).               |
+-----------------------------------------------------------------------------+
Passos: 3 | Ferramentas usadas: 2 | Duracao: 8.72s
```

> O YAML vive em `agents/` e as ferramentas em `tools/`: a plataforma resolve o diretório de ferramentas por busca ascendente (ADR-004 em `platform-docs`).

## Ferramentas

| Ferramenta | Operação | Descrição |
|---|---|---|
| `youtube_list_channels` | leitura | Lista canais do usuário autenticado (id, título, descrição) |
| `youtube_list_playlists` | leitura | Lista playlists (id, título, privacidade) |
| `youtube_upload_video` | escrita* | Upload resumable de vídeo local (título, descrição, tags, categoria, privacidade) |
| `youtube_update_video_metadata` | escrita* | Atualiza título, descrição, tags e privacidade de um vídeo existente |

\* Disponíveis no agente, mas **não usadas para escrita no v0.1** — ver "Segurança e quota".

## Segurança e quota

- **Menor privilégio por tarefa**: o agente v0.1 só consulta; as instruções do YAML proíbem upload/alteração sem pedido explícito do usuário
- **Quota da YouTube Data API v3**: 10.000 unidades/dia por padrão; um upload custa **1.600 unidades** (~6 uploads/dia). Leituras são baratas
- **Segredos fora do git**: `client_secret.json` e `token.json` ficam em `secrets/youtube/`, fora do repositório

## Roadmap v0.2

- `agents/publisher.yml`: variante de publicação com **confirmação humana** antes de tools de escrita
- Testes de integração marcados (`-m integration`), cientes de quota
- Empacotamento namespaced das tools (eliminar colisão de pacotes `tools/` entre agentes — ADR-006)

## Testes

```powershell
uv run python test_oauth.py    # autenticação + listagem real de canais
```

(Testes automatizados de integração entram na v0.2.)

## Licença

PolyForm Noncommercial License 1.0.0 — uso educacional, pessoal e de pesquisa liberado; uso comercial requer licença separada. Mesma licença dos demais repos da plataforma.

---

Parte da **Agent Platform** — veja `platform-docs` para o spec de agentes (`agent-spec.md`), o contrato de ferramentas (`tool-contract.md`) e os ADRs.