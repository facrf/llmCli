# 🚀 Guia de Início Rápido (Getting Started) - llmCli

Bem-vindo ao **llmCli**, seu assistente de inteligência artificial interativo para desenvolvimento no terminal.

---

## 📋 Pré-requisitos

- **Python:** 3.10 ou superior
- **Git:** Instalado e configurado no ambiente
- *(Opcional)* Servidor local de LLM rodando (ex: **llama.cpp** ou **Ollama**) ou chave de API para serviços na nuvem (Google Gemini, OpenAI, Anthropic, DeepSeek, etc.).

---

## ⚙️ 1. Instalação Passo a Passo

### Passo 1: Clone ou Acesse o Repositório

Navegue até a raiz do projeto:
```bash
cd /storage/www/projetos/utils/llmCli
```

### Passo 2: Criar e Ativar o Ambiente Virtual

```bash
# Criar o ambiente virtual na pasta .venv
python3 -m venv .venv

# Ativar o ambiente virtual no Linux/macOS
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

Edite o arquivo `.env` para incluir suas chaves ou ajustar as URLs locais:

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

# Modelo padrão inicial
DEFAULT_MODEL=gemini/gemini-2.5-flash
YOLO_MODE=false
```

---

## 🧪 3. Verificando o Ambiente

Para verificar se todos os provedores e credenciais estão configurados corretamente, execute:

```bash
./bin/llm-cli --models
```

Você verá uma tabela informativa mostrando quais servidores locais estão online e quais provedores na nuvem possuem chaves válidas.

---

## 🎮 4. Modos de Uso

### Modo Interativo (REPL - Recomendado)

Inicie a sessão interativa digitando:
```bash
./bin/llm-cli
```

### Modo One-Shot (Execução Direta por Linha de Comando)

Você pode passar prompts diretamente pela linha de comando:
```bash
./bin/llm-cli "Analise o arquivo src/config.py e sugira melhorias"
```

Com inclusão de arquivos e modo YOLO ativado:
```bash
./bin/llm-cli -m llamacpp/default -f src/tools/filesystem.py --yolo "Adicione tratamento para links simbólicos"
```

---

## 📚 Próximos Passos

- [Descoberta de Modelos por IP](file:///storage/www/projetos/utils/llmCli/docs/network_discovery.md): Como escanear máquinas na rede e conectar a servidores remotos.
- [Provedores e Modelos](file:///storage/www/projetos/utils/llmCli/docs/models_and_providers.md): Como configurar e subir servidores llama.cpp, Ollama e modelos de nuvem.
- [Comandos e Modo YOLO](file:///storage/www/projetos/utils/llmCli/docs/commands_and_yolo.md): Aprenda todos os comandos slash disponíveis.

- [Ferramentas e Segurança](file:///storage/www/projetos/utils/llmCli/docs/tools_and_safety.md): Entenda os checkpoints automáticos do Git e restrições do workspace.
