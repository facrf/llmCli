# ⚡ Slash Commands and YOLO Mode

**llmCli** features a rich, extensible terminal environment with slash commands, smart autocomplete, and full autonomy modes.

---

## ⚡ 1. What is YOLO Mode (`/yolo`)?

**YOLO** (*You Only Live Once* / Full Autonomous Mode) is designed for maximum developer velocity:

| Feature | Standard Mode (`🛡️ YOLO: OFF`) | YOLO Mode (`⚡ YOLO: ON`) |
| :--- | :--- | :--- |
| **File reads & searches** | Automatic | Automatic |
| **File editing & writes** | Prompts for confirmation | **Executes automatically** |
| **Terminal execution (`run_command`)** | Prompts for confirmation | **Executes automatically** |
| **Git Safety Checkpoints** | Creates snapshots before modifications | **Creates snapshots before modifications** |
| **Rollback via `/undo`** | Available | **Fully Available** |

---

## 🕹️ 2. Slash Commands Reference

### 🤖 Models, Providers & Architecture
- **`/model [name|id]`**: Interactive menu or direct switch of active LLM.
- **`/models`**: Health and connectivity status table of all providers.
- **`/architect [model|off]`**: Toggle two-stage Architect/Editor pipeline.
- **`/scan <ip>`**: Scan remote host for LLM services and models.
- **`/host <ip>`**: Connect to remote machine and configure endpoints automatically.
- **`/mcp`**: List configured MCP servers and active dynamic tools.
- **`/lang [code]`**: Change language (`en`, `pt`, `es`, `de`, `fr`, `zh`, `ru`, `hi`, `auto`).

### 📂 Context, Search & Web
- **`/add <path>`**: Add file or folder to context (`Tab` autocomplete supported).
- **`/drop <path>`**: Remove file from context.
- **`/files`**: List currently tracked files.
- **`/index`**: Index codebase with AST and BM25 for offline semantic search.
- **`/search <query>`**: Search codebase using semantic retrieval.
- **`/web <query>`**: Search the web via DuckDuckGo or Tavily API.

### 🛠️ Git, Quality & Testing
- **`/diff`**: View pending uncommitted Git diff with syntax highlighting.
- **`/commit [msg]`**: AI-generated semantic commit message or direct commit.
- **`/review`**: Run automated technical Code Review on pending changes.
- **`/undo`**: Rollback the last modification or Git snapshot.
- **`/test [args]`**: Run `pytest` test suite with AI-assisted auto-fix.
- **`/gentest <file>`**: Generate complete unit test suite for a file.
- **`/run <cmd>`**: Run terminal command within workspace root.

### 📋 Planning & Session
- **`/plan <goal>`**: Break goal into steps and populate `/todo` checklist.
- **`/todo [add|check|clear]`**: Manage task checklist interactively.
- **`/export [md|html]`**: Export session report to Markdown or HTML.
- **`/paste`**: Enter multiline input mode (`:done` to send).
- **`/compact`**: Compact conversation history into a consolidated summary.
- **`/temp [val]`**: View or adjust temperature (saved per model).
- **`/system [prompt|reset]`**: View, customize, or reset system prompt.
- **`/clear`**: Clear messages while preserving tracked files.
- **`/reset [prefs|all]`**: Reset session or user preferences.
- **`/tokens`**: Show context token consumption and session total.
- **`/help`**: Display command help.
- **`/exit`**: Quit assistant.
