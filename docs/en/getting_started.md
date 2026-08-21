# 🚀 Getting Started with llmCli

Welcome to **llmCli**, your next-generation interactive AI coding assistant for the terminal.

---

## 📋 Prerequisites

- **Python:** 3.10 or higher
- **Git:** Installed and initialized in your repository
- *(Optional)* Local LLM server running (e.g., **llama.cpp**, **Ollama**, **LM Studio**, **vLLM**) or API keys for Cloud providers (Google Gemini, OpenAI, Anthropic, DeepSeek, Groq, OpenRouter).

---

## ⚙️ 1. Step-by-Step Installation

### Step 1: Access Repository Root

```bash
cd /storage/www/projetos/utils/llmCli
```

### Step 2: Create & Activate Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🔑 2. Configure Credentials & Endpoints

Copy [.env.example](file:///storage/www/projetos/utils/llmCli/.env.example) to `.env`:

```bash
cp .env.example .env
```

Edit `.env` with your API keys and local endpoint settings:

```env
# Cloud Providers
GEMINI_API_KEY=your_gemini_key
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
DEEPSEEK_API_KEY=your_deepseek_key
GROQ_API_KEY=your_groq_key
OPENROUTER_API_KEY=your_openrouter_key

# Web Search (Optional)
TAVILY_API_KEY=your_tavily_key

# Local Endpoints
LLAMACPP_BASE_URL=http://localhost:8080
OLLAMA_BASE_URL=http://localhost:11434
LMSTUDIO_BASE_URL=http://localhost:1234/v1
VLLM_BASE_URL=http://localhost:8000/v1

# Defaults
DEFAULT_MODEL=gemini/gemini-2.5-flash
ARCHITECT_MODEL=gemini/gemini-2.5-pro
LLMCLI_LANG=en-US
YOLO_MODE=false
```

---

## 🧪 3. Check Provider Connectivity

Run the status check command:

```bash
./bin/llm-cli --models
```

This displays a table indicating which local servers are online and which cloud providers are configured.

---

## 🎮 4. Usage Modes

### Interactive REPL (Recommended)

Start the interactive terminal:
```bash
./bin/llm-cli
```

### Direct Execution (One-Shot Batch)

Pass instructions directly on the command line:
```bash
./bin/llm-cli "Analyze src/config.py and improve error handling" --yolo
```

---

## 📚 Next Guides

- [Slash Commands & YOLO Mode](file:///storage/www/projetos/utils/llmCli/docs/en/commands_and_yolo.md)
- [Models & Providers](file:///storage/www/projetos/utils/llmCli/docs/en/models_and_providers.md)
- [System Architecture](file:///storage/www/projetos/utils/llmCli/docs/en/architecture.md)
- [Tools & Safety](file:///storage/www/projetos/utils/llmCli/docs/en/tools_and_safety.md)
- [Internationalization System](file:///storage/www/projetos/utils/llmCli/docs/i18n.md)
