# 🤖 llmCli

> **Language / Idioma:** 🇧🇷 [Português](README.md) | 🇺🇸 [English](README_EN.md) | 🇪🇸 [Español](README_ES.md) | 🇩🇪 [Deutsch](README_DE.md) | 🇫🇷 [Français](README_FR.md) | 🇨🇳 [中文](README_ZH.md) | 🇷🇺 [Русский](README_RU.md) | 🇮🇳 [हिन्दी](README_HI.md)

**llmCli** is a state-of-the-art interactive AI assistant for terminal-based software engineering (inspired by OpenAI Codex, Aider, and Claude Code), engineered to seamlessly operate with **Local LLMs** (llama.cpp, Ollama, LM Studio, vLLM) and **Cloud LLMs** (Google Gemini, OpenAI GPT-4o / o-series, Anthropic Claude 3.7 / 3.5, DeepSeek V3 / R1, Groq, OpenRouter).

---

## 🌟 Key Features

- 🔄 **Full Hybrid Support:**
  - **Local:** **llama.cpp** (`http://localhost:8080`), **Ollama** (`http://localhost:11434`), **LM Studio** (`http://localhost:1234/v1`), **vLLM** (`http://localhost:8000/v1`).
  - **Cloud:** **Google Gemini** (2.5 Flash / Pro), **OpenAI** (GPT-4o / o3-mini), **Anthropic Claude** (3.7 Sonnet / 3.5 Haiku), **DeepSeek** (V3 / R1), **Groq**, and **OpenRouter**.
- 🏛️ **Architect Mode (`/architect` / `/arch`):**
  - Two-stage intelligent pipeline: a high-reasoning model (Architect) formulates a structured technical plan, and a high-speed model (Editor) applies changes and executes tools in the codebase.
- 🌐 **Multi-language Localization (`/lang`):**
  - Native support for 8 languages (**English**, **Portuguese**, **Spanish**, **German**, **French**, **Simplified Chinese**, **Russian**, **Hindi**) with automatic OS locale detection (`/lang auto`).
- ⚡ **YOLO Mode (`/yolo`):**
  - Full autonomous execution. Applies file edits and executes terminal commands continuously without stopping to prompt for manual confirmation at every step.
- 🧠 **Offline Semantic Search & RAG (`/index` / `/search`):**
  - AST-aware indexing of classes, functions, and code blocks with built-in BM25 and TF-IDF scoring, 100% offline with zero external vector DB dependencies.
- 🔌 **Model Context Protocol Client (`/mcp`):**
  - Dynamically connects to external MCP servers defined in `mcp_servers.json` or `~/.llmcli_mcp.json` and registers their tools directly into the AI agent.
- 🌐 **Web Search & URL Reader (`/web` / `read_url`):**
  - Real-time search for up-to-date documentation, API references, and bug solutions via DuckDuckGo or Tavily API.
- 📋 **Checklist & Task Planner (`/plan` / `/todo`):**
  - Automatically breaks high-level engineering goals into structured checklist tasks and tracks progress interactively.
- 🧪 **Test Generation & Auto-Fix (`/gentest` / `/test`):**
  - Automated pytest test suite generation for any source file and interactive test execution with AI diagnostic and auto-repair.
- 💾 **Persistent User Preferences:**
  - Automatic persistence of last active model, YOLO mode, language, and per-model temperature in `~/.llmcli_preferences.json`.
- 📄 **Session Exporter (`/export`):**
  - Exports complete technical session reports to clean **Markdown** (`.md`) or standalone styled **HTML** (`.html`).
