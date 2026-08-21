# 🏗️ Arquitetura do llmCli

Este documento detalha o design modular, os adaptadores de provedores e o ciclo de vida do agente no **llmCli**.

---

## 📐 Visão Geral da Arquitetura

```text
llmCli/
├── bin/
│   └── llm-cli               # Script executável de inicialização
├── src/
│   ├── main.py               # Ponto de entrada CLI (Argparse + Dispatcher)
│   ├── config.py             # Configuração (Pydantic, .env e config.yaml)
│   ├── providers/            # Camada de Adaptadores de LLMs
│   │   ├── base.py           # Interface LLMProvider e estruturas ChatMessage/StreamChunk
│   │   ├── llamacpp.py       # Suporte nativo ao servidor llama.cpp (porta 8080)
│   │   ├── ollama.py         # Suporte ao Ollama (porta 11434 e descoberta de modelos)
│   │   ├── openai_compatible.py # Adaptador universal (LM Studio, vLLM, DeepSeek, Groq, OpenRouter)
│   │   ├── gemini.py         # API REST nativa do Google Gemini com streaming e tools
│   │   ├── anthropic.py      # API nativa do Anthropic Claude com streaming e tools
│   │   └── registry.py       # Factory de provedores e verificação de saúde/status
│   ├── core/
│   │   ├── session.py        # Gestão de histórico, montagem de prompts e contagem de tokens
│   │   ├── agent.py          # Loop autônomo de raciocínio, chamadas de ferramentas e YOLO
│   │   └── diff_applier.py   # Parser e aplicador de blocos SEARCH/REPLACE (estilo Aider)
│   ├── tools/
│   │   ├── base.py           # Definição e schemas de ferramentas
│   │   ├── filesystem.py     # Leitura, gravação, grep e listagem com proteção de workspace
│   │   ├── terminal.py       # Execução controlada de comandos com timeout
│   │   └── git_ops.py        # Checkpoints automáticos, diffs e comando /undo
│   ├── context/
│   │   ├── file_tracker.py   # Rastreamento de arquivos ativos (/add e /drop)
│   │   └── repomap.py        # Geração compacta de árvore de arquivos do projeto
│   └── ui/
│       ├── console.py        # Formatação Rich (Markdown, painéis, tabelas, diffs)
│       ├── repl.py           # Loop interativo com comandos slash (/yolo, /model, etc.)
│       └── completer.py      # Autocomplete de comandos e caminhos de arquivo no terminal
└── tests/                    # Suíte de testes automatizados (Pytest)
```

---

## ⚡ Modo YOLO (/yolo)

O modo YOLO permite a execução autônoma total do ciclo de desenvolvimento:
- **Modo Padrão (`yolo=False`):** Antes de executar ferramentas que alterem arquivos (`write_file`) ou rodem comandos no terminal (`run_command`), o sistema pausa e solicita autorização do usuário (`[s]im / [N]ão / [y]olo / [c]ancelar`).
- **Modo YOLO (`yolo=True`):** Ações são executadas imediatamente sem interrupção humana, com logs formatados e checkpoints automáticos no Git para fácil reversão via `/undo`.

---

## 🦙 Adaptador llama.cpp

O adaptador dedicado [llamacpp.py](file:///storage/www/projetos/utils/llmCli/src/providers/llamacpp.py) comunica-se com a instância do `llama.cpp` server:
- Suporta streaming SSE de tokens.
- Verifica `/health` e `/props` para detectar automaticamente tamanho de contexto (`n_ctx`) e estado do servidor.
- Compatível com modelos quantizados GGUF locais (Qwen Coder, DeepSeek Coder, Llama 3, etc.).
