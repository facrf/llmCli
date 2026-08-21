# 🤖 Models and Providers Guide

**llmCli** supports a universal hybrid architecture. Switch between local or cloud models at any time with `/model <name_or_id>`.

---

## 📋 1. Official Presets and Numerical Selector

Typing `/model` without arguments presents an interactive menu where you can choose a model by **number** or **name**:

| # | Category | Model Name | Description |
| :-: | :--- | :--- | :--- |
| **1** | Local | `llamacpp/default` | Local llama.cpp server (port 8080) |
| **2** | Local | `ollama/qwen2.5-coder:7b` | Ollama Qwen 2.5 Coder 7B |
| **3** | Local | `ollama/deepseek-r1:latest` | Ollama DeepSeek R1 |
| **4** | Local | `lmstudio/default` | LM Studio local server (port 1234) |
| **5** | Local | `vllm/default` | vLLM local server (port 8000) |
| **6** | Cloud | `gemini/gemini-2.5-flash` | Google Gemini 2.5 Flash (Ultra-fast, native tools) |
| **7** | Cloud | `gemini/gemini-2.5-pro` | Google Gemini 2.5 Pro (Deep reasoning) |
| **8** | Cloud | `openai/gpt-4o` | OpenAI GPT-4o Flagship |
| **9** | Cloud | `openai/gpt-4o-mini` | OpenAI GPT-4o Mini (Cost-efficient) |
| **10** | Cloud | `openai/o3-mini` | OpenAI o3-mini Reasoning Model |
| **11** | Cloud | `anthropic/claude-3-7-sonnet-20250219` | Anthropic Claude 3.7 Sonnet |
| **12** | Cloud | `anthropic/claude-3-5-haiku-20241022` | Anthropic Claude 3.5 Haiku |
| **13** | Cloud | `deepseek/deepseek-chat` | DeepSeek V3 |
| **14** | Cloud | `groq/llama-3.3-70b-versatile` | Groq LPU Inference |

---

## 🏛️ 2. Architect Mode (`/architect`)

Use two models collaboratively:
- **Architect:** High-reasoning model (default: `gemini/gemini-2.5-pro`) analyzes architecture and creates technical plans.
- **Editor:** Agile active model (e.g., `gemini-2.5-flash` or `llamacpp/default`) applies code edits and tool calls.

---

## 🦙 3. Local Providers

### llama.cpp Server
```bash
./llama-server -m /path/to/model.gguf --host 0.0.0.0 --port 8080 -c 8192
/model llamacpp/default
```

### Ollama
```bash
ollama run qwen2.5-coder:7b
/model ollama/qwen2.5-coder:7b
```
