# 🏗️ llmCli System Architecture

This document details the modular system architecture, LLM providers adapter layer, offline indexing subsystems, and autonomous agent life cycle in **llmCli**.

---

## 📐 Architecture Overview

```text
llmCli/
├── bin/
│   └── llm-cli               # Main CLI executable
├── src/
│   ├── main.py               # Entrypoint & CLI dispatcher
│   ├── config.py             # Configuration & UserPreferences management
│   ├── i18n.py               # Multi-language translation engine (8 languages)
│   ├── providers/            # LLM adapter implementations
│   │   ├── base.py           # Abstract LLMProvider & message dataclasses
│   │   ├── llamacpp.py       # llama.cpp server adapter (SSE streaming)
│   │   ├── ollama.py         # Ollama adapter
│   │   ├── openai_compatible.py # Universal OpenAI-compatible adapter
│   │   ├── gemini.py         # Google Gemini native REST API
│   │   ├── anthropic.py      # Anthropic Claude native API
│   │   ├── registry.py       # Provider factory, presets, and health checker
│   │   └── scanner.py        # Async network scanner for discovery
│   ├── core/
│   │   ├── agent.py          # Autonomous reasoning loop & Architect pipeline
│   │   ├── session.py        # History, system prompt builder & token accounting
│   │   ├── diff_applier.py   # Whitespace-tolerant SEARCH/REPLACE parser
│   │   ├── todo_manager.py   # Interactive task checklist manager
│   │   └── exporter.py       # Session exporter to Markdown and styled HTML
│   ├── context/
│   │   ├── file_tracker.py   # File context tracking (/add, /drop)
│   │   ├── repomap.py        # Compact repository tree generator
│   │   └── semantic_indexer.py # AST parser, TF-IDF and BM25 local indexer
│   ├── tools/
│   │   ├── base.py           # BaseTool definitions & JSON schemas
│   │   ├── filesystem.py     # Sandboxed file read/write/list/grep tools
│   │   ├── terminal.py       # Sandboxed command execution with timeout
│   │   ├── git_ops.py        # Checkpoints, diffs, semantic commits & undo
│   │   ├── web_tools.py      # DuckDuckGo/Tavily search & URL scraper
│   │   ├── mcp_client.py     # Model Context Protocol (MCP) dynamic client
│   │   └── test_generator.py # Specialized pytest unit test generator
│   └── ui/
│       ├── console.py        # Rich styling, tables, diffs, banners
│       ├── repl.py           # Interactive REPL session
│       └── completer.py      # Smart autocomplete for commands and files
└── tests/                    # Comprehensive pytest test suite
```

---

## 🏛️ Two-Stage Architect / Editor Pipeline

1. **Planning Phase (Architect):** High-reasoning model analyzes codebase context and devises an architectural plan.
2. **Execution Phase (Editor):** Agile active model applies SEARCH/REPLACE blocks and invokes tools.

---

## 🧠 Local Semantic Search (`SemanticIndexer`)

- Chunks Python AST nodes (classes and functions) and text blocks with sliding windows.
- Indexes tokens offline in `.cache/semantic_index.json`.
- Uses BM25 ranking algorithm with term frequency and symbol name boosts for instant retrieval.
