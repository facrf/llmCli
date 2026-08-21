# 🤖 llmCli

> **Language / 语言:** 🇧🇷 [Português](README.md) | 🇺🇸 [English](README_EN.md) | 🇪🇸 [Español](README_ES.md) | 🇩🇪 [Deutsch](README_DE.md) | 🇫🇷 [Français](README_FR.md) | 🇨🇳 [中文](README_ZH.md) | 🇷🇺 [Русский](README_RU.md) | 🇮🇳 [हिन्दी](README_HI.md)

**llmCli** 是面向终端开发的新一代全能交互式 AI 编程助手（灵感来源于 OpenAI Codex、Aider 与 Claude Code），原生支持**本地大模型**（llama.cpp、Ollama、LM Studio、vLLM）与**云端大模型**（Google Gemini、OpenAI GPT-4o / o 系列、Anthropic Claude 3.7 / 3.5、DeepSeek V3 / R1、Groq、OpenRouter）。

---

## 🌟 核心特性

- 🔄 **完整的混合模型架构：**
  - **本地：** **llama.cpp** (`http://localhost:8080`), **Ollama** (`http://localhost:11434`), **LM Studio** (`http://localhost:1234/v1`), **vLLM** (`http://localhost:8000/v1`)。
  - **云端：** **Google Gemini** (2.5 Flash / Pro), **OpenAI** (GPT-4o / o3-mini), **Anthropic Claude** (3.7 Sonnet / 3.5 Haiku), **DeepSeek** (V3 / R1), **Groq** 以及 **OpenRouter**。
- 🏛️ **架构师模式 (`/architect` / `/arch`)：**
  - 双阶段智能流水线：高推理能力模型（架构师）负责制定系统化方案，高速度模型（编辑器）负责在代码中执行修改和工具调用。
- 🌐 **多语言国际化支持 (`/lang`)：**
  - 原生支持 8 种语言（**简体中文**、**英语**、**葡萄牙语**、**西班牙语**、**德语**、**法语**、**俄语**、**印地语**），支持根据操作系统 Locale 自动切换 (`/lang auto`)。
- ⚡ **YOLO 自主模式 (`/yolo`)：**
  - 全自动连续执行模式。AI 自动应用代码补丁并执行终端命令，无需每一步都暂停等待用户确认。
- 🧠 **离线语义检索与本地 RAG (`/index` / `/search`)：**
  - 基于 AST 的代码类与函数切片索引，内置 BM25 与 TF-IDF 算法，100% 离线运行，无需外置向量数据库。
- 🔌 **Model Context Protocol (MCP) 扩展 (`/mcp`)：**
  - 支持动态接入 `mcp_servers.json` 或 `~/.llmcli_mcp.json` 中配置的外部 MCP 服务器。
- 🌐 **联网搜索与 URL 网页提取 (`/web` / `read_url`)：**
  - 支持 DuckDuckGo 与 Tavily API 实时查询技术文档、第三方库与报错排查方案。
- 📋 **任务清单与规划管理 (`/plan` / `/todo`)：**
  - 输入目标自动拆解为结构化 Checklist，并在终端实时追踪完成进度。
- 🧪 **单元测试自动生成与智能修复 (`/gentest` / `/test`)：**
  - 自动生成完整的 `pytest` 测试用例；执行测试并在遇到报错时由 AI 自动分析排查与修复代码。
- 💾 **用户偏好持久化：**
  - 自动保存上次使用的模型、YOLO 状态、语言以及各模型独立的温度配置于 `~/.llmcli_preferences.json`。
- 📄 **会话记录导出 (`/export`)：**
  - 将完整开发过程导出为优雅的 **Markdown** (`.md`) 或交互式 **HTML** (`.html`) 报告。
- 🛡️ **严格安全边界与 Git 恢复点：**
  - 严格限制操作于项目目录范围内 ([AGENTS.md](file:///storage/www/projetos/utils/llmCli/AGENTS.md))。
  - 每次代码修改前自动建立 Git Checkpoint 快照，支持通过 `/undo` 一键回滚。
  - 自动生成 Conventional Commits 规范提交信息 (`/commit`) 与代码审查 (`/review`)。

---

## 🚀 快速上手

```bash
# 1. 创建并激活虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# 2. 安装依赖包
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env

# 4. 启动交互终端
./bin/llm-cli
```

---

## 🎮 常用斜杠命令 (Slash Commands)

| 命令 | 说明 |
| :--- | :--- |
| `/yolo` | 切换 YOLO 自主模式（开启/关闭） |
| `/architect` | 切换架构师模式（规划者 + 编辑者双模型协同） |
| `/lang <语言代码>`| 切换界面及 AI 回答语言 (`zh`, `en`, `pt`, `es`, `de`, `fr`, `ru`, `hi`, `auto`) |
| `/model [名称/编号]` | 交互式模型选择菜单或直接切换模型 |
| `/models` | 查看所有本地与云端模型的健康与连接状态 |
| `/scan <IP>` | 扫描局域网 IP 上的 LLM 实例与可用模型 |
| `/host <IP>` | 连接远程局域网主机并自动配置端点 |
| `/add <路径>` | 将文件或目录加入 AI 上下文（支持 `Tab` 补全） |
| `/drop <路径>` | 从上下文移除文件 |
| `/files` | 查看当前上下文载入的文件列表 |
| `/index` | 建立本地代码库 AST/BM25 语义检索索引 |
| `/search <关键词>`| 在已索引代码库中进行语义及关键词检索 |
| `/web <关键词>` | 进行互联网检索 (DuckDuckGo / Tavily) |
| `/diff` | 查看当前待提交的 Git 代码变更 |
| `/commit [信息]` | 使用 AI 分析差异并生成标准规范的 Git 提交 |
| `/review` | 对待提交的代码变更进行技术 Code Review |
| `/undo` | 回滚 AI 上一次所做的修改快照 |
| `/test [参数]` | 运行 `pytest` 并在失败时由 AI 自动修复 |
| `/gentest <文件>`| 为指定文件生成完整的 pytest 单元测试 |
| `/plan <目标>` | 制定详细技术方案并自动录入 `/todo` |
| `/todo` | 查看与管理会话任务清单 |
| `/export [md\|html]`| 导出完整会话报告至 Markdown 或 HTML |
| `/exit` | 退出程序 |
