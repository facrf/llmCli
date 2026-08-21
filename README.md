# 🤖 llmCli

> **Language / Idioma:** 🇧🇷 [Português](README.md) | 🇺🇸 [English](README_EN.md) | 🇪🇸 [Español](README_ES.md) | 🇩🇪 [Deutsch](README_DE.md) | 🇫🇷 [Français](README_FR.md) | 🇨🇳 [中文](README_ZH.md) | 🇷🇺 [Русский](README_RU.md) | 🇮🇳 [हिन्दी](README_HI.md)

**llmCli** é um assistente de inteligência artificial interativo de última geração para desenvolvimento no terminal (inspirado no OpenAI Codex, Aider e Claude Code), projetado para operar perfeitamente com **LLMs locais** (llama.cpp, Ollama, LM Studio, vLLM) e **LLMs na nuvem** (Google Gemini, OpenAI GPT-4o / o-series, Anthropic Claude 3.7 / 3.5, DeepSeek V3 / R1, Groq, OpenRouter).


---

## 🌟 Principais Recursos

- 🔄 **Suporte Híbrido Completo:**
  - **Local:** **llama.cpp** (`http://localhost:8080`), **Ollama** (`http://localhost:11434`), **LM Studio** (`http://localhost:1234/v1`), **vLLM** (`http://localhost:8000/v1`).
  - **Nuvem:** **Google Gemini** (2.5 Flash / Pro), **OpenAI** (GPT-4o / o3-mini), **Anthropic Claude** (3.7 Sonnet / 3.5 Haiku), **DeepSeek** (V3 / R1), **Groq** e **OpenRouter**.
- 🏛️ **Modo Arquiteto (`/architect` / `/arch`):**
  - Pipeline inteligente em duas etapas: um modelo de raciocínio de ponta (Arquiteto) planeja a solução estruturada e um modelo ágil (Editor) aplica as alterações e executa ferramentas no código.
- 🌐 **Internacionalização e Multi-idioma (`/lang`):**
  - Suporte nativo a 8 idiomas (**Português**, **English**, **Español**, **Deutsch**, **Français**, **简体中文**, **Русский**, **हिन्दी**) com auto-detecção via locale do sistema operacional (`/lang auto`).
- ⚡ **Modo YOLO (`/yolo`):**
  - Execução autônoma contínua. Aplica modificações de arquivos e roda comandos no terminal sem interromper o fluxo com confirmações manuais a cada passo.
- 🧠 **Busca Semântica & RAG Local (`/index` / `/search`):**
  - Indexação inteligente de classes, funções e blocos de código com pontuação BM25 e TF-IDF integrada, 100% offline e sem dependências externas pesadas.
- 🔌 **Extensibilidade via Model Context Protocol (`/mcp`):**
  - Conexão dinâmica com servidores MCP externos configurados em `mcp_servers.json` ou `~/.llmcli_mcp.json`.
- 🌐 **Pesquisa Web & Leitura de URLs (`/web` / `read_url`):**
  - Consulta informações atualizadas, documentações de bibliotecas e soluções de erros na web via DuckDuckGo ou Tavily API.
- 📋 **Checklist & Planejador de Tarefas (`/plan` / `/todo`):**
  - Criação automática de tarefas estruturadas a partir de objetivos em linguagem natural e acompanhamento do progresso em tempo real.
- 🧪 **Geração & Execução de Testes com Auto-Fix (`/gentest` / `/test`):**
  - Geração automática de suítes de testes unitários completos com `pytest` e execução de testes com diagnóstico e auto-correção de falhas via IA.
- 💾 **Preferências Persistentes do Usuário:**
  - Persistência automática do último modelo utilizado, modo YOLO, idioma e temperatura individual por modelo em `~/.llmcli_preferences.json`.
- 📄 **Exportação de Sessões (`/export`):**
  - Exporta relatórios técnicos completos da sessão em **Markdown** (`.md`) ou **HTML estilizado** interativo (`.html`).
