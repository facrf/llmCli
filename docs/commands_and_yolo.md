# ⚡ Comandos Slash e Modo YOLO

O **llmCli** oferece comandos interativos no terminal para controle do contexto, ferramentas e fluxo de execução.

---

## ⚡ 1. O que é o Modo YOLO (`/yolo`)?

O modo **YOLO** (*You Only Live Once* / Full Autonomous Access) foi desenvolvido para máxima velocidade e produtividade:

### Comparativo de Modos

| Recurso | Modo Normal (`🛡️ YOLO: OFF`) | Modo YOLO (`⚡ YOLO: ON`) |
| :--- | :--- | :--- |
| **Leitura de arquivos e buscas** | Automática | Automática |
| **Edição e gravação de arquivos** | Pede confirmação (`[s]im / [N]ão / [y]olo / [c]ancelar`) | **Executa automaticamente** |
| **Comandos de terminal (`run_command`)** | Pede confirmação prévia | **Executa automaticamente** |
| **Git Checkpoints** | Cria checkpoints antes de cada alteração | **Cria checkpoints antes de cada alteração** |
| **Reversão com `/undo`** | Disponível | **Totalmente disponível** |

### Como Ativar / Desativar

1. **Dentro da sessão interativa:**
   Digite simplesmente:
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

## 🕹️ 2. Tabela Completa de Comandos Slash

| Comando | Sintaxe / Exemplo | Descrição |
| :--- | :--- | :--- |
| **`/yolo`** | `/yolo` | Alterna o modo autônomo total (on/off). |
| **`/model`** | `/model llamacpp/default`<br>`/model gemini/gemini-2.5-flash` | Troca o modelo de LLM ativo em tempo real. |
| **`/models`** | `/models` | Lista status de saúde de todos os provedores locais e em nuvem. |
| **`/add`** | `/add src/core/agent.py`<br>`/add src/tools/` | Adiciona um arquivo ou pasta inteira ao contexto ativo. Suporta `Tab` para autocomplete. |
| **`/drop`** | `/drop src/core/agent.py` | Remove um arquivo do contexto ativo. |
| **`/files`** | `/files` | Lista todos os arquivos atualmente anexados ao contexto. |
| **`/diff`** | `/diff` | Exibe as alterações Git pendentes com syntax highlighting colorido. |
| **`/undo`** | `/undo` | Reverte o último checkpoint / modificação realizada pela IA. |
| **`/run`** | `/run pytest tests/` | Executa um comando de terminal no workspace e exibe a saída. |
| **`/clear`** | `/clear` | Limpa o histórico de mensagens mantendo os arquivos carregados. |
| **`/reset`** | `/reset` | Limpa tanto o histórico quanto os arquivos carregados no contexto. |
| **`/tokens`** | `/tokens` | Mostra estimativa de caracteres e tokens do contexto atual. |
| **`/help`** | `/help` | Exibe o menu de ajuda com todos os comandos. |
| **`/exit`** | `/exit` ou `/quit` | Encerra a execução do assistente. |

---

## ⌨️ 3. Atalhos de Teclado no Terminal

- **`Tab`**: Auto-completa nomes de comandos (ex: `/mo` -> `/model`) e caminhos de arquivos da árvore do projeto.
- **`Enter`**: Envia o comando ou prompt para a IA.
- **`Ctrl + C`**: Cancela o prompt atual ou interrompe a geração em andamento.
- **`Ctrl + D`**: Encerra a aplicação de forma limpa.
- **Setas `Cima` / `Baixo`**: Navega pelo histórico de prompts digitados.
