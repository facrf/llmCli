# 🚀 Guia de Início Rápido (Getting Started) - llmCli

Bem-vindo ao **llmCli**, seu assistente de inteligência artificial interativo para desenvolvimento no terminal.

---

## 📋 Pré-requisitos

- **Python:** 3.10 ou superior
- **Git:** Instalado e configurado no ambiente
- *(Opcional)* Servidor local de LLM rodando (ex: **llama.cpp**, **Ollama**, **LM Studio**, **vLLM**) ou chave de API para serviços na nuvem (Google Gemini, OpenAI, Anthropic, DeepSeek, Groq, OpenRouter).

---

## ⚙️ 1. Instalação Passo a Passo

### Passo 1: Acesse a Raiz do Repositório

```bash
cd /storage/www/projetos/utils/llmCli
```

### Passo 2: Criar e Ativar o Ambiente Virtual

```bash
# Criar o ambiente virtual na pasta .venv
python3 -m venv .venv

# Ativar o ambiente virtual no Linux
source .venv/bin/activate
```

### Passo 3: Instalar as Dependências

```bash
pip install -r requirements.txt
```

---

## 🔑 2. Configuração de Credenciais e Endpoints

Copie o arquivo de modelo [.env.example](file:///storage/www/projetos/utils/llmCli/.env.example) para `.env`:

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

# Configurações Gerais
DEFAULT_MODEL=gemini/gemini-2.5-flash
ARCHITECT_MODEL=gemini/gemini-2.5-pro
LLMCLI_LANG=pt-BR
YOLO_MODE=false
```

---

## 🧪 3. Verificando o Ambiente e Conectividade

Execute o script de verificação ou use a flag `--models`:

```bash
# Verificar status dos provedores
./bin/llm-cli --models

# Ou executar o script de diagnóstico
python3 scripts/health_check.py
```

Você verá uma tabela informativa exibindo quais servidores locais estão online e quais provedores em nuvem estão configurados e prontos.

---

## 🎮 4. Modos de Uso

### Modo Interativo (REPL - Recomendado)

Inicie a sessão interativa digitando:
```bash
./bin/llm-cli
```

No terminal do assistente, você pode:
- Conversar e solicitar refatorações no código diretamente.
- Adicionar arquivos ao contexto com `/add <caminho>` (com autocomplete `Tab`).
- Ativar o modo autônomo total com `/yolo`.
- Ativar o modo de planejamento em duas etapas com `/architect`.
- Fazer busca semântica local no código com `/index` e `/search <conceito>`.
- Gerar testes com `/gentest <arquivo>` e rodar a suíte com `/test`.
- Exportar a conversa em relatório HTML com `/export html`.

### Modo One-Shot (Execução Direta não-interativa)

Passe instruções diretamente via linha de comando para automações e scripts:
```bash
./bin/llm-cli "Analise o arquivo src/config.py e adicione docstrings completas" --yolo
```

Com carregamento de arquivos específicos e modelo customizado:
```bash
./bin/llm-cli -m llamacpp/default -f src/tools/filesystem.py -y "Adicione suporte a links simbólicos"
```

---

## 📚 Próximos Passos

- [Comandos Slash e Modo YOLO](file:///storage/www/projetos/utils/llmCli/docs/commands_and_yolo.md): Catálogo completo de comandos interativos.
- [Provedores e Modelos de LLM](file:///storage/www/projetos/utils/llmCli/docs/models_and_providers.md): Presets de modelos locais e nuvem.
- [Descoberta Automática de Modelos por IP](file:///storage/www/projetos/utils/llmCli/docs/network_discovery.md): Como conectar e escanear nós de inferência na rede local.
- [Arquitetura do Sistema](file:///storage/www/projetos/utils/llmCli/docs/architecture.md): Estrutura de classes, agentes e subsistemas.
- [Ferramentas e Segurança](file:///storage/www/projetos/utils/llmCli/docs/tools_and_safety.md): Sandbox e checkpoints Git.
- [Diagnóstico e Resolução de Problemas](file:///storage/www/projetos/utils/llmCli/docs/troubleshooting.md): Guia de resolução de problemas comuns.

