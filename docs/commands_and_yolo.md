# ⚡ Comandos Slash e Modo YOLO

O **llmCli** oferece uma interface interativa rica e altamente extensível no terminal com suporte completo a comandos *slash* (`/`), autocomplete contextual e modo autônomo.

---

## ⚡ 1. O que é o Modo YOLO (`/yolo`)?

O modo **YOLO** (*You Only Live Once* / Full Autonomous Access) foi desenvolvido para máxima velocidade de desenvolvimento:

### Comparativo de Modos

| Recurso | Modo Normal (`🛡️ YOLO: OFF`) | Modo YOLO (`⚡ YOLO: ON`) |
| :--- | :--- | :--- |
| **Leitura de arquivos e buscas** | Automática | Automática |
| **Edição e gravação de arquivos** | Pede confirmação (`[s]im / [N]ão / [y]olo / [c]ancelar`) | **Executa automaticamente** |
| **Comandos de terminal (`run_command`)** | Pede confirmação prévia | **Executa automaticamente** |
| **Git Checkpoints de Segurança** | Cria snapshot antes de cada alteração | **Cria snapshot antes de cada alteração** |
| **Reversão com `/undo`** | Totalmente disponível | **Totalmente disponível** |
| **Persistência** | Salvo por modelo e globalmente | **Salvo por modelo e globalmente** |

### Como Ativar / Desativar

1. **Dentro da sessão interativa:**
   ```bash
   /yolo
   ```
   A barra de prompt mudará dinamicamente para `[... | ⚡ YOLO: ON]`.

2. **Na inicialização da CLI:**
   ```bash
   ./bin/llm-cli --yolo
   # ou com a flag curta:
   ./bin/llm-cli -y
   ```

3. **No arquivo `.env`:**
   ```env
   YOLO_MODE=true
   ```

---

## 🕹️ 2. Catálogo Completo de Comandos Slash

### 🤖 A. Modelos, Conectividade e Arquitetura

| Comando | Sintaxe | Descrição |
| :--- | :--- | :--- |
| **`/model`** | `/model`<br>`/model <nome_ou_numero>` | Abre o menu interativo com tabela de modelos ou troca diretamente o modelo ativo (ex: `/model llamacpp/default`, `/model gemini/gemini-2.5-flash`). |
| **`/models`** | `/models` | Exibe a tabela com o status de conectividade (ONLINE / OFFLINE / CONFIGURADO) de todos os provedores. |
| **`/architect`** | `/architect [modelo\|off]` | Alterna o Modo Arquiteto. Um modelo planeja a arquitetura da solução e outro aplica as alterações no código. |
| **`/scan`** | `/scan <ip_ou_host>` | Escaneia portas de servidores de LLM em um IP e lista os modelos disponíveis. |
| **`/host`** | `/host <ip_ou_host>` | Conecta ao IP remoto, atualiza os endpoints locais e seleciona o modelo disponível. |
| **`/mcp`** | `/mcp` | Lista os servidores MCP configurados e as ferramentas dinâmicas ativas. |
| **`/lang`** | `/lang [codigo]` | Exibe ou altera o idioma (`pt`, `en`, `es`, `de`, `fr`, `zh`, `ru`, `hi`, `auto`). |

---

### 📂 B. Contexto, Código e Pesquisa

| Comando | Sintaxe | Descrição |
| :--- | :--- | :--- |
| **`/add`** | `/add <caminho>` | Adiciona um arquivo ou pasta inteira ao contexto da IA (com suporte a `Tab` para autocomplete). |
| **`/drop`** | `/drop <caminho>` | Remove um arquivo do contexto da IA. |
| **`/files`** | `/files` | Lista todos os arquivos atualmente anexados ao contexto. |
| **`/index`** | `/index` | Varre o projeto e constrói o índice AST/BM25 offline para busca semântica. |
| **`/search`** | `/search <termo>` | Executa busca semântica/RAG no código indexado e exibe snippets formatados. |
| **`/web`** | `/web <pesquisa>` | Realiza busca na internet via DuckDuckGo ou Tavily API. |

---

### 🛠️ C. Git, Segurança e Qualidade de Código

| Comando | Sintaxe | Descrição |
| :--- | :--- | :--- |
| **`/diff`** | `/diff` | Exibe as alterações Git não commitadas com syntax highlighting colorido. |
| **`/commit`** | `/commit [mensagem]` | Analisa o git diff e gera mensagem de commit semântica com IA ou cria commit com a mensagem fornecida. |
| **`/review`** | `/review` | Executa Code Review das alterações Git pendentes avaliando bugs, segurança e performance. |
| **`/undo`** | `/undo` | Reverte o último checkpoint / modificação realizada pela IA. |
| **`/test`** | `/test [argumentos]` | Executa os testes unitários (`pytest`) e oferece correção automática via IA se houver falhas. |
| **`/gentest`** | `/gentest <arquivo>` | Gera uma suíte completa de testes unitários com pytest para o arquivo especificado. |
| **`/run`** | `/run <comando>` | Executa um comando no terminal a partir da raiz do workspace. |

---

### 📋 D. Planejamento, Tarefas e Exportação

| Comando | Sintaxe | Descrição |
| :--- | :--- | :--- |
| **`/plan`** | `/plan <objetivo>` | Cria um plano técnico passo a passo e popula automaticamente o checklist `/todo`. |
| **`/todo`** | `/todo`<br>`/todo add <tarefa>`<br>`/todo check <id>`<br>`/todo clear` | Visualiza e gerencia o checklist interativo de tarefas da sessão. |
| **`/export`** | `/export`<br>`/export md [caminho]`<br>`/export html [caminho]` | Exporta a sessão completa em Markdown (`.md`) ou HTML interativo estilizado (`.html`). |

---

### ⚙️ E. Sessão, Parâmetros e Histórico

| Comando | Sintaxe | Descrição |
| :--- | :--- | :--- |
| **`/paste`** | `/paste` | Inicia o modo multilinha para colar grandes blocos de texto ou código (`:done` para enviar, `:cancel` para abortar). |
| **`/compact`** | `/compact` | Compacta o histórico da conversa gerando um resumo consolidado de contexto. |
| **`/temp`** | `/temp [0.0 - 2.0]` | Exibe ou altera a temperatura do modelo ativo (preferência salva por LLM). |
| **`/system`** | `/system [prompt\|reset]` | Exibe, altera ou redefine o System Prompt da sessão. |
| **`/clear`** | `/clear` | Limpa o histórico de mensagens mantendo os arquivos no contexto. |
| **`/reset`** | `/reset`<br>`/reset prefs`<br>`/reset all` | Limpa sessão e contexto, redefine preferências do usuário ou ambos. |
| **`/tokens`** | `/tokens` | Exibe estimativa de tokens do contexto atual e total acumulado na sessão. |
| **`/help`** | `/help` | Exibe o menu com o resumo de todos os comandos. |
| **`/exit`** | `/exit` ou `/quit` | Encerra a aplicação de forma limpa. |

---

## ⌨️ 3. Atalhos de Teclado no Terminal

- **`Tab`**: Auto-completa nomes de comandos (ex: `/mo` -> `/model`) e caminhos de arquivos da árvore do projeto.
- **`Enter`**: Envia o comando ou prompt para a IA.
- **`Ctrl + C`**: Cancela o prompt atual ou interrompe a geração em andamento.
- **`Ctrl + D`**: Encerra a aplicação de forma limpa.
- **Setas `Cima` / `Baixo`**: Navega pelo histórico de prompts digitados (persistido em `~/.llmcli_history`).

