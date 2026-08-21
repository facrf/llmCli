# 🏗️ Arquitetura do llmCli

Este documento detalha o design modular, os adaptadores de provedores, subsistemas de indexação, persistência e o ciclo de vida do agente no **llmCli**.

---

## 📐 Visão Geral da Arquitetura

```text
llmCli/
├── bin/
│   └── llm-cli               # Script executável de inicialização
├── src/
│   ├── main.py               # Ponto de entrada CLI (Argparse + Dispatcher de execução)
│   ├── config.py             # Configuração (Pydantic, .env, config.yaml e UserPreferences)
│   ├── i18n.py               # Internacionalização e catálogo multi-idioma (8 idiomas)
│   ├── providers/            # Camada de Adaptadores de LLMs
│   │   ├── base.py           # Interface abstrata LLMProvider e dataclasses (ChatMessage, StreamChunk)
│   │   ├── llamacpp.py       # Suporte nativo ao servidor llama.cpp (porta 8080/8081 com SSE)
│   │   ├── ollama.py         # Suporte ao Ollama (porta 11434 e descoberta de tags)
│   │   ├── openai_compatible.py # Adaptador universal (LM Studio, vLLM, DeepSeek, Groq, OpenRouter)
│   │   ├── gemini.py         # API REST nativa do Google Gemini com streaming e function calling
│   │   ├── anthropic.py      # API nativa do Anthropic Claude com streaming e function calling
│   │   ├── registry.py       # Factory de provedores, presets, fallback e verificação de status
│   │   └── scanner.py        # Scanner assíncrono de rede local para descoberta de modelos
│   ├── core/
│   │   ├── agent.py          # Loop autônomo de raciocínio, ferramentas, YOLO e pipeline do Arquiteto
│   │   ├── session.py        # Gestão de histórico, montagem de prompts, tokens e compactação
│   │   ├── diff_applier.py   # Parser e aplicador tolerante de blocos SEARCH/REPLACE (estilo Aider)
│   │   ├── todo_manager.py   # Gerenciador de tarefas interativo e parser de planos (/todo e /plan)
│   │   └── exporter.py       # Exportador de relatórios da sessão em Markdown (.md) e HTML estilizado
│   ├── context/
│   │   ├── file_tracker.py   # Rastreamento de arquivos ativos (/add e /drop com validação)
│   │   ├── repomap.py        # Geração de árvore compacta da base de código para system prompt
│   │   └── semantic_indexer.py # Indexador AST local, TF-IDF e BM25 para busca semântica offline
│   ├── tools/
│   │   ├── base.py           # Definição abstrata BaseTool e schemas JSON
│   │   ├── filesystem.py     # Leitura, gravação, grep e listagem com proteção de workspace
│   │   ├── terminal.py       # Execução controlada de comandos com timeout e sandbox
│   │   ├── git_ops.py        # Checkpoints automáticos, diffs coloridos, commits semânticos e /undo
│   │   ├── web_tools.py      # Busca na internet (DuckDuckGo/Tavily) e extrator de URLs
│   │   ├── mcp_client.py     # Cliente MCP para integração dinâmica de ferramentas externas
│   │   └── test_generator.py # Gerador de prompts especializados para testes com pytest
│   └── ui/
│       ├── console.py        # Formatação visual Rich (Markdown, tabelas, diffs coloridos, alertas)
│       ├── repl.py           # Loop interativo REPL com dispatcher de slash commands
│       └── completer.py      # Autocomplete inteligente de comandos e arquivos (prompt_toolkit)
├── scripts/
│   ├── health_check.py       # Diagnóstico rápido de conectividade de provedores
│   └── run_tests.sh          # Execução rápida da suíte de testes com cobertura
└── tests/                    # Suíte completa de testes automatizados com pytest
```

---

## 🏛️ Pipeline em Duas Etapas: Modo Arquiteto

O Modo Arquiteto divide a resolução de problemas complexos em duas fases especializadas:

1. **Fase de Planejamento (Arquiteto):**
   - Utiliza um modelo com alta capacidade de raciocínio lógico (ex: `gemini-2.5-pro` ou `claude-3-7-sonnet`).
   - Avalia a arquitetura, dependências, requisitos e elabora um plano detalhado de implementação.
2. **Fase de Execução (Editor):**
   - Utiliza o modelo ativo de alta velocidade para aplicar os blocos `SEARCH/REPLACE` e executar chamadas de ferramentas.
   - Solicita confirmação antes da aplicação caso o modo YOLO esteja desativado.

---

## 🧠 Indexador Semântico & RAG Local (`SemanticIndexer`)

O módulo [semantic_indexer.py](file:///storage/www/projetos/utils/llmCli/src/context/semantic_indexer.py) fornece busca vetorial/semântica no código sem dependências pesadas:
- Faz parsing de arquivos Python via biblioteca padrão `ast` para isolar classes e funções.
- Para outras linguagens (`.ts`, `.js`, `.go`, `.rs`, `.java`, `.php`, etc.), particiona o arquivo em janelas lógicas com overlap.
- Constrói um índice invertido em cache local (`.cache/semantic_index.json`).
- Utiliza algoritmo **BM25** combinado com frequência de termos (TF-IDF) e ponderação no nome de símbolos para classificar os trechos mais relevantes.

---

## 🔌 Integração MCP (Model Context Protocol)

O módulo [mcp_client.py](file:///storage/www/projetos/utils/llmCli/src/tools/mcp_client.py) permite conectar ferramentas dinâmicas de terceiros:
- Lê as definições de servidores em `mcp_servers.json`, `.mcp.json` ou `~/.llmcli_mcp.json`.
- Registra automaticamente as ferramentas externas no agente com o prefixo `mcp_<servidor>_<ferramenta>`.
- Permite que a IA invoque serviços externos de banco de dados, deploy, APIs e integrações customizadas.

---

## 💾 Persistência de Preferências do Usuário

A classe `UserPreferences` em [config.py](file:///storage/www/projetos/utils/llmCli/src/config.py) armazena preferências persistentes em `~/.llmcli_preferences.json`:
- **Globais:** Último modelo ativo, modo arquiteto padrão e idioma preferido.
- **Por Modelo:** Temperatura preferida e estado do modo YOLO para cada LLM individualmente.
- O comando `/reset prefs` permite limpar as preferências e restaurar valores padrão a qualquer momento.

---

## ⚡ Modo YOLO e Ciclo de Execução do Agente

1. **Recepção do Prompt:** O usuário envia um comando no REPL ou CLI.
2. **Construção do Contexto:** O [session.py](file:///storage/www/projetos/utils/llmCli/src/core/session.py) monta o prompt com instruções no idioma ativo, repomap e arquivos carregados via `/add`.
3. **Inferência com Streaming:** O provedor emite chunks de texto e tool calls via SSE.
4. **Resolução de Ferramentas / Patches:**
   - Se `yolo_mode=True`, ferramentas de modificação e patches são executados imediatamente com Git snapshot.
   - Se `yolo_mode=False`, uma confirmação interativa é exibida ao usuário (`[s]im / [N]ão / [y]olo / [c]ancelar`).
5. **Auto-commit e Registro de Tokens:** As alterações são commitadas para suportar `/undo` e as estatísticas de tokens são atualizadas.

