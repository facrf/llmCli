# 🛡️ Tools, Safety and Git Checkpoints

**llmCli** operates under strict security and code integrity principles, ensuring actions remain sandboxed within your workspace boundary.

---

## 🔒 1. Workspace Boundary Policy (AGENTS.md)

1. **Path Sandbox:** All file reading and writing tools validate that target paths reside inside the project root (`/storage/www/projetos/utils/llmCli`). Out-of-bounds access is blocked immediately.
2. **Controlled Command Execution:** Shell commands execute with working directory strictly bound to project root. Destructive root commands are intercepted.
3. **Secret Protection:** API keys and sensitive tokens are kept in `.env` and never committed to version control.

---

## 🛠️ 2. Tool Inventory

| Tool | Parameters | Description |
| :--- | :--- | :--- |
| `read_file` | `path`, `start_line`, `end_line` | Reads file content with optional line pagination. |
| `write_file` | `path`, `content` | Writes/overwrites files within workspace with auto-parent directory creation. |
| `list_dir` | `path`, `max_depth` | Lists directory contents and files. |
| `grep_search` | `query`, `path`, `case_sensitive` | Performs text or regex search across workspace files. |
| `find_files` | `pattern`, `path` | Locates files using glob patterns. |
| `run_command` | `command`, `timeout_seconds` | Executes shell commands in workspace with timeout. |
| `semantic_search` | `query`, `top_k` | Retrieves functions/classes from indexed code via BM25. |
| `web_search` | `query`, `max_results` | Searches the web via DuckDuckGo or Tavily. |
| `read_url` | `url`, `max_chars` | Scrapes readable text from online URLs. |
| `mcp_*` | `dynamic kwargs` | Dynamic tools provided by configured external MCP servers. |

---

## ⏪ 3. Automatic Checkpoints & Rollbacks (`/undo`)

Before any file write or patch is applied:
1. The assistant automatically creates a Git snapshot commit.
2. If you wish to revert changes, run:
   ```bash
   /undo
   ```
3. `llmCli` safely rolls back the snapshot, restoring your code immediately.
