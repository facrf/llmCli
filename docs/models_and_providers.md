# 🤖 Guia de Provedores e Modelos de LLM

O **llmCli** suporta uma arquitetura híbrida universal. Você pode alternar entre qualquer modelo local ou em nuvem a qualquer momento durante a execução com o comando `/model <nome>`.

---

## 🦙 1. Provedores Locais

### A. llama.cpp Server (Porta 8080)

O `llama.cpp` é ideal para rodar modelos quantizados GGUF (como Qwen 2.5 Coder, DeepSeek Coder ou Llama 3) com alta velocidade em CPU ou GPU.

1. **Iniciando o servidor llama.cpp:**
   ```bash
   ./llama-server -m /caminho/para/seu-modelo.gguf --host 0.0.0.0 --port 8080 -c 8192 --n-gpu-layers 35
   ```
2. **Utilizando no llmCli:**
   ```bash
   /model llamacpp/default
   # ou especificando o nome do modelo
   /model llamacpp/qwen2.5-coder-7b
   ```
3. **Variável no `.env`:**
   ```env
   LLAMACPP_BASE_URL=http://localhost:8080
   ```

---

### B. Ollama (Porta 11434)

O Ollama permite baixar e executar modelos com um único comando.

1. **Baixar e rodar modelo no Ollama:**
   ```bash
   ollama run qwen2.5-coder:7b
   ```
2. **Utilizando no llmCli:**
   ```bash
   /model ollama/qwen2.5-coder:7b
   /model ollama/deepseek-r1:latest
   ```
3. **Variável no `.env`:**
   ```env
   OLLAMA_BASE_URL=http://localhost:11434
   ```

---

### C. LM Studio / vLLM / LocalAI

Qualquer servidor com endpoint compatível com a OpenAI (`/v1/chat/completions`) pode ser utilizado:

```bash
/model lmstudio/meu-modelo-carregado
/model vllm/meu-modelo
```

---

## ☁️ 2. Provedores em Nuvem

| Provedor | Variável de Ambiente | Exemplo de Comando `/model` |
| :--- | :--- | :--- |
| **Google Gemini** | `GEMINI_API_KEY` | `/model gemini/gemini-2.5-flash`<br>`/model gemini/gemini-2.5-pro` |
| **Anthropic Claude** | `ANTHROPIC_API_KEY` | `/model anthropic/claude-3-7-sonnet-20250219`<br>`/model anthropic/claude-3-5-haiku-20241022` |
| **OpenAI** | `OPENAI_API_KEY` | `/model openai/gpt-4o`<br>`/model openai/gpt-4o-mini`<br>`/model openai/o3-mini` |
| **DeepSeek** | `DEEPSEEK_API_KEY` | `/model deepseek/deepseek-chat`<br>`/model deepseek/deepseek-reasoner` |
| **Groq** | `GROQ_API_KEY` | `/model groq/llama-3.3-70b-versatile` |
| **OpenRouter** | `OPENROUTER_API_KEY` | `/model openrouter/anthropic/claude-3.5-sonnet` |

---

## 🔍 3. Verificando Status em Tempo Real

A qualquer momento dentro do REPL, execute:

```bash
/models
```

Isso exibirá a tabela com o estado de saúde e conectividade de todos os provedores configurados.
