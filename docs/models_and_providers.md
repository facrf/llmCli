# 🤖 Guia de Provedores e Modelos de LLM

O **llmCli** suporta uma arquitetura híbrida universal. Você pode alternar entre qualquer modelo local ou em nuvem a qualquer momento durante a execução com o comando `/model <nome_ou_id>`.

---

## 📋 1. Presets Oficiais e Seletor Numérico

Ao digitar `/model` sem argumentos no terminal interativo, uma tabela formatada é exibida permitindo escolher o modelo digitando apenas o **número** ou o **nome**:

| # | Categoria | Nome do Modelo | Descrição |
| :-: | :--- | :--- | :--- |
| **1** | Local | `llamacpp/default` | Servidor llama.cpp local (porta 8080) |
| **2** | Local | `ollama/qwen2.5-coder:7b` | Ollama com modelo Qwen 2.5 Coder 7B |
| **3** | Local | `ollama/deepseek-r1:latest` | Ollama com modelo DeepSeek R1 |
| **4** | Local | `lmstudio/default` | Servidor LM Studio local (porta 1234) |
| **5** | Local | `vllm/default` | Servidor vLLM local (porta 8000) |
| **6** | Nuvem | `gemini/gemini-2.5-flash` | Google Gemini 2.5 Flash (Ultra-rápido, Function Calling) |
| **7** | Nuvem | `gemini/gemini-2.5-pro` | Google Gemini 2.5 Pro (Raciocínio complexo e coding profundo) |
| **8** | Nuvem | `openai/gpt-4o` | OpenAI GPT-4o Flagship |
| **9** | Nuvem | `openai/gpt-4o-mini` | OpenAI GPT-4o Mini (Ágil e econômico) |
| **10** | Nuvem | `openai/o3-mini` | OpenAI o3-mini Reasoning Model |
| **11** | Nuvem | `anthropic/claude-3-7-sonnet-20250219` | Anthropic Claude 3.7 Sonnet (Hybrid Thinking) |
| **12** | Nuvem | `anthropic/claude-3-5-haiku-20241022` | Anthropic Claude 3.5 Haiku |
| **13** | Nuvem | `deepseek/deepseek-chat` | DeepSeek V3 (Ótimo custo-benefício para código) |
| **14** | Nuvem | `groq/llama-3.3-70b-versatile` | Groq LPU Inference (Incrível velocidade de geração) |

> **Dica:** Você pode digitar `/model 6` ou `/model gemini/gemini-2.5-flash` diretamente.

---

## 🏛️ 2. Modo Arquiteto (`/architect`)

O Modo Arquiteto permite usar dois modelos em conjunto:
- **Arquiteto:** Um modelo com profunda capacidade de raciocínio lógico (padrão: `gemini/gemini-2.5-pro`) analisa a base de código, dependências e planeja a solução.
- **Editor:** O modelo ativo ágil (ex: `gemini/gemini-2.5-flash`, `gpt-4o-mini` ou `llamacpp/default`) executa a edição dos arquivos e chamadas de ferramentas.

### Ativando o Modo Arquiteto:
```bash
# Alternar estado on/off
/architect

# Especificar um modelo específico de arquiteto
/architect anthropic/claude-3-7-sonnet-20250219
/architect gemini/gemini-2.5-pro
```

---

## 🦙 3. Provedores Locais

### A. llama.cpp Server (Porta 8080)
1. **Iniciando o servidor llama.cpp:**
   ```bash
   ./llama-server -m /caminho/para/seu-modelo.gguf --host 0.0.0.0 --port 8080 -c 8192 --n-gpu-layers 35
   ```
2. **Utilizando no llmCli:**
   ```bash
   /model llamacpp/default
   ```
3. **Variável no `.env`:**
   ```env
   LLAMACPP_BASE_URL=http://localhost:8080
   ```

### B. Ollama (Porta 11434)
1. **Baixar e rodar modelo no Ollama:**
   ```bash
   ollama run qwen2.5-coder:7b
   ```
2. **Utilizando no llmCli:**
   ```bash
   /model ollama/qwen2.5-coder:7b
   ```
3. **Variável no `.env`:**
   ```env
   OLLAMA_BASE_URL=http://localhost:11434
   ```

### C. LM Studio / vLLM / LocalAI
```bash
/model lmstudio/default
/model vllm/default
```

---

## ☁️ 4. Provedores em Nuvem e Variáveis de Ambiente

| Provedor | Variável de Ambiente | Modelos Suportados |
| :--- | :--- | :--- |
| **Google Gemini** | `GEMINI_API_KEY` | `gemini/gemini-2.5-flash`, `gemini/gemini-2.5-pro`, `gemini/gemini-2.0-flash` |
| **Anthropic Claude** | `ANTHROPIC_API_KEY` | `anthropic/claude-3-7-sonnet-20250219`, `anthropic/claude-3-5-haiku-20241022` |
| **OpenAI** | `OPENAI_API_KEY` | `openai/gpt-4o`, `openai/gpt-4o-mini`, `openai/o3-mini`, `openai/o1` |
| **DeepSeek** | `DEEPSEEK_API_KEY` | `deepseek/deepseek-chat`, `deepseek/deepseek-reasoner` |
| **Groq** | `GROQ_API_KEY` | `groq/llama-3.3-70b-versatile`, `groq/deepseek-r1-distill-llama-70b` |
| **OpenRouter** | `OPENROUTER_API_KEY` | `openrouter/<qualquer_modelo>` |
| **Tavily (Web Search)**| `TAVILY_API_KEY` | Utilizado pelo `/web` e `web_search` (opcional, fallback DuckDuckGo gratuito ativo) |

---

## 🔄 5. Fallback e Recomendação Automática

Caso ocorra um erro de rede, timeout ou quota em um provedor, o `llmCli` sugere automaticamente uma alternativa configurada compatível (ex: se o Gemini falhar e o OpenAI estiver configurado, sugere trocar para `openai/gpt-4o`).

---

## 🔍 6. Verificando Status em Tempo Real

A qualquer momento dentro do REPL, execute:

```bash
/models
```

Isso exibirá a tabela com o estado de saúde e conectividade de todos os provedores locais e na nuvem.