- 🛡️ **Segurança Rigorosa & Git Checkpoints:**
  - Isolamento estrito de escopo ao diretório do projeto ([AGENTS.md](file:///storage/www/projetos/utils/llmCli/AGENTS.md)).
  - Auto-commit de segurança antes de cada edição para permitir reversão instantânea com o comando `/undo`.
  - Geração de mensagens de commit semânticas (`/commit`) e Code Review automatizado (`/review`).

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

Edite o arquivo `.env` com suas credenciais ou endpoints desejados:

```env
# Provedores em Nuvem
GEMINI_API_KEY=sua_chave_gemini
OPENAI_API_KEY=sua_chave_openai
ANTHROPIC_API_KEY=sua_chave_anthropic
DEEPSEEK_API_KEY=sua_chave_deepseek
GROQ_API_KEY=sua_chave_groq
OPENROUTER_API_KEY=sua_chave_openrouter

# Pesquisa na Web (Opcional - DuckDuckGo gratuito ativo por padrão)
TAVILY_API_KEY=sua_chave_tavily

# Provedores Locais
LLAMACPP_BASE_URL=http://localhost:8080
OLLAMA_BASE_URL=http://localhost:11434
LMSTUDIO_BASE_URL=http://localhost:1234/v1
VLLM_BASE_URL=http://localhost:8000/v1

# Configurações Padrão
DEFAULT_MODEL=gemini/gemini-2.5-flash
ARCHITECT_MODEL=gemini/gemini-2.5-pro
LLMCLI_LANG=pt-BR
YOLO_MODE=false
```

### 3. Executar o llmCli

```bash
# Iniciar a interface interativa (REPL)
./bin/llm-cli

# Ou executar com um modelo específico
./bin/llm-cli -m llamacpp/default

# Conectar e escanear servidores em outra máquina da rede local
./bin/llm-cli --host 192.168.0.11 --yolo

# Execução direta não-interativa (one-shot batch)
./bin/llm-cli "Crie um script em Python que calcule números primos" --yolo
```

---

## 🎮 Comandos Interativos (Slash Commands)

Durante a sessão interativa no terminal:

| Comando | Sintaxe | Descrição |
| :--- | :--- | :--- |
| **`/yolo`** | `/yolo` | Alterna o modo autônomo YOLO (salva preferência por modelo). |
| **`/architect`** | `/architect [modelo]` | Alterna o Modo Arquiteto (planejamento forte + editor ágil). |
| **`/lang`** | `/lang <código>` | Altera o idioma do sistema (`pt`, `en`, `es`, `de`, `fr`, `zh`, `ru`, `hi`, `auto`). |
| **`/model`** | `/model <nome>` | Menu interativo ou troca direta de modelo (ex: `/model llamacpp/default`). |
| **`/models`** | `/models` | Exibe status de conectividade e saúde de todos os provedores. |
| **`/scan`** | `/scan <ip>` | Escaneia um IP/host e detecta servidores e modelos de LLM ativos. |
| **`/host`** | `/host <ip>` | Conecta ao IP informado e configura endpoints locais automaticamente. |
| **`/mcp`** | `/mcp` | Lista servidores MCP e ferramentas dinâmicas ativas. |
| **`/add`** | `/add <caminho>` | Adiciona arquivo ou pasta ao contexto da IA (com autocomplete `Tab`). |
| **`/drop`** | `/drop <caminho>` | Remove arquivo do contexto ativo. |
| **`/files`** | `/files` | Lista todos os arquivos atualmente anexados ao contexto. |
| **`/index`** | `/index` | Indexa a base de código para busca semântica/RAG local. |
| **`/search`** | `/search <termo>` | Executa busca semântica/BM25 no código indexado. |
| **`/web`** | `/web <pesquisa>` | Pesquisa na web (DuckDuckGo/Tavily) e traz respostas atualizadas. |
| **`/diff`** | `/diff` | Exibe as alterações Git pendentes com visualizador colorido. |
| **`/commit`** | `/commit [msg]` | Gera mensagem de commit semântica com IA ou cria commit direto. |
| **`/review`** | `/review` | Executa Code Review técnico das alterações Git pendentes. |
| **`/undo`** | `/undo` | Reverte o último checkpoint / alteração realizada pela IA. |
| **`/test`** | `/test [args]` | Executa `pytest` e sugere correção automática caso ocorra falha. |
| **`/gentest`** | `/gentest <arquivo>` | Gera suíte completa de testes unitários com pytest para o arquivo indicado. |
| **`/run`** | `/run <comando>` | Executa um comando de terminal diretamente no workspace. |
| **`/plan`** | `/plan <objetivo>` | Cria plano técnico estruturado e gera tarefas automáticas no `/todo`. |
| **`/todo`** | `/todo [add\|check\|clear]` | Gerencia o checklist interativo de tarefas da sessão. |
| **`/export`** | `/export [md\|html]` | Exporta relatório técnico completo da sessão em Markdown ou HTML. |
| **`/paste`** | `/paste` | Modo multilinha para colar grandes blocos de código (`:done` para enviar). |
| **`/compact`** | `/compact` | Compacta o histórico da conversa gerando resumo consolidado. |
| **`/temp`** | `/temp [valor]` | Exibe ou altera a temperatura do modelo ativo (salva preferência). |
| **`/system`** | `/system [prompt\|reset]` | Exibe, personaliza ou redefine o System Prompt do assistente. |
| **`/clear`** | `/clear` | Limpa o histórico de mensagens mantendo os arquivos no contexto. |
| **`/reset`** | `/reset [prefs\|all]` | Limpa sessão ou redefine preferências salvas do usuário para o padrão. |
| **`/tokens`** | `/tokens` | Exibe estimativa de consumo de tokens do contexto e da sessão. |
| **`/help`** | `/help` | Exibe o menu com todos os comandos disponíveis. |
| **`/exit`** | `/exit` ou `/quit` | Encerra o assistente. |

---

## 📚 Documentação Detalhada

Explore os guias detalhados na pasta [`docs/`](file:///storage/www/projetos/utils/llmCli/docs):

- 🚀 [Guia de Início Rápido](file:///storage/www/projetos/utils/llmCli/docs/getting_started.md): Instalação, configuração passo a passo e primeiros comandos.
- 🏗️ [Arquitetura do Sistema](file:///storage/www/projetos/utils/llmCli/docs/architecture.md): Estrutura de pastas, adaptadores de LLM, pipeline de raciocínio e subsistemas.
- ⚡ [Comandos Slash e Modo YOLO](file:///storage/www/projetos/utils/llmCli/docs/commands_and_yolo.md): Detalhamento completo de todos os comandos e atalhos.
- 🤖 [Provedores e Modelos de LLM](file:///storage/www/projetos/utils/llmCli/docs/models_and_providers.md): Configuração de llama.cpp, Ollama, LM Studio, vLLM e modelos de nuvem.
- 📡 [Descoberta Automática de Modelos por IP](file:///storage/www/projetos/utils/llmCli/docs/network_discovery.md): Varredura assíncrona de rede e conexão com nós de inferência remotos.
- 🛡️ [Ferramentas e Segurança](file:///storage/www/projetos/utils/llmCli/docs/tools_and_safety.md): Política de isolamento do workspace, catálogo de ferramentas e checkpoints Git.
- 🔧 [Diagnóstico e Resolução de Problemas](file:///storage/www/projetos/utils/llmCli/docs/troubleshooting.md): Perguntas frequentes e soluções para erros comuns.

---

## 🧪 Executando os Testes

Execute a suíte completa de testes automatizados com cobertura:

```bash
# Via script auxiliar
./scripts/run_tests.sh

# Ou diretamente via pytest no ambiente virtual
.venv/bin/pytest -v --cov=src
```

---

## 🔒 Diretrizes para Agentes de IA

Consulte o arquivo [AGENTS.md](file:///storage/www/projetos/utils/llmCli/AGENTS.md) para detalhes sobre isolamento de diretório e integridade de arquivos.