- 🛡️ **Strict Safety & Git Checkpoints:**
  - Strict workspace directory isolation boundary ([AGENTS.md](file:///storage/www/projetos/utils/llmCli/AGENTS.md)).
  - Automatic Git snapshots before every modification allowing instant rollbacks via `/undo`.
  - Semantic commit message generation (`/commit`) and automated code reviews (`/review`).

---

## 🚀 Getting Started

### 1. Environment Setup & Dependencies

```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy the example file [.env.example](file:///storage/www/projetos/utils/llmCli/.env.example) to `.env`:

```bash
cp .env.example .env
```

Edit `.env` with your API keys or local server endpoints:

```env
# Cloud Providers
GEMINI_API_KEY=your_gemini_api_key
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
DEEPSEEK_API_KEY=your_deepseek_api_key
GROQ_API_KEY=your_groq_api_key
OPENROUTER_API_KEY=your_openrouter_api_key

# Web Search (Optional - Free DuckDuckGo fallback active by default)
TAVILY_API_KEY=your_tavily_api_key

# Local Providers
LLAMACPP_BASE_URL=http://localhost:8080
OLLAMA_BASE_URL=http://localhost:11434
LMSTUDIO_BASE_URL=http://localhost:1234/v1
VLLM_BASE_URL=http://localhost:8000/v1

# General Settings
DEFAULT_MODEL=gemini/gemini-2.5-flash
ARCHITECT_MODEL=gemini/gemini-2.5-pro
LLMCLI_LANG=en-US
YOLO_MODE=false
```

### 3. Launching llmCli

```bash
# Start interactive REPL session
./bin/llm-cli

# Start with a specific model
./bin/llm-cli -m llamacpp/default

# Connect to a remote machine on local network
./bin/llm-cli --host 192.168.0.11 --yolo

# Direct batch execution (one-shot prompt)
./bin/llm-cli "Create a Python script that calculates prime numbers" --yolo
```

---

## 🎮 Interactive Slash Commands

During an interactive terminal session:

| Command | Syntax | Description |
| :--- | :--- | :--- |
| **`/yolo`** | `/yolo` | Toggle autonomous YOLO mode (saves preference per model). |
| **`/architect`** | `/architect [model]` | Toggle Architect Mode (strong planner + agile editor). |
| **`/lang`** | `/lang [code]` | Change UI & AI language (`en`, `pt`, `es`, `de`, `fr`, `zh`, `ru`, `hi`, `auto`). |
| **`/model`** | `/model [name\|id]` | Interactive menu or switch active model (ex: `/model llamacpp/default`, `/model 6`). |
| **`/models`** | `/models` | Display status and health table of all local and cloud providers. |
| **`/scan`** | `/scan <ip>` | Scan network IP for active LLM inference servers and models. |
| **`/host`** | `/host <ip>` | Connect to remote host and configure endpoints automatically. |
| **`/mcp`** | `/mcp` | List configured MCP servers and active dynamic tools. |
| **`/add`** | `/add <path>` | Add file or folder to AI context (with `Tab` autocomplete). |
| **`/drop`** | `/drop <path>` | Remove file from active context. |
| **`/files`** | `/files` | List all files currently tracked in context. |
| **`/index`** | `/index` | Build offline AST/BM25 index for semantic codebase search. |
| **`/search`** | `/search <query>` | Search indexed code using semantic/BM25 ranking. |
| **`/web`** | `/web <query>` | Search the web (DuckDuckGo/Tavily) for up-to-date solutions. |
| **`/diff`** | `/diff` | Display uncommitted Git diff with syntax highlighting. |
| **`/commit`** | `/commit [msg]` | Generate semantic commit message with AI or commit directly. |
| **`/review`** | `/review` | Run automated Code Review on pending Git changes. |
| **`/undo`** | `/undo` | Rollback the last modification or checkpoint made by the AI. |
| **`/test`** | `/test [args]` | Run `pytest` test suite and offer auto-fix if tests fail. |
| **`/gentest`** | `/gentest <file>` | Generate a complete pytest test suite for the specified file. |
| **`/run`** | `/run <cmd>` | Execute a shell command within the workspace root. |
| **`/plan`** | `/plan <goal>` | Formulate a technical plan and populate `/todo` checklist. |
| **`/todo`** | `/todo [add\|check\|clear]` | Manage interactive session task checklist. |
| **`/export`** | `/export [md\|html]` | Export session report to Markdown or styled HTML. |
| **`/paste`** | `/paste` | Enter multiline paste mode (`:done` to submit, `:cancel` to abort). |
| **`/compact`** | `/compact` | Compact conversation history into a consolidated summary. |
| **`/temp`** | `/temp [value]` | Display or update model temperature (saved per model). |
| **`/system`** | `/system [prompt\|reset]` | View, customize, or reset system prompt. |
| **`/clear`** | `/clear` | Clear conversation history while keeping tracked files. |
| **`/reset`** | `/reset [prefs\|all]` | Reset session and/or user preferences to default. |
| **`/tokens`** | `/tokens` | Display token consumption estimates for context and session. |
| **`/help`** | `/help` | Show command help menu. |
| **`/exit`** | `/exit` or `/quit` | Exit assistant cleanly. |

---

## 📚 Documentation & Guides

- 🚀 [Getting Started](file:///storage/www/projetos/utils/llmCli/docs/en/getting_started.md)
- ⚡ [Commands & YOLO Mode](file:///storage/www/projetos/utils/llmCli/docs/en/commands_and_yolo.md)
- 🤖 [Models & Providers](file:///storage/www/projetos/utils/llmCli/docs/en/models_and_providers.md)
- 🏗️ [Architecture](file:///storage/www/projetos/utils/llmCli/docs/en/architecture.md)
- 🛡️ [Tools & Safety](file:///storage/www/projetos/utils/llmCli/docs/en/tools_and_safety.md)
- 🌐 [Internationalization System](file:///storage/www/projetos/utils/llmCli/docs/i18n.md)
- 📡 [Network Discovery](file:///storage/www/projetos/utils/llmCli/docs/network_discovery.md)
- 🔧 [Troubleshooting](file:///storage/www/projetos/utils/llmCli/docs/troubleshooting.md)

---

## 🧪 Running Tests

```bash
./scripts/run_tests.sh
```
