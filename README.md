# 🤖 llmCli

**llmCli** é um assistente de inteligência artificial interativo para desenvolvimento no terminal (inspirado no OpenAI Codex, Aider e Claude Code), projetado para operar com **LLMs locais** (llama.cpp, Ollama, LM Studio, vLLM) e **LLMs na nuvem** (Google Gemini, OpenAI, Anthropic Claude, DeepSeek, Groq, OpenRouter).

---

## 🌟 Principais Recursos

- 🔄 **Suporte Híbrido Completo:**
  - **Local:** **llama.cpp** (`http://localhost:8080`), **Ollama** (`http://localhost:11434`), **LM Studio** (`http://localhost:1234/v1`), **vLLM** (`http://localhost:8000/v1`).
  - **Nuvem:** **Google Gemini**, **OpenAI GPT-4o / o-series**, **Anthropic Claude 3.7 / 3.5**, **DeepSeek V3 / R1**, **Groq**, **OpenRouter**.
- 📡 **Descoberta Automática de Modelos por IP (`--scan` / `/scan` / `/host`):**
  - Passando o IP de qualquer máquina da sua rede (ex: `192.168.0.11`), o `llmCli` faz uma varredura paralela, detecta os servidores e modelos ativos e permite conectar instantaneamente.
- ⚡ **Modo YOLO (`/yolo`):** Modo de execução autônoma total. Quando ativado, a IA aplica edições de arquivos e executa comandos no terminal sem interromper para pedir confirmações a cada passo.

- 🛠️ **Edição Inteligente de Código:**
  - Suporte a *Function Calling* nativo para modelos de ponta.
  - Suporte a blocos *SEARCH/REPLACE* tolerantes a espaços em branco (estilo Aider) para modelos locais sem function calling nativo.
- 🛡️ **Segurança & Git Checkpoints:**
  - Restrição estrita de escopo ao diretório do projeto ([AGENTS.md](file:///storage/www/projetos/utils/llmCli/AGENTS.md)).
  - Auto-commit de segurança antes de cada edição para permitir reversão instantânea com o comando `/undo`.
- 💻 **Interface Rica de Terminal:**
  - Streaming em tempo real.
  - Autocomplete interativo de comandos e caminhos de arquivos (`prompt_toolkit`).
  - Diffs coloridos com syntax highlighting (`rich`).

---

## 🚀 Como Iniciar

### 1. Criar Ambiente e Instalar Dependências

```bash
# Criar e ativar o ambiente virtual
python3 -m venv .venv
source .venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### 2. Configurar Variáveis de Ambiente

Copie o arquivo de exemplo [.env.example](file:///storage/www/projetos/utils/llmCli/.env.example) para `.env`:

```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas chaves de API ou URLs de servidores locais:

```env
# Provedores em Nuvem
GEMINI_API_KEY=sua_chave_gemini
OPENAI_API_KEY=sua_chave_openai
ANTHROPIC_API_KEY=sua_chave_anthropic
DEEPSEEK_API_KEY=sua_chave_deepseek
GROQ_API_KEY=sua_chave_groq
OPENROUTER_API_KEY=sua_chave_openrouter

# Provedores Locais
LLAMACPP_BASE_URL=http://localhost:8080
OLLAMA_BASE_URL=http://localhost:11434
LMSTUDIO_BASE_URL=http://localhost:1234/v1
```

### 3. Executar o llmCli

```bash
# Iniciar a interface interativa (REPL)
./bin/llm-cli

# Ou executar com um modelo específico
./bin/llm-cli -m llamacpp/default

# Ou iniciar diretamente no modo YOLO
./bin/llm-cli -m gemini/gemini-2.5-flash --yolo

# Ou execução direta (one-shot batch)
./bin/llm-cli "Crie um script em Python que calcule números primos" --yolo
```

---

## 🎮 Comandos Interativos (Slash Commands)

Durante a sessão interativa no terminal:

| Comando | Descrição |
| :--- | :--- |
| `/yolo` | **Alterna o Modo YOLO** (execução autônoma total sem confirmações) |
| `/model <nome>` | Troca o modelo ativo (ex: `/model llamacpp/default`, `/model gemini/gemini-2.5-flash`) |
| `/models` | Exibe o status de conectividade de todos os provedores locais e na nuvem |
| `/add <caminho>` | Adiciona arquivo ou pasta ao contexto da IA (com autocomplete `Tab`) |
| `/drop <caminho>` | Remove arquivo do contexto |
| `/files` | Lista todos os arquivos atualmente no contexto da IA |
| `/diff` | Exibe as alterações Git pendentes com visualizador colorido |
| `/undo` | Reverte o último checkpoint / modificação realizada pela IA |
| `/run <cmd>` | Executa um comando de terminal diretamente no workspace |
| `/clear` | Limpa o histórico de conversas |
| `/reset` | Limpa histórico e remove arquivos do contexto |
| `/tokens` | Exibe estimativa de consumo de tokens |
| `/help` | Exibe menu com todos os comandos |
| `/exit` ou `/quit` | Encerra o assistente |

---

## 🦙 Utilizando com Llama.cpp Local

Para utilizar com o servidor `llama.cpp`:

1. Inicie o servidor do **llama.cpp**:
   ```bash
   ./llama-server -m /caminho/para/seu-modelo.gguf --port 8080 -c 8192
   ```
2. No `llmCli`, selecione o modelo:
   ```bash
   /model llamacpp/default
   ```

---

## 🧪 Executando os Testes

```bash
.venv/bin/pytest -v
```

---

## 🔒 Diretrizes para Agentes de IA

Consulte o arquivo [AGENTS.md](file:///storage/www/projetos/utils/llmCli/AGENTS.md) para detalhes sobre isolamento de diretório e integridade de arquivos.
